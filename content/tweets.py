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
    data_dir = Path("data") / "tweets"
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
.tweet { padding: 6px 0; }
.tweet_meta { font-size: 0.9em; color: #666; margin-top: 4px; }
.tweet_media img { max-width: 100%; height: auto; display: block; margin: 6px 0; }
</style>
"""
    return styles + "\n".join(parts)
