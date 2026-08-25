#!/usr/bin/env python3
"""Mirror new Bluesky posts into the site's short-form post format."""

import argparse
import html
import json
import mimetypes
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


DEFAULT_ACTOR = "ja3k.bsky.social"
DEFAULT_API_URL = "https://public.api.bsky.app"
DEFAULT_STATE_FILE = ".github/bluesky-sync-state.json"
AUTHOR_FEED_ENDPOINT = "app.bsky.feed.getAuthorFeed"
POST_THREAD_ENDPOINT = "app.bsky.feed.getPostThread"
MAX_FEED_PAGES = 20
TWITTER_CHARACTER_LIMIT = 280


def at_uri_did(uri):
    parts = uri.split("/")
    return parts[2] if len(parts) > 2 and parts[0] == "at:" else ""


def at_uri_rkey(uri):
    return uri.rstrip("/").rsplit("/", 1)[-1]


def bluesky_post_url(handle, uri):
    return f"https://bsky.app/profile/{handle}/post/{at_uri_rkey(uri)}"


def parse_datetime(value):
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.min


def display_text(text):
    return " ".join(text.split()).strip()


def shortened(text, length, fallback="Bluesky post"):
    text = display_text(text) or fallback
    return text[: length - 3] + "..." if len(text) > length else text


def post_record(post):
    record = post.get("record", {})
    return record if isinstance(record, dict) else {}


def post_created_at(post):
    record = post_record(post)
    return record.get("createdAt") or post.get("indexedAt", "")


def post_reply(post):
    reply = post_record(post).get("reply")
    return reply if isinstance(reply, dict) else None


def root_uri_for_post(post):
    reply = post_reply(post)
    if reply:
        root = reply.get("root", {})
        if isinstance(root, dict) and root.get("uri"):
            return root["uri"]
    return post.get("uri", "")


def is_site_post(post, actor_did):
    """Include roots and replies directly chained through the author's own posts."""
    author_did = post.get("author", {}).get("did")
    if author_did != actor_did:
        return False

    reply = post_reply(post)
    if not reply:
        return True

    parent_uri = reply.get("parent", {}).get("uri", "")
    root_uri = reply.get("root", {}).get("uri", "")
    return at_uri_did(parent_uri) == actor_did and at_uri_did(root_uri) == actor_did


def link_for_facet(feature):
    feature_type = feature.get("$type", "")
    if feature_type.endswith("#link"):
        return feature.get("uri")
    if feature_type.endswith("#mention") and feature.get("did"):
        return f"https://bsky.app/profile/{feature['did']}"
    if feature_type.endswith("#tag") and feature.get("tag"):
        return f"https://bsky.app/hashtag/{quote(feature['tag'])}"
    return None


def rich_text_html(record):
    """Render Bluesky UTF-8 byte-indexed facets without trusting post HTML."""
    text = record.get("text", "")
    text_bytes = text.encode("utf-8")
    ranges = []

    for facet in record.get("facets", []):
        index = facet.get("index", {})
        start = index.get("byteStart")
        end = index.get("byteEnd")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        if start < 0 or end <= start or end > len(text_bytes):
            continue
        url = next(
            (link_for_facet(feature) for feature in facet.get("features", []) if link_for_facet(feature)),
            None,
        )
        if url:
            ranges.append((start, end, url))

    ranges.sort()
    rendered = []
    position = 0
    for start, end, url in ranges:
        if start < position:
            continue
        rendered.append(html.escape(text_bytes[position:start].decode("utf-8")))
        label = html.escape(text_bytes[start:end].decode("utf-8"))
        rendered.append(
            f'<a href="{html.escape(url, quote=True)}" target="_blank">{label}</a>'
        )
        position = end
    rendered.append(html.escape(text_bytes[position:].decode("utf-8")))
    return "".join(rendered)


