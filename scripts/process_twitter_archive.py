#!/usr/bin/env python3
"""
Process a Twitter/X data export into:
- Individual JSON files per tweet under an output data directory (default: data/tweets)
- Copies downloaded media into a site-relative assets directory (default: nongenerated/assets/crosspoast)
- Optionally downloads media from URLs if missing locally (--download)

Expected Twitter export shapes supported (placed under --archive-dir):
- data/tweets.js (legacy, window.YTD.tweets.part0 = [...])
- data/tweets/*.js (sharded parts)
- data/tweet.js (some exports)
- data/account.js (to discover screen_name) or data/profile.js
- data/tweet_media/ or data/tweets_media/ (for media files)

For each tweet authored by the account owner:
- content: full text
- link: https://x.com/&lt;screen_name&gt;/status/&lt;id&gt;
- timestamp: ISO 8601 in UTC
- media: list of relative asset paths copied under /assets/crosspoast (site path), with local source filename mapping
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from glob import glob
from pathlib import Path
from typing import Dict, Any, Iterable, List, Optional

try:
    import requests  # only used if --download is set
except Exception:
    requests = None  # lazy-check later


def _read_js_json(path: Path) -> Any:
    """
    Twitter exports often prefix files with 'window.YTD.... = ' followed by JSON.
    Strip up to the first '=' and parse the remainder.
    """
    text = path.read_text(encoding="utf-8")
    # Find first '[' or '{' to be robust
    m = re.search(r"[\[\{]", text)
    if not m:
        raise ValueError(f"Could not locate JSON start in {path}")
    payload = text[m.start():]
    return json.loads(payload)


def _iter_tweet_records(archive_dir: Path) -> Iterable[Dict[str, Any]]:
    """
    Yield raw tweet dicts (as in export), where record contains a 'tweet' key or is the tweet itself.
    """
    candidates = []
    # Multiple possible locations
    candidates += [archive_dir / "data" / "tweets.js"]
    candidates += list((archive_dir / "data" / "tweets").glob("*.js"))
    candidates += [archive_dir / "data" / "tweet.js"]
    found_any = False
    for p in candidates:
        if not p.exists():
            continue
        found_any = True
        data = _read_js_json(p)
        # Legacy format: list of {"tweet": {...}}
        if isinstance(data, list) and data and isinstance(data[0], dict):
            for item in data:
                if "tweet" in item:
                    yield item["tweet"]
                else:
                    # Some exports store the tweet object directly
                    yield item
        else:
            # Unexpected structure; best effort
            if isinstance(data, dict) and "tweets" in data and isinstance(data["tweets"], list):
                for item in data["tweets"]:
                    if "tweet" in item:
                        yield item["tweet"]
                    else:
                        yield item
            else:
                raise ValueError(f"Unrecognized tweets structure in {p}")
    if not found_any:
        raise FileNotFoundError("Could not find tweets data (looked for data/tweets.js, data/tweets/*.js, data/tweet.js)")


def _discover_screen_name(archive_dir: Path) -> Optional[str]:
    # Try data/account.js, data/profile.js, data/account-creation.js
    for name in ["account.js", "profile.js", "account-creation.js"]:
        p = archive_dir / "data" / name
        if p.exists():
            try:
                payload = _read_js_json(p)
                # payload can be list[{"account":{...}}] or list[{"profile":{...}}]
                if isinstance(payload, list) and payload:
                    obj = payload[0]
                    if "account" in obj and "username" in obj["account"]:
                        return obj["account"]["username"]
                    if "profile" in obj and "screenName" in obj["profile"]:
                        return obj["profile"]["screenName"]
                    # Some variants
                    for v in obj.values():
                        if isinstance(v, dict):
                            for k2 in ("username", "screenName"):
                                if k2 in v:
                                    return v[k2]
            except Exception:
                continue
    # Fallback: None -> require --screen-name
    return None


def _parse_timestamp(ts: str) -> datetime:
    """
    Tweets export 'created_at' as RFC 2822-ish, e.g., 'Mon Jan 01 12:34:56 +0000 2020'
    Convert to aware UTC datetime.
    """
    # Try standard Twitter format
    for fmt in [
        "%a %b %d %H:%M:%S %z %Y",
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO in some exports
        "%Y-%m-%dT%H:%M:%SZ",
    ]:
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    # Best-effort
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _copy_local_media_if_exists(media_src_dir_candidates: List[Path], fn: str, dst_dir: Path) -> Optional[Path]:
    """
    Try to locate the media file by filename within known media directories and copy it.
    Returns destination path if copied.
    """
    for base in media_src_dir_candidates:
        # Scan with glob to find the file anywhere under base
        for path in base.rglob(fn):
            rel_name = path.name
            dst_path = dst_dir / rel_name
            if not dst_path.exists():
                _ensure_dir(dst_dir)
                shutil.copy2(path, dst_path)
            return dst_path
    return None


def _download_media(url: str, dst_dir: Path) -> Optional[Path]:
    if requests is None:
        return None
    try:
        _ensure_dir(dst_dir)
        # Give files deterministic names from URL path
        name = url.split("?")[0].rstrip("/").split("/")[-1]
        if not name:
            name = "media"
        dst = dst_dir / name
        if dst.exists():
            return dst
        resp = requests.get(url, timeout=20)
        if resp.ok:
            with open(dst, "wb") as f:
                f.write(resp.content)
            return dst
    except Exception:
        return None
    return None


def _best_video_variant(media_obj: Dict[str, Any]) -> Optional[str]:
    # Choose highest bitrate mp4
    try:
        variants = media_obj.get("video_info", {}).get("variants", [])
        mp4s = [v for v in variants if v.get("content_type") == "video/mp4"]
        mp4s.sort(key=lambda v: v.get("bitrate", 0), reverse=True)
        if mp4s:
            return mp4s[0]["url"]
    except Exception:
        pass
    return None


def _discover_account_id(archive_dir: Path) -> Optional[str]:
    for name in ["account.js", "profile.js", "account-creation.js"]:
        p = archive_dir / "data" / name
        if p.exists():
            try:
                payload = _read_js_json(p)
                if isinstance(payload, list) and payload:
                    obj = payload[0]
                    if "account" in obj and "accountId" in obj["account"]:
                        return str(obj["account"]["accountId"])
                    if "profile" in obj and "userId" in obj["profile"]:
                        return str(obj["profile"]["userId"])
            except Exception:
                continue
    return None


def process_archive(
    archive_dir: Path,
    out_data_dir: Path,
    out_media_dir: Path,
    screen_name: Optional[str],
    download_missing: bool,
) -> int:
    if not screen_name:
        screen_name = _discover_screen_name(archive_dir)
    if not screen_name:
        raise SystemExit("Could not determine screen name. Supply --screen-name USERNAME.")

    _ensure_dir(out_data_dir)
    _ensure_dir(out_media_dir)

    media_src_dir_candidates = [
        archive_dir / "data" / "tweets_media",
        archive_dir / "data" / "tweet_media",
        archive_dir / "data" / "media",
        archive_dir,  # last resort
    ]

    # Load all tweets first to support filtering and threading
    raw: List[Dict[str, Any]] = list(_iter_tweet_records(archive_dir))
    by_id: Dict[str, Dict[str, Any]] = {}
    for t in raw:
        tid = t.get("id_str") or t.get("id")
        if tid:
            by_id[str(tid)] = t

    own_user_id = _discover_account_id(archive_dir)
    if not own_user_id:
        # Fallback: infer from one of the tweets
        for t in raw:
            uid = t.get("user_id_str") or (t.get("user") or {}).get("id_str")
            if uid:
                own_user_id = str(uid)
                break

    def is_self_reply(t: Dict[str, Any]) -> bool:
        in_reply_to_uid = t.get("in_reply_to_user_id_str") or t.get("in_reply_to_user_id")
        return bool(in_reply_to_uid) and own_user_id and str(in_reply_to_uid) == own_user_id

    def thread_root_id(t: Dict[str, Any]) -> str:
        seen = set()
        current = t
        while True:
            tid = str(current.get("id_str") or current.get("id"))
            parent_id = current.get("in_reply_to_status_id_str") or current.get("in_reply_to_status_id")
            if not parent_id:
                return tid
            parent_id = str(parent_id)
            if parent_id in seen:
                return tid
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            if not parent:
                return tid
            # only follow chain if parent is authored by self
            parent_uid = parent.get("user_id_str") or (parent.get("user") or {}).get("id_str")
            if own_user_id and str(parent_uid) != own_user_id:
                return tid
            current = parent

    # Filter: keep top-level tweets and self-threads (replies where in_reply_to_user_id is self)
    filtered: List[Dict[str, Any]] = []
    for t in raw:
        is_reply = bool(t.get("in_reply_to_status_id_str") or t.get("in_reply_to_status_id"))
        if not is_reply or is_self_reply(t):
            filtered.append(t)

    # Write outputs
    count = 0
    for t in filtered:
        id_str = str(t.get("id_str") or t.get("id"))
        created_at = t.get("created_at") or t.get("createdAt") or t.get("time")
        if not id_str or not created_at:
            continue
        dt = _parse_timestamp(created_at)
        iso_ts = dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

        full_text = (
            t.get("full_text")
            or t.get("text")
            or t.get("fullText")
            or ""
        )

        # Entities and media
        entities = t.get("extended_entities") or t.get("entities") or {}
        media_list = entities.get("media", []) or []

        copied_assets: List[str] = []
        for m in media_list:
            media_url = m.get("media_url_https") or m.get("media_url") or ""
            typ = m.get("type")
            candidate_url = media_url
            if typ in ("video", "animated_gif"):
                best = _best_video_variant(m) or media_url
                candidate_url = best

            site_rel = None
            # Try local copy
            name_guess = None
            if candidate_url:
                name_guess = candidate_url.split("?")[0].rstrip("/").split("/")[-1]
            if name_guess:
                copied = _copy_local_media_if_exists(media_src_dir_candidates, name_guess, out_media_dir)
                if copied:
                    site_rel = "/assets/crosspoast/" + copied.name

            # Optionally download
            if not site_rel and download_missing and candidate_url:
                downloaded = _download_media(candidate_url, out_media_dir)
                if downloaded:
                    site_rel = "/assets/crosspoast/" + downloaded.name

            if site_rel:
                copied_assets.append(site_rel)

        in_reply_to = t.get("in_reply_to_status_id_str") or t.get("in_reply_to_status_id")
        root_id = thread_root_id(t)

        obj = {
            "id": id_str,
            "Title": f"Tweet {id_str}",
            "Template": "empty.temp",
            "Hide": True,
            "content": full_text,
            "link": f"https://x.com/{screen_name}/status/{id_str}",
            "timestamp": iso_ts,
            "thread_root": root_id,
        }
        if in_reply_to:
            obj["in_reply_to_status_id"] = str(in_reply_to)
        if copied_assets:
            obj["media"] = copied_assets

        out_path = out_data_dir / f"{id_str}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        count += 1

    return count


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Extract tweets from a Twitter/X archive to site JSON and assets.")
    p.add_argument("--archive-dir", required=True, help="Path to root of the Twitter data export")
    p.add_argument("--out-data-dir", default="data/tweets_data", help="Directory to write per-tweet JSON files")
    p.add_argument("--out-media-dir", default="nongenerated/assets/crosspoast", help="Directory to place media assets to be served at /assets/crosspoast")
    p.add_argument("--screen-name", help="Your Twitter/X @username (without @). If omitted, try to read from archive.")
    p.add_argument("--download", action="store_true", help="Download media from URLs if not present in the archive (requires 'requests').")
    args = p.parse_args(argv)

    archive_dir = Path(args.archive_dir).expanduser().resolve()
    out_data_dir = Path(args.out_data_dir)
    out_media_dir = Path(args.out_media_dir)

    try:
        n = process_archive(
            archive_dir=archive_dir,
            out_data_dir=out_data_dir,
            out_media_dir=out_media_dir,
            screen_name=args.screen_name,
            download_missing=args.download,
        )
        print(f"Wrote {n} tweets to {out_data_dir} and media to {out_media_dir}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
