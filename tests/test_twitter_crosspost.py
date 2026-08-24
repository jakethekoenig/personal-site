import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOCIAL_SCRIPTS = Path(__file__).parents[1] / "scripts" / "social"
sys.path.insert(0, str(SOCIAL_SCRIPTS))

import sync_bluesky


ACTOR = "ja3k.bsky.social"
DID = "did:plc:author"


def post(rkey, text, reply=None):
    uri = f"at://{DID}/app.bsky.feed.post/{rkey}"
    record = {
        "$type": "app.bsky.feed.post",
        "createdAt": "2026-08-24T12:00:00.000Z",
        "text": text,
    }
    if reply:
        record["reply"] = {
            "parent": {"uri": reply, "cid": "parent-cid"},
            "root": {"uri": reply, "cid": "root-cid"},
        }
    return {
        "uri": uri,
        "cid": f"cid-{rkey}",
        "author": {"did": DID, "handle": ACTOR},
        "record": record,
        "indexedAt": record["createdAt"],
    }


class FakeMediaApi:
    def __init__(self):
        self.uploads = []
        self.metadata = []

    def media_upload(self, filename, **kwargs):
        self.uploads.append((filename, kwargs))
        return SimpleNamespace(media_id_string=f"media-{len(self.uploads)}")

    def create_media_metadata(self, media_id, alt_text):
        self.metadata.append((media_id, alt_text))


class FakePostingClient:
    def __init__(self, ids, fail_on_call=None):
        self.ids = iter(ids)
        self.fail_on_call = fail_on_call
        self.calls = []

    def create_tweet(
        self,
        *,
        text=None,
        in_reply_to_tweet_id=None,
        media_ids=None,
    ):
        self.calls.append(
            {
                "text": text,
                "in_reply_to_tweet_id": in_reply_to_tweet_id,
                "media_ids": media_ids,
            }
        )
        if self.fail_on_call == len(self.calls):
            raise RuntimeError("temporary X failure")
        return SimpleNamespace(data={"id": next(self.ids)})


class FakeBlueskyClient:
    def download_media(self, actor_did, spec):
        raise AssertionError("No media was expected")

    def get_post_thread(self, root_uri):
        return {"thread": {"post": self.root, "replies": []}}


class TwitterCrosspostTest(unittest.TestCase):
    def test_posts_media_and_replies_with_tweepy_keyword_arguments(self):
        root = post("root", "Root")
        reply = post("reply", "Reply", reply=root["uri"])
        media_api = FakeMediaApi()
        posting_client = FakePostingClient(["100", "101"])

        with tempfile.TemporaryDirectory() as temporary_directory:
            media_dir = Path(temporary_directory)
            (media_dir / "photo.jpg").write_bytes(b"photo")
            media_by_post = {
                root["uri"]: [
                    {
                        "url": "/asset/bluesky/photo.jpg",
                        "alt": "A diagram",
                    }
                ],
                reply["uri"]: [],
            }
            with (
                patch.object(
                    sync_bluesky,
                    "twitter_clients",
                    return_value=(media_api, posting_client),
                ),
                patch.object(sync_bluesky.time, "sleep"),
            ):
                crossposts, complete = sync_bluesky.crosspost_to_twitter(
                    [root, reply],
                    media_by_post,
                    media_dir,
                    "ja3k_",
                )

        self.assertTrue(complete)
        self.assertEqual(
            posting_client.calls,
            [
                {
                    "text": "Root",
                    "in_reply_to_tweet_id": None,
                    "media_ids": ["media-1"],
                },
                {
                    "text": "Reply",
                    "in_reply_to_tweet_id": "100",
                    "media_ids": None,
                },
            ],
        )
        self.assertEqual(media_api.metadata, [("media-1", "A diagram")])
        self.assertEqual([item["tweet_id"] for item in crossposts], ["100", "101"])

    def test_retry_resumes_after_the_successful_prefix(self):
        root = post("root", "Root")
        reply = post("reply", "Reply", reply=root["uri"])
        first_client = FakePostingClient(["100"], fail_on_call=2)

        with (
            patch.object(
                sync_bluesky,
                "twitter_clients",
                return_value=(FakeMediaApi(), first_client),
            ),
            patch.object(sync_bluesky.time, "sleep"),
        ):
            crossposts, complete = sync_bluesky.crosspost_to_twitter(
                [root, reply],
                {root["uri"]: [], reply["uri"]: []},
                Path("."),
                "ja3k_",
            )

        self.assertFalse(complete)
        self.assertEqual([item["tweet_id"] for item in crossposts], ["100"])

        retry_client = FakePostingClient(["101"])
        with (
            patch.object(
                sync_bluesky,
                "twitter_clients",
                return_value=(FakeMediaApi(), retry_client),
            ),
            patch.object(sync_bluesky.time, "sleep"),
        ):
            crossposts, complete = sync_bluesky.crosspost_to_twitter(
                [root, reply],
                {root["uri"]: [], reply["uri"]: []},
                Path("."),
                "ja3k_",
                existing_crossposts=crossposts,
            )

        self.assertTrue(complete)
        self.assertEqual(len(retry_client.calls), 1)
        self.assertEqual(retry_client.calls[0]["in_reply_to_tweet_id"], "100")
        self.assertEqual([item["tweet_id"] for item in crossposts], ["100", "101"])

    def test_enabled_crossposting_rejects_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            sync_bluesky._twitter_clients = None
            with self.assertRaisesRegex(RuntimeError, "TWITTER_API_KEY"):
                sync_bluesky.twitter_clients()

    def test_bluesky_only_record_has_no_tweet_url(self):
        root = post("root", "Root")
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            with patch.dict(os.environ, {}, clear=True):
                path, complete = sync_bluesky.save_thread(
                    repo_root,
                    FakeBlueskyClient(),
                    ACTOR,
                    DID,
                    [root],
                )
            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertTrue(complete)
        self.assertNotIn("tweet_url", data)
        self.assertEqual(
            data["bluesky_url"],
            "https://bsky.app/profile/ja3k.bsky.social/post/root",
        )

    def test_incomplete_crosspost_is_saved_without_advancing_checkpoint(self):
        root = post("root", "Root")
        client = FakeBlueskyClient()
        client.root = root

        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            state_path = repo_root / ".github" / "bluesky-sync-state.json"
            state_path.parent.mkdir(parents=True)
            initial_state = {
                "actor": ACTOR,
                "actor_did": DID,
                "last_seen_uri": "at://old",
                "last_seen_indexed_at": "2026-08-23T12:00:00.000Z",
            }
            state_path.write_text(json.dumps(initial_state), encoding="utf-8")
            scan = sync_bluesky.FeedScan(
                items=[{"post": root}],
                newest_uri=root["uri"],
                newest_indexed_at=root["indexedAt"],
            )

            with (
                patch.object(sync_bluesky, "scan_feed", return_value=scan),
                patch.object(
                    sync_bluesky,
                    "twitter_crossposting_enabled",
                    return_value=True,
                ),
                patch.object(
                    sync_bluesky,
                    "crosspost_to_twitter",
                    return_value=([], False),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "checkpoint was not advanced"):
                    sync_bluesky.sync(repo_root, client, ACTOR, state_path)

            self.assertEqual(
                json.loads(state_path.read_text(encoding="utf-8")),
                initial_state,
            )
            data = json.loads(
                (repo_root / "data" / "short" / "root.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertTrue(data["twitter_crosspost_pending"])
        self.assertNotIn("tweet_url", data)


if __name__ == "__main__":
    unittest.main()