def text_as_paragraphs(record):
    rendered = rich_text_html(record)
    if not rendered:
        return ""
    paragraphs = rendered.split("\n\n")
    return "\n".join(f"<p>{paragraph.replace(chr(10), '<br>')}</p>" for paragraph in paragraphs)


def embedded_record_view(embed):
    embed_type = embed.get("$type", "")
    if embed_type.endswith("recordWithMedia#view"):
        return embed.get("record", {})
    if embed_type.endswith("record#view"):
        return embed
    return {}


def quoted_post_uri(post):
    embed = post.get("embed", {})
    record_view = embedded_record_view(embed)
    record = record_view.get("record", {}) if isinstance(record_view, dict) else {}
    return record.get("uri") if isinstance(record, dict) else None


def media_record_embed(post):
    embed = post_record(post).get("embed", {})
    if not isinstance(embed, dict):
        return {}
    if embed.get("$type", "").endswith("recordWithMedia"):
        media = embed.get("media", {})
        return media if isinstance(media, dict) else {}
    return embed


def media_view_embed(post):
    embed = post.get("embed", {})
    if not isinstance(embed, dict):
        return {}
    if embed.get("$type", "").endswith("recordWithMedia#view"):
        media = embed.get("media", {})
        return media if isinstance(media, dict) else {}
    return embed


def blob_cid(blob):
    reference = blob.get("ref", {}) if isinstance(blob, dict) else {}
    return reference.get("$link") if isinstance(reference, dict) else None


def extract_media_specs(post):
    """Return downloadable attached images and video, excluding link-card thumbnails."""
    specs = []
    record_embed = media_record_embed(post)
    view_embed = media_view_embed(post)
    record_type = record_embed.get("$type", "")
    view_type = view_embed.get("$type", "")

    if record_type.endswith("images") or view_type.endswith("images#view"):
        record_images = record_embed.get("images", [])
        view_images = view_embed.get("images", [])
        count = max(len(record_images), len(view_images))
        for index in range(count):
            record_image = record_images[index] if index < len(record_images) else {}
            view_image = view_images[index] if index < len(view_images) else {}
            blob = record_image.get("image", {})
            specs.append(
                {
                    "type": "photo",
                    "alt": view_image.get("alt", record_image.get("alt", "")),
                    "download_url": view_image.get("fullsize") or view_image.get("thumb"),
                    "blob_cid": blob_cid(blob),
                    "mime_type": blob.get("mimeType", "image/jpeg"),
                }
            )

    if record_type.endswith("video") or view_type.endswith("video#view"):
        video_blob = record_embed.get("video", {})
        specs.append(
            {
                "type": "video",
                "alt": view_embed.get("alt", record_embed.get("alt", "")),
                "download_url": None,
                "blob_cid": blob_cid(video_blob),
                "mime_type": video_blob.get("mimeType", "video/mp4"),
                "thumbnail": view_embed.get("thumbnail"),
            }
        )

    return [spec for spec in specs if spec.get("download_url") or spec.get("blob_cid")]


def extension_for_content_type(content_type, fallback_type):
    content_type = (content_type or fallback_type or "").split(";", 1)[0].lower()
    preferred = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
    }
    extension = preferred.get(content_type) or mimetypes.guess_extension(content_type) or ".bin"
    return extension if extension.replace(".", "").isalnum() else ".bin"


@dataclass
class FeedScan:
    items: list
    newest_uri: str
    newest_indexed_at: str


