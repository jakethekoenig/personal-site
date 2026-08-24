import sys
import unittest
from pathlib import Path


BUILD_SCRIPTS = Path(__file__).parents[1] / "scripts" / "build"
sys.path.insert(0, str(BUILD_SCRIPTS))

from shortform_render import source_links_html


class ShortformSourceLinksTest(unittest.TestCase):
    def test_platform_fields_render_independently(self):
        bluesky_url = "https://bsky.app/profile/example/post/123"
        twitter_url = "https://x.com/example/status/456"

        bluesky_only = source_links_html({"bluesky_url": bluesky_url})
        self.assertIn(bluesky_url, bluesky_only)
        self.assertIn("tweet-bluesky-link", bluesky_only)
        self.assertNotIn("tweet-twitter-link", bluesky_only)

        both = source_links_html(
            {"bluesky_url": bluesky_url, "tweet_url": twitter_url}
        )
        self.assertIn(bluesky_url, both)
        self.assertIn(twitter_url, both)
        self.assertIn("tweet-bluesky-link", both)
        self.assertIn("tweet-twitter-link", both)


if __name__ == "__main__":
    unittest.main()
