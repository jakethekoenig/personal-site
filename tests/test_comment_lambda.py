import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


COMMENT_BACKEND = Path(__file__).parents[1] / "backend" / "catchcomments"
sys.path.insert(0, str(COMMENT_BACKEND))
sys.modules.setdefault("boto3", types.SimpleNamespace(client=lambda *args, **kwargs: MagicMock()))

import lambda_function


class CommentNotificationTest(unittest.TestCase):
    def test_commented_page_url(self):
        self.assertEqual(
            lambda_function.commented_page_url("comments/blog/zeroutils.html"),
            "https://ja3k.com/blog/zeroutils",
        )
        self.assertEqual(
            lambda_function.commented_page_url("comments/.html"),
            "https://ja3k.com/",
        )

    def test_notification_contains_commented_page(self):
        event = {
            "text": "Great post!",
            "author": "Reader",
            "url": "comments/blog/zeroutils.html",
        }

        with patch.object(lambda_function, "send_email") as send_email:
            result = lambda_function.handle_addcomment(event)

        self.assertEqual(result["statusCode"], 200)
        body, subject = send_email.call_args.args
        self.assertEqual(subject, "New Comment on ja3k.com")
        self.assertIn("Reader wrote:\n\nGreat post!", body)
        self.assertIn("Page: https://ja3k.com/blog/zeroutils", body)


if __name__ == "__main__":
    unittest.main()