class BlueskyClient:
    def __init__(self, api_url=DEFAULT_API_URL, timeout=30, attempts=3):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.attempts = attempts
        self._pds_urls = {}

    def _open(self, url):
        request = Request(url, headers={"User-Agent": "ja3k.com-bluesky-sync/1.0"})
        for attempt in range(self.attempts):
            try:
                return urlopen(request, timeout=self.timeout)
            except HTTPError as error:
                if error.code not in {429, 500, 502, 503, 504} or attempt + 1 == self.attempts:
                    raise
            except URLError:
                if attempt + 1 == self.attempts:
                    raise
            time.sleep(2**attempt)
        raise RuntimeError(f"Unable to fetch {url}")

    def get_json(self, endpoint, **params):
        url = f"{self.api_url}/xrpc/{endpoint}?{urlencode(params)}"
        with self._open(url) as response:
            return json.load(response)

    def get_author_feed(self, actor, cursor=None):
        params = {
            "actor": actor,
            "filter": "posts_with_replies",
            "limit": 100,
        }
        if cursor:
            params["cursor"] = cursor
        return self.get_json(AUTHOR_FEED_ENDPOINT, **params)

    def get_post_thread(self, uri):
        return self.get_json(POST_THREAD_ENDPOINT, uri=uri, depth=100, parentHeight=0)

    def pds_url(self, did):
        if did in self._pds_urls:
            return self._pds_urls[did]
        if did.startswith("did:plc:"):
            document_url = f"https://plc.directory/{quote(did, safe=':')}"
        elif did.startswith("did:web:"):
            host_and_path = did.removeprefix("did:web:").split(":")
            host = host_and_path[0]
            path = "/".join(host_and_path[1:])
            document_url = f"https://{host}/{'%s/did.json' % path if path else '.well-known/did.json'}"
        else:
            raise ValueError(f"Unsupported DID method: {did}")
        with self._open(document_url) as response:
            document = json.load(response)
        services = document.get("service", [])
        service = next(
            (
                item
                for item in services
                if item.get("id") == "#atproto_pds"
                or item.get("type") == "AtprotoPersonalDataServer"
            ),
            None,
        )
        if not service or not service.get("serviceEndpoint"):
            raise ValueError(f"No AT Protocol PDS found for {did}")
        self._pds_urls[did] = service["serviceEndpoint"].rstrip("/")
        return self._pds_urls[did]

    def download_media(self, actor_did, spec):
        if spec.get("download_url"):
            url = spec["download_url"]
        else:
            params = urlencode({"did": actor_did, "cid": spec["blob_cid"]})
            url = f"{self.pds_url(actor_did)}/xrpc/com.atproto.sync.getBlob?{params}"
        with self._open(url) as response:
            return response.read(), response.headers.get_content_type()


def load_state(path):
    with path.open(encoding="utf-8") as state_file:
        return json.load(state_file)


# --- Twitter/X cross-posting -------------------------------------------------

_twitter_clients = None


def chunk_text(text, limit=TWITTER_CHARACTER_LIMIT - 10):
    """Split text into <=limit character chunks, preferring paragraph breaks."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > limit:
        window = remaining[: limit + 1]
        cut = window.rfind("\n\n")
        if cut < limit // 2:
            cut = window.rfind("\n")
        if cut < limit // 2:
            cut = window.rfind(" ")
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def text_with_full_links(record):
    """Expand Bluesky's shortened link labels to their complete facet URLs."""
    text = record.get("text", "")
    text_bytes = text.encode("utf-8")
    links = []
    for facet in record.get("facets", []):
        index = facet.get("index", {})
        start = index.get("byteStart")
        end = index.get("byteEnd")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        if start < 0 or end <= start or end > len(text_bytes):
            continue
        url = next(
            (
                feature.get("uri")
                for feature in facet.get("features", [])
                if feature.get("$type", "").endswith("#link")
                and feature.get("uri")
            ),
            None,
        )
        if url:
            links.append((start, end, url))

    if not links:
        return text

    links.sort()
    expanded = []
    position = 0
    for start, end, url in links:
        if start < position:
            continue
        expanded.append(text_bytes[position:start].decode("utf-8"))
        expanded.append(url)
        position = end
    expanded.append(text_bytes[position:].decode("utf-8"))
    return "".join(expanded)


