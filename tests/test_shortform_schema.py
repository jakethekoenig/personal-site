import json
import unittest
from pathlib import Path
from urllib.parse import urlparse


DATA_DIR = Path(__file__).parents[1] / "data" / "short"
LEGACY_FIELDS = {
    "bluesky_thread_urls",
    "bluesky_url",
    "source",
    "source_badge",
    "source_name",
    "thread_urls",
    "tweet_url",
    "twitter_crossposts",
    "twitter_post_uris",
    "twitter_posted",
    "twitter_urls",
}


class ShortformSchemaTest(unittest.TestCase):
    def test_every_record_uses_only_the_posts_url_schema(self):
        paths = sorted(DATA_DIR.glob("*.json"))
        self.assertGreater(len(paths), 1)

        for path in paths:
            if path.name == "default.json":
                continue
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(LEGACY_FIELDS.isdisjoint(data))
                self.assertIsInstance(data.get("posts"), list)
                self.assertTrue(data["posts"])
                for urls in data["posts"]:
                    self.assertIsInstance(urls, list)
                    self.assertTrue(urls)
                    for url in urls:
                        parsed = urlparse(url)
                        self.assertEqual(parsed.scheme, "https")
                        self.assertTrue(parsed.hostname)
                if data.get("is_thread"):
                    self.assertEqual(data.get("thread_length"), len(data["posts"]))


if __name__ == "__main__":
    unittest.main()
