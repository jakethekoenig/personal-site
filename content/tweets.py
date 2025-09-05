import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Renders a single tweet block
def render_tweet(t: Dict[str, Any]) -> str:
    content_html = ""
    for para in t["content"].split("\n"):
        if para.strip():
            content_html += "<p>" + escape_html(para) + "</p>"
    link = t.get("link", "#")
    ts = t.get("timestamp")
    pretty = ts
    try:
        pretty = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%b %d, %Y %H:%M:%S %Z")
    except Exception:
        pass

    media_html = ""
    for m in t.get("media", []):
        # Heuristic: render images with img tag, others as links
        if any(m.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            media_html += f"<div class='tweet_media'><img src='{m}' loading='lazy'></div>"
        else:
            media_html += f"<div class='tweet_media'><a href='{m}'>{m}</a></div>"

    meta = f"<div class='tweet_meta'><a href='{link}' target='_blank' rel='noopener noreferrer'>{link}</a> · <span class='tweet_time'>{pretty}</span></div>"
    return f"<div class='tweet'>{content_html}{media_html}{meta}</div>"

def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def load_all_tweets(data_dir: Path) -> List[Dict[str, Any]]:
    tweets: List[Dict[str, Any]] = []
    if not data_dir.exists():
        return tweets
    for p in data_dir.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                t = json.load(f)
                tweets.append(t)
        except Exception:
            continue
    # Sort newest first by timestamp if present
    def key(t):
        ts = t.get("timestamp", "")
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return datetime.min
    tweets.sort(key=key, reverse=True)
    return tweets

def generate(data, index):
    # Load tweet JSONs written by scripts/process_twitter_archive.py
    data_dir = Path("data") / "tweets"
    tweets = load_all_tweets(data_dir)
    # Note: With very large numbers of tweets, this page could be very large.
    # This is intentionally a single static page per user request.
    parts = []
    parts.append("<div class='tweets'>")
    for t in tweets:
        parts.append(render_tweet(t))
    parts.append("</div>")
    # Minimal inline styles for readability; can be moved to a CSS file if desired
    styles = """
<style>
.tweets { max-width: 900px; }
.tweet { padding: 10px 0; border-bottom: 1px solid #ddd; }
.tweet_meta { font-size: 0.9em; color: #666; margin-top: 4px; }
.tweet_media img { max-width: 100%; height: auto; display: block; margin: 6px 0; }
</style>
"""
    return styles + "\n".join(parts)