def twitter_clients():
    """Return the authenticated v1.1 media API and v2 posting client."""
    global _twitter_clients
    if _twitter_clients is not None:
        return _twitter_clients
    credentials = {
        key: os.environ.get(f"TWITTER_{key}")
        for key in ("API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET")
    }
    missing = [key for key, value in credentials.items() if not value]
    if missing:
        names = ", ".join(f"TWITTER_{key}" for key in missing)
        raise RuntimeError(f"Twitter cross-posting is enabled but {names} is not set")
    try:
        import tweepy
    except ImportError as error:
        raise RuntimeError("Twitter cross-posting requires tweepy") from error
    auth = tweepy.OAuth1UserHandler(
        credentials["API_KEY"],
        credentials["API_SECRET"],
        credentials["ACCESS_TOKEN"],
        credentials["ACCESS_SECRET"],
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        consumer_key=credentials["API_KEY"],
        consumer_secret=credentials["API_SECRET"],
        access_token=credentials["ACCESS_TOKEN"],
        access_token_secret=credentials["ACCESS_SECRET"],
    )
    _twitter_clients = (api_v1, client_v2)
    return _twitter_clients


def upload_media(api_v1, path, alt=""):
    mime = mimetypes.guess_type(str(path))[0] or ""
    is_video = "video" in mime or path.suffix.lower() in {".mp4", ".webm", ".mov"}
    if is_video:
        media = api_v1.media_upload(
            str(path),
            chunked=True,
            media_category="tweet_video",
        )
    else:
        media = api_v1.media_upload(str(path))
    media_id = media.media_id_string
    if alt and not is_video:
        api_v1.create_media_metadata(media_id, alt[:1000])
    return media_id


def twitter_crossposting_enabled():
    """Allow local site-only imports while requiring X in the scheduled workflow."""
    return os.environ.get("TWITTER_CROSSPOST_ENABLED", "").lower() in {
        "1",
        "true",
        "yes",
    }


def is_twitter_post_url(url):
    hostname = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return hostname in {"twitter.com", "x.com"} and "/status/" in urlparse(url).path


