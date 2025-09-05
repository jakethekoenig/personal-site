import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Renders a single tweet block
def render_tweet(t: Dict[str, Any]) -> str:
    link = t.get("link", "#")
    ts = t.get("timestamp")
    pretty = ts
    try:
        pretty = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%b %d, %Y %H:%M:%S %Z")
    except Exception:
        pass

    # Prepare text: remove trailing t.co media tokens if media present, and linkify remaining URLs
    raw = t.get("content", "")
    text_html = ""
    for para in raw.split("\n"):
        para = para.strip()
        if not para:
            continue
        # If media present, strip bare t.co tokens (common in exports)
        if t.get("media"):
            words = []
            for w in para.split():
                if w.startswith("https://t.co/"):
                    continue
                words.append(w)
            para = " ".join(words)
        text_html += "<p>" + linkify(escape_html(para)) + "</p>"

    # Media
    media_html = ""
    for m in t.get("media", []):
        lower = m.lower()
        if any(lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]):
            media_html += f"<div class='tweet_media'><img src='{m}' loading='lazy' referrerpolicy='no-referrer'></div>"
        else:
            media_html += f"<div class='tweet_media'><a href='{m}' target='_blank' rel='noopener noreferrer'>{m}</a></div>"

    # X icon link (inline SVG) + time
    x_icon = (
        f"<a class='tweet_x' href='{link}' target='_blank' rel='noopener noreferrer' aria-label='View on X'>"
        "<svg width='18' height='18' viewBox='0 0 24 24' fill='currentColor' xmlns='http://www.w3.org/2000/svg' "
        "aria-hidden='true'><path d='M18.244 2H21l-6.56 7.49L22 22h-6.91l-4.51-5.62L4.29 22H2l7.02-8.01L2 2h6.91l4.22 5.26L18.244 2zm-2.43 18h2.02L8.27 4H6.25l9.56 16z'/></svg>"
        "</a>"
    )
    meta = f"<div class='tweet_meta'>{x_icon}<span class='tweet_time'>{pretty}</span></div>"

    # Layout with avatar
    avatar = "<img class='tweet_avatar' src='/asset/pfp.png' alt='avatar'>"
    body = f"<div class='tweet_body'>{text_html}{media_html}{meta}</div>"
    return f"<div class='tweet'>{avatar}{body}</div>"

def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )

def linkify(s: str) -> str:
    # very small linkifier for http(s) urls
    import re
    url_re = re.compile(r"(https?://[^\s<>'\"]+)")
    return url_re.sub(lambda m: f"<a href='{m.group(1)}' target='_blank' rel='noopener noreferrer'>{m.group(1)}</a>", s)

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
    return tweets

def parse_ts(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.min

def group_threads(tweets: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Group tweets by 'thread_root'. Singletons (no replies) will be size 1.
    Order groups by newest item in the group (desc). Within a group, order ascending by timestamp.
    """
    from collections import defaultdict
    groups = defaultdict(list)
    for t in tweets:
        root = t.get("thread_root") or t.get("id")
        groups[str(root)].append(t)
    # Order each group
    ordered_groups: List[List[Dict[str, Any]]] = []
    for root, items in groups.items():
        items.sort(key=lambda x: parse_ts(x.get("timestamp", "")))
        ordered_groups.append(items)
    # Sort groups by newest timestamp in group (desc)
    ordered_groups.sort(key=lambda grp: parse_ts(grp[-1].get("timestamp", "")), reverse=True)
    return ordered_groups

def render_thread(items: List[Dict[str, Any]]) -> str:
    if len(items) == 1:
        return render_tweet(items[0])
    inner = []
    inner.append("<div class='thread'>")
    for t in items:
        inner.append(render_tweet(t))
    inner.append("</div>")
    return "\n".join(inner)

def generate(data, index):
    # Load tweet JSONs written by scripts/process_twitter_archive.py
    data_dir = Path("data") / "tweets_data"
    tweets = load_all_tweets(data_dir)

    # Group into threads (self-replies only; processor already filtered)
    threads = group_threads(tweets)

    parts = []
    parts.append("<div class='tweets'>")
    for thread in threads:
        parts.append(render_thread(thread))
    parts.append("</div>")

    styles = """
<style>
.tweets { max-width: 900px; }
.thread { padding: 12px 0; border-bottom: 1px solid #ddd; }
.tweet {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin: 10px 0;
  background: #fff;
}
.tweet_avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}
.tweet_body p { margin: 6px 0; }
.tweet_meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  color: #666;
  margin-top: 6px;
}
.tweet_x { color: #666; text-decoration: none; display: inline-flex; }
.tweet_x:hover { color: #000; }
.tweet_media img { max-width: 100%; height: auto; display: block; margin: 6px 0; border-radius: 8px; }
</style>
"""
    return styles + "\n".join(parts)