def twitter_post_id(url):
    path_parts = urlparse(url).path.strip("/").split("/")
    try:
        return path_parts[path_parts.index("status") + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Cannot find an X post ID in {url}") from None


def crosspost_to_twitter(
    posts,
    post_links,
    media_by_post,
    media_dir,
    username,
    skipped_uris=None,
):
    """Mirror posts to X, using their public links as durable retry state."""
    post_links = [list(urls) for urls in post_links]
    skipped_uris = set(skipped_uris or [])
    previous_id = None

    try:
        api_v1, client_v2 = twitter_clients()
    except Exception as error:
        print(f"Twitter cross-posting deferred: {error}")
        return post_links, False

    for post_index, post in enumerate(posts):
        if post["uri"] in skipped_uris:
            continue
        existing_urls = [
            url for url in post_links[post_index] if is_twitter_post_url(url)
        ]
        for index, chunk in enumerate(chunk_text(text_with_full_links(post_record(post))) or [""]):
            if index < len(existing_urls):
                previous_id = twitter_post_id(existing_urls[index])
                continue

            try:
                payload = {}
                if chunk:
                    payload["text"] = chunk
                if previous_id:
                    payload["in_reply_to_tweet_id"] = previous_id
                if index == 0:
                    media_ids = []
                    for item in media_by_post.get(post["uri"], [])[:4]:
                        local_path = media_dir / Path(item["url"]).name
                        if local_path.exists():
                            media_ids.append(
                                upload_media(api_v1, local_path, item.get("alt", ""))
                            )
                    if media_ids:
                        payload["media_ids"] = media_ids
                response = client_v2.create_tweet(**payload)
                previous_id = str(response.data["id"])
            except Exception as error:
                successful_count = sum(
                    is_twitter_post_url(url)
                    for urls in post_links
                    for url in urls
                )
                print(
                    "Twitter cross-posting deferred after "
                    f"{successful_count} successful post(s): {error}"
                )
                return post_links, False
            post_links[post_index].append(
                f"https://x.com/{username}/status/{previous_id}"
            )
            time.sleep(2)

    twitter_urls = [
        url for urls in post_links for url in urls if is_twitter_post_url(url)
    ]
    print(f"Cross-posted to Twitter: {twitter_urls}")
    return post_links, True


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(value, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_path, path)


def scan_feed(client, actor, state):
    marker_uri = state.get("last_seen_uri")
    marker_time = parse_datetime(state.get("last_seen_indexed_at"))
    items = []
    cursor = None
    newest_uri = ""
    newest_indexed_at = ""

    for _ in range(MAX_FEED_PAGES):
        page = client.get_author_feed(actor, cursor)
        page_items = page.get("feed", [])
        if not page_items:
            break
        if not newest_uri:
            newest_post = page_items[0].get("post", {})
            newest_uri = newest_post.get("uri", "")
            newest_indexed_at = newest_post.get("indexedAt", "")

        reached_marker = False
        for item in page_items:
            post = item.get("post", {})
            if post.get("uri") == marker_uri:
                reached_marker = True
                break
            if marker_time != datetime.min and parse_datetime(post.get("indexedAt")) <= marker_time:
                reached_marker = True
                break
            items.append(item)

        if reached_marker:
            break
        cursor = page.get("cursor")
        if not cursor:
            break
    else:
        raise RuntimeError(
            f"Bluesky checkpoint was not found within {MAX_FEED_PAGES * 100} feed items"
        )

    return FeedScan(items=items, newest_uri=newest_uri, newest_indexed_at=newest_indexed_at)


def collect_own_thread(thread_data, actor_did):
    root_node = thread_data.get("thread", {})
    posts = []

    def visit(node):
        post = node.get("post", {}) if isinstance(node, dict) else {}
        if not post or post.get("author", {}).get("did") != actor_did:
            return
        if posts and not is_site_post(post, actor_did):
            return
        posts.append(post)
        current_uri = post.get("uri")
        for child in node.get("replies", []) or []:
            child_post = child.get("post", {}) if isinstance(child, dict) else {}
            reply = post_reply(child_post) or {}
            parent_uri = reply.get("parent", {}).get("uri")
            if parent_uri == current_uri and child_post.get("author", {}).get("did") == actor_did:
                visit(child)

    visit(root_node)
    posts.sort(key=lambda post: parse_datetime(post_created_at(post)))
    return posts


def quote_html(post, handle):
    uri = quoted_post_uri(post)
    if not uri:
        return ""
    url = bluesky_post_url(at_uri_did(uri), uri)
    return (
        '<p class="quoted-post"><a href="'
        + html.escape(url, quote=True)
        + '" target="_blank">Quoted Bluesky post</a></p>'
    )


def render_post(post, media, handle):
    parts = []
    text_html = text_as_paragraphs(post_record(post))
    if text_html:
        parts.append(text_html)
    quoted = quote_html(post, handle)
    if quoted:
        parts.append(quoted)
    for item in media:
        url = html.escape(item["url"], quote=True)
        alt = html.escape(item.get("alt") or "Bluesky media", quote=True)
        if item["type"] == "photo":
            parts.append(f'<img src="{url}" alt="{alt}">')
        elif item["type"] == "video":
            parts.append(
                f'<video controls preload="metadata" aria-label="{alt}"><source src="{url}"></video>'
            )
    return "\n\n".join(parts)


def existing_media_paths(data_path, repo_root):
    if not data_path.exists():
        return set()
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    paths = set()
    for item in data.get("media", []):
        url = item.get("url", "")
        if url.startswith("/asset/bluesky/"):
            paths.add(repo_root / "nongenerated" / url.lstrip("/"))
    return paths


def existing_bluesky_data_path(repo_root, root_uri, public_url):
    """Find a short-form record already associated with a Bluesky root."""
    data_dir = repo_root / "data" / "short"
    for path in data_dir.glob("*.json"):
        if path.name == "default.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("bluesky_uri") == root_uri:
            return path
        if any(public_url in urls for urls in data.get("posts", [])):
            return path
    return None


def save_thread(repo_root, client, actor, actor_did, posts):
    root = posts[0]
    root_uri = root["uri"]
    slug = at_uri_rkey(root_uri)
    public_root_url = bluesky_post_url(actor, root_uri)
    data_path = existing_bluesky_data_path(
        repo_root,
        root_uri,
        public_root_url,
    ) or (repo_root / "data" / "short" / f"{slug}.json")
    media_dir = repo_root / "nongenerated" / "asset" / "bluesky"
    media_dir.mkdir(parents=True, exist_ok=True)

    if data_path.exists():
        existing_data = json.loads(data_path.read_text(encoding="utf-8"))
        if existing_data.get("bluesky_uri") not in {None, root_uri}:
            raise RuntimeError(
                f"Cannot mirror {root_uri}: short-form URL {slug} is already in use"
            )
    else:
        existing_data = None

    site_slug = str((existing_data or {}).get("URL") or slug)
    content_reference = (existing_data or {}).get("Content") or f"short/{site_slug}.md"
    content_path = repo_root / "content" / content_reference

    media_by_post = {}
    all_media = []
    for post in posts:
        post_uri = post["uri"]
        media_rkey = at_uri_rkey(post_uri)
        post_media = []
        for index, spec in enumerate(extract_media_specs(post), 1):
            body, content_type = client.download_media(actor_did, spec)
            extension = extension_for_content_type(content_type, spec.get("mime_type"))
            filename = f"{media_rkey}_{index}{extension}"
            path = media_dir / filename
            if not path.exists() or path.read_bytes() != body:
                path.write_bytes(body)
            item = {
                "type": spec["type"],
                "url": f"/asset/bluesky/{filename}",
                "original_url": spec.get("download_url")
                or f"at://{actor_did}/blob/{spec.get('blob_cid')}",
                "alt": spec.get("alt", ""),
                "source_post_uri": post_uri,
            }
            post_media.append(item)
            all_media.append(item)
        media_by_post[post_uri] = post_media

    expected_media_paths = {
        repo_root / "nongenerated" / item["url"].lstrip("/") for item in all_media
    }
    for obsolete_path in existing_media_paths(data_path, repo_root) - expected_media_paths:
        obsolete_path.unlink(missing_ok=True)

    text_parts = [post_record(post).get("text", "") for post in posts]
    combined_text = "\n\n".join(text for text in text_parts if text)

    # Public links are both the site schema and the durable X retry state.
    existing_data = existing_data or {}
    existing_post_uris = existing_data.get("post_uris", [])
    existing_posts = existing_data.get("posts", [])
    links_by_uri = {
        uri: list(existing_posts[index])
        for index, uri in enumerate(existing_post_uris)
        if index < len(existing_posts)
    }
    if not links_by_uri and len(existing_posts) == len(posts):
        links_by_uri = {
            post["uri"]: list(existing_posts[index])
            for index, post in enumerate(posts)
        }
    post_links = []
    for post in posts:
        links = links_by_uri.get(post["uri"], [])
        bluesky_url = bluesky_post_url(actor, post["uri"])
        if bluesky_url not in links:
            links.insert(0, bluesky_url)
        post_links.append(links)

    skipped_twitter_uris = list(existing_data.get("twitter_skipped_post_uris", []))
    twitter_complete = not existing_data.get("twitter_crosspost_pending", False)
    if twitter_crossposting_enabled():
        post_links, twitter_complete = crosspost_to_twitter(
            posts,
            post_links,
            media_by_post,
            media_dir,
            os.environ.get("TWITTER_USERNAME", "ja3k_"),
            skipped_uris=skipped_twitter_uris,
        )

    is_thread = len(posts) > 1
    data = {
        "Title": (
            f"Thread: {shortened(text_parts[0], 80)}"
            if is_thread
            else shortened(text_parts[0], 100)
        ),
        "Author": "Jake Koenig",
        "URL": site_slug,
        "Template": "tweet.temp",
        "Date": parse_datetime(post_created_at(root)).strftime("%Y-%m-%d"),
        "Content": content_reference,
        "Summary": shortened(combined_text, 200),
        "Categories": ["shorts", "bluesky"] + (["threads"] if is_thread else []),
        "tweet_id": (existing_data or {}).get("tweet_id", site_slug),
        "posts": post_links,
        "original_date": post_created_at(root),
        "media": all_media,
        "is_thread": is_thread,
        "bluesky_uri": root_uri,
        "post_uris": [post["uri"] for post in posts],
    }
    for preserved_key in ("Hide", "quoted_tweet"):
        if preserved_key in existing_data:
            data[preserved_key] = existing_data[preserved_key]
    if is_thread:
        data["thread_length"] = len(posts)
    if skipped_twitter_uris:
        data["twitter_skipped_post_uris"] = skipped_twitter_uris
    if not twitter_complete:
        data["twitter_crosspost_pending"] = True

    if is_thread:
        sections = ["# Thread", ""]
        for index, post in enumerate(posts, 1):
            sections.extend(
                [
                    f"## Tweet {index}",
                    "",
                    render_post(post, media_by_post[post["uri"]], actor),
                    "",
                    "---",
                    "",
                ]
            )
        content = "\n".join(sections)
    else:
        content = render_post(root, media_by_post[root_uri], actor) + "\n"

    write_json(data_path, data)
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(content, encoding="utf-8")
    return data_path, twitter_complete


def sync(repo_root, client, actor, state_path):
    state = load_state(state_path)
    actor_did = state["actor_did"]
    scan = scan_feed(client, actor, state)
    eligible_posts = [
        item.get("post", {})
        for item in scan.items
        if is_site_post(item.get("post", {}), actor_did)
    ]
    if not eligible_posts:
        print(f"No new standalone posts or self-thread replies for @{actor}.")
        return 0

    root_uris = []
    for post in reversed(eligible_posts):
        root_uri = root_uri_for_post(post)
        if root_uri and root_uri not in root_uris:
            root_uris.append(root_uri)

    written = 0
    twitter_complete = True
    fallback_posts = {post.get("uri"): post for post in eligible_posts}
    for root_uri in root_uris:
        try:
            posts = collect_own_thread(client.get_post_thread(root_uri), actor_did)
        except (HTTPError, URLError, ValueError, KeyError) as error:
            print(f"Warning: could not hydrate {root_uri}: {error}")
            posts = [
                post
                for post in fallback_posts.values()
                if root_uri_for_post(post) == root_uri
            ]
            posts.sort(key=lambda post: parse_datetime(post_created_at(post)))
        if not posts or posts[0].get("uri") != root_uri:
            raise RuntimeError(f"Could not load Bluesky thread root {root_uri}")
        path, thread_twitter_complete = save_thread(
            repo_root,
            client,
            actor,
            actor_did,
            posts,
        )
        print(f"Updated {path.relative_to(repo_root)} with {len(posts)} post(s).")
        written += 1
        twitter_complete = twitter_complete and thread_twitter_complete

    if not twitter_complete:
        raise RuntimeError(
            "One or more X cross-posts are incomplete; Bluesky checkpoint was not advanced"
        )

    state["last_seen_uri"] = scan.newest_uri
    state["last_seen_indexed_at"] = scan.newest_indexed_at
    state["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    write_json(state_path, state)
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actor", default=DEFAULT_ACTOR)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    state_path = Path(args.state_file)
    if not state_path.is_absolute():
        state_path = repo_root / state_path
    count = sync(repo_root, BlueskyClient(), args.actor, state_path)
    print(f"Bluesky sync complete: {count} page(s) updated.")


if __name__ == "__main__":
    main()
