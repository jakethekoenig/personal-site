#!/usr/bin/env python3
"""
Script to process Twitter archive and extract tweets into JSON format
similar to the blog post structure used by this site.

Usage: python3 scripts/one_off/tweet_migration/process_twitter_archive.py <path_to_twitter_archive>
"""

import json
import os
import sys
import shutil
import re
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import argparse


TWITTER_USERNAME = "ja3k_"


class ArchiveSource:
    """Read a Twitter archive from either an extracted directory or its ZIP."""

    def __init__(self, archive_path):
        self.path = Path(archive_path)
        self.zip_file = None
        self.zip_names = set()
        if self.path.is_dir():
            return
        if zipfile.is_zipfile(self.path):
            self.zip_file = zipfile.ZipFile(self.path)
            self.zip_names = set(self.zip_file.namelist())
            return
        raise ValueError(f"Archive must be a directory or ZIP file: {archive_path}")

    def close(self):
        if self.zip_file:
            self.zip_file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @staticmethod
    def normalized(relative_path):
        return str(relative_path).replace(os.sep, "/").strip("/")

    def exists(self, relative_path):
        relative_path = self.normalized(relative_path)
        if self.zip_file:
            return relative_path in self.zip_names
        return (self.path / relative_path).is_file()

    def is_dir(self, relative_path):
        relative_path = self.normalized(relative_path).rstrip("/") + "/"
        if self.zip_file:
            return any(name.startswith(relative_path) for name in self.zip_names)
        return (self.path / relative_path).is_dir()

    def read_text(self, relative_path):
        relative_path = self.normalized(relative_path)
        if self.zip_file:
            return self.zip_file.read(relative_path).decode("utf-8")
        return (self.path / relative_path).read_text(encoding="utf-8")

    def list_files(self, relative_dir, prefix=""):
        relative_dir = self.normalized(relative_dir).rstrip("/")
        if self.zip_file:
            directory_prefix = relative_dir + "/"
            return [
                name.removeprefix(directory_prefix)
                for name in self.zip_names
                if name.startswith(directory_prefix)
                and "/" not in name.removeprefix(directory_prefix)
                and name.removeprefix(directory_prefix).startswith(prefix)
            ]
        directory = self.path / relative_dir
        return [
            path.name
            for path in directory.iterdir()
            if path.is_file() and path.name.startswith(prefix)
        ]

    def copy_file(self, relative_path, destination):
        relative_path = self.normalized(relative_path)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if self.zip_file:
            with self.zip_file.open(relative_path) as source, destination.open("wb") as dest:
                shutil.copyfileobj(source, dest)
        else:
            shutil.copy2(self.path / relative_path, destination)

def parse_twitter_date(date_str):
    """Parse Twitter's date format to an ISO date."""
    # Twitter dates are typically in format: "Wed Oct 05 19:41:02 +0000 2011"
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        # Try ISO format as backup
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return date_str


def twitter_datetime(date_str):
    """Parse a Twitter timestamp for chronological thread ordering."""
    try:
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat((date_str or "").replace("Z", "+00:00"))
        except ValueError:
            return datetime.min.astimezone()

def extract_tweet_id_from_url(url):
    """Extract tweet ID from Twitter URL"""
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else None


def existing_tweet_ids(output_dir):
    """Return every X/Twitter post ID already represented in short-form data."""
    tweet_ids = set()
    for path in Path(output_dir).glob("*.json"):
        if path.name == "default.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Warning: Could not inspect existing record {path}: {error}")
            continue
        for urls in data.get("posts", []):
            for url in urls:
                tweet_id = extract_tweet_id_from_url(url)
                if tweet_id:
                    tweet_ids.add(tweet_id)
    return tweet_ids

def clean_tweet_text(text):
    """Clean tweet text for display"""
    # Remove t.co links that are just URL shorteners
    text = re.sub(r'https://t\.co/\w+', '', text)
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def process_quoted_tweet(tweet, tweet_map=None):
    """Extract quoted tweet information if present"""
    quoted_tweet_info = None
    
    # Check for quoted tweet in various possible locations
    if 'quoted_status' in tweet:
        quoted = tweet['quoted_status']
        quoted_user = quoted.get('user', {}).get('screen_name', 'unknown')
        quoted_text = quoted.get('full_text', quoted.get('text', ''))
        quoted_id = quoted.get('id_str', quoted.get('id', ''))
        
        if quoted_text and quoted_id:
            quoted_tweet_info = {
                'user': quoted_user,
                'text': clean_tweet_text(quoted_text),
                'url': f"https://twitter.com/{quoted_user}/status/{quoted_id}"
            }
    
    # Check for quote tweets referenced via URLs in entities
    if not quoted_tweet_info and 'entities' in tweet and 'urls' in tweet['entities']:
        for url_entity in tweet['entities']['urls']:
            expanded_url = url_entity.get('expanded_url', '')
            
            # Check if this is a Twitter/X URL pointing to a tweet
            if expanded_url and ('twitter.com' in expanded_url or 'x.com' in expanded_url):
                # Extract username and tweet ID from URL
                # Format: https://x.com/username/status/tweet_id or https://twitter.com/username/status/tweet_id
                match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)', expanded_url)
                if match:
                    quoted_user = match.group(1)
                    quoted_id = match.group(2)
                    archived_quote = (tweet_map or {}).get(quoted_id, {})
                    quoted_text = clean_tweet_text(
                        archived_quote.get('full_text', archived_quote.get('text', ''))
                    )
                    quoted_tweet_info = {
                        'user': quoted_user,
                        'text': quoted_text or None,
                        'url': expanded_url,
                    }
                    if not quoted_text:
                        quoted_tweet_info['is_url_reference'] = True
                    break
    
    return quoted_tweet_info

def media_filename(media):
    """Return the archive filename represented by a media entity."""
    if media.get("type") in {"video", "animated_gif"}:
        variants = [
            variant
            for variant in media.get("video_info", {}).get("variants", [])
            if variant.get("content_type") == "video/mp4" and variant.get("url")
        ]
        if variants:
            variant = max(variants, key=lambda item: int(item.get("bitrate", 0)))
            return os.path.basename(urlparse(variant["url"]).path), variant["url"]
    media_url = media.get("media_url_https") or media.get("media_url", "")
    return os.path.basename(urlparse(media_url).path), media_url


def process_media(tweet, archive, media_dir, output_media_dir):
    """Process media files associated with a tweet"""
    media_files = []
    
    # Get tweet ID for filename matching
    tweet_id = tweet.get('id_str', tweet.get('id', ''))
    
    # Check multiple possible locations for media in the tweet data
    media_sources = []
    
    # Extended entities (most common)
    if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
        media_sources.extend(tweet['extended_entities']['media'])
    
    # Regular entities (fallback)
    if 'entities' in tweet and 'media' in tweet['entities']:
        media_sources.extend(tweet['entities']['media'])

    # The same attachment normally appears in both entity collections. Prefer
    # the richer extended entity so video variants are not processed twice.
    unique_media_sources = []
    seen_media = set()
    for media in media_sources:
        identity = media.get('id_str') or media.get('media_url_https') or media.get('media_url')
        if identity in seen_media:
            continue
        seen_media.add(identity)
        unique_media_sources.append(media)

    for media in unique_media_sources:
        if media.get('media_url') or media.get('media_url_https'):
            # Extract filename from URL
            original_filename, media_url = media_filename(media)
            
            # Twitter archives often prefix media files with tweet ID
            # Try different possible filename patterns
            possible_filenames = [
                # With tweet ID prefix (most common in archives)
                f"{tweet_id}-{original_filename}",
                f"{tweet_id}-{original_filename.replace('.jpg', '.png')}",
                f"{tweet_id}-{original_filename.replace('.png', '.jpg')}",
                # Without prefix (fallback)
                original_filename,
                original_filename.replace('.jpg', '.png'),
                original_filename.replace('.png', '.jpg'),
                original_filename + '.jpg',
                original_filename + '.png'
            ]
            
            actual_filename = None
            for possible_filename in possible_filenames:
                archive_path = os.path.join(media_dir, possible_filename)
                if archive.exists(archive_path):
                    actual_filename = possible_filename
                    break

            # Newer archives store video files under the tweet ID plus the
            # highest-bitrate variant's basename. Fall back to that prefix if
            # X changes the entity URL shape again.
            if not actual_filename and media.get('type') in {'video', 'animated_gif'}:
                video_files = [
                    filename
                    for filename in archive.list_files(media_dir, f"{tweet_id}-")
                    if filename.lower().endswith((".mp4", ".mov", ".webm"))
                ]
                if video_files:
                    actual_filename = sorted(video_files)[0]

            if actual_filename:
                # Drop the redundant tweet-ID prefix used inside the archive.
                output_filename = actual_filename.removeprefix(f"{tweet_id}-")
                
                # Copy to output directory
                os.makedirs(output_media_dir, exist_ok=True)
                dest_path = os.path.join(output_media_dir, output_filename)
                archive.copy_file(os.path.join(media_dir, actual_filename), dest_path)
                
                # Store relative path for the JSON
                media_files.append({
                    'type': 'video' if media.get('type') == 'animated_gif' else media.get('type', 'photo'),
                    'url': f"/asset/crosspoast/{output_filename}",
                    'original_url': media_url
                })
                print(f"Found media: {actual_filename} -> {output_filename}")
            else:
                print(f"Warning: Could not find media file for {original_filename} (tried with tweet ID {tweet_id})")

    ans = []
    urls = set()
    for media_file in media_files:
        if media_file['url'] not in urls:
            ans.append(media_file)
            urls.add(media_file['url'])

    return ans

def process_tweets_js_file(file_path):
    """Process tweets.js file from Twitter archive"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return process_tweets_js_content(f.read(), str(file_path))


def process_tweets_js_content(content, source="tweets.js"):
    """Parse the JavaScript assignment wrapping archive tweet JSON."""
    tweets = []
    for prefix in (
        'window.YTD.tweets.part0 = ',
        'window.YTD.tweet.part0 = ',
    ):
        if content.startswith(prefix):
            content = content[len(prefix):]
            break
    content = content.rstrip().rstrip(';')

    try:
        data = json.loads(content)
        for item in data:
            tweets.append(item['tweet'] if 'tweet' in item else item)
    except json.JSONDecodeError as error:
        print(f"Error parsing JSON from {source}: {error}")
        return []
    return tweets

def identify_tweet_threads(tweets, username="ja3k_"):
    """Identify which tweets are part of threads by the same user"""
    tweet_map = {
        tweet.get('id_str', tweet.get('id', '')): tweet
        for tweet in tweets
        if tweet.get('id_str', tweet.get('id', ''))
    }
    parent_by_id = {}
    children_by_id = {}
    for tweet_id, tweet in tweet_map.items():
        parent_id = tweet.get('in_reply_to_status_id_str')
        parent_user = tweet.get('in_reply_to_screen_name')
        if (
            parent_id in tweet_map
            and parent_user
            and parent_user.lower() == username.lower()
        ):
            parent_by_id[tweet_id] = parent_id
            children_by_id.setdefault(parent_id, []).append(tweet_id)

    roots = set()
    for tweet_id in parent_by_id:
        root_id = tweet_id
        visited = set()
        while root_id in parent_by_id and root_id not in visited:
            visited.add(root_id)
            root_id = parent_by_id[root_id]
        roots.add(root_id)

    threads = {}
    tweet_to_thread = {}
    for root_id in roots:
        root = tweet_map[root_id]
        root_reply_user = root.get('in_reply_to_screen_name')
        if root_reply_user and root_reply_user.lower() != username.lower():
            continue

        ids = []
        pending = [root_id]
        visited = set()
        while pending:
            tweet_id = pending.pop()
            if tweet_id in visited:
                continue
            visited.add(tweet_id)
            ids.append(tweet_id)
            pending.extend(children_by_id.get(tweet_id, []))
        if len(ids) < 2:
            continue

        thread_tweets = sorted(
            (tweet_map[tweet_id] for tweet_id in ids),
            key=lambda tweet: twitter_datetime(tweet.get('created_at', '')),
        )
        threads[root_id] = thread_tweets
        for tweet_id in ids:
            tweet_to_thread[tweet_id] = root_id

    return threads, tweet_to_thread

def process_twitter_archive(
    archive_path,
    output_dir="data/short",
    media_output_dir="nongenerated/asset/crosspoast",
    content_output_dir="content/short",
):
    """Incrementally add previously unseen posts from a Twitter archive."""
    with ArchiveSource(archive_path) as archive:
        possible_paths = [
            'data/tweets.js',
            'data/tweet.js',
            'tweets.js',
            'tweet.js',
        ]
        tweets_file = next((path for path in possible_paths if archive.exists(path)), None)
        if not tweets_file:
            print("Could not find tweets.js or tweet.js file in the archive")
            print("Looked in:", possible_paths)
            return

        print(f"Processing tweets from: {archive_path}/{tweets_file}")
        possible_media_dirs = [
            'data/tweets_media',
            'data/tweet_media',
            'tweets_media',
            'tweet_media',
        ]
        media_dir = next(
            (path for path in possible_media_dirs if archive.is_dir(path)),
            None,
        )
        print(f"Found media directory: {media_dir}" if media_dir else "No media directory found")

        tweets = process_tweets_js_content(
            archive.read_text(tweets_file),
            f"{archive_path}/{tweets_file}",
        )
        tweet_map = {
            tweet.get('id_str', tweet.get('id', '')): tweet
            for tweet in tweets
            if tweet.get('id_str', tweet.get('id', ''))
        }
        print(f"Found {len(tweets)} tweets")
        threads, tweet_to_thread = identify_tweet_threads(tweets)
        print(f"Found {len(threads)} tweet threads")

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(content_output_dir, exist_ok=True)
        if media_dir:
            os.makedirs(media_output_dir, exist_ok=True)

        already_synced = existing_tweet_ids(output_dir)
        print(f"Found {len(already_synced)} already-synced Twitter post URLs")
        processed_count = 0
        skipped_count = 0
        processed_tweets = set()

        for thread_id, thread_tweets in threads.items():
            thread_ids = {
                tweet.get('id_str', tweet.get('id', ''))
                for tweet in thread_tweets
            }
            processed_tweets.update(thread_ids)
            if thread_ids & already_synced:
                skipped_count += len(thread_ids)
                continue
            try:
                thread_data = process_tweet_thread(
                    thread_tweets,
                    archive,
                    media_dir,
                    media_output_dir,
                    output_dir,
                    content_output_dir,
                    tweet_map,
                )
                if thread_data:
                    processed_count += len(thread_tweets)
            except Exception as error:
                print(f"Error processing thread {thread_id}: {error}")

        for tweet in tweets:
            try:
                tweet_id = tweet.get('id_str', tweet.get('id', ''))
                text = tweet.get('full_text', tweet.get('text', ''))
                created_at = tweet.get('created_at', '')
                if not tweet_id or not text or tweet_id in processed_tweets:
                    continue
                if tweet_id in already_synced:
                    skipped_count += 1
                    continue
                if text.startswith('RT @') or tweet.get('in_reply_to_status_id_str'):
                    continue

                clean_text = clean_tweet_text(text)
                media_files = []
                if media_dir:
                    media_files = process_media(
                        tweet,
                        archive,
                        media_dir,
                        media_output_dir,
                    )
                quoted_tweet = process_quoted_tweet(tweet, tweet_map)
                if not clean_text and not media_files and not quoted_tweet:
                    continue
                title_text = clean_text or "Media post"
                tweet_data = {
                    "Title": title_text[:100] + "..." if len(title_text) > 100 else title_text,
                    "Author": "Jake Koenig",
                    "URL": str(tweet_id),
                    "Template": "tweet.temp",
                    "Hide": True,
                    "Date": parse_twitter_date(created_at),
                    "Content": f"short/{tweet_id}.md",
                    "Summary": clean_text or title_text,
                    "Categories": ["tweets"],
                    "tweet_id": tweet_id,
                    "posts": [[f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}"]],
                    "original_date": created_at,
                    "media": media_files,
                    "quoted_tweet": quoted_tweet,
                    "is_thread": False,
                }

                json_path = os.path.join(output_dir, f"{tweet_id}.json")
                with open(json_path, 'w', encoding='utf-8') as output_file:
                    json.dump(tweet_data, output_file, indent=4, ensure_ascii=False)
                    output_file.write("\n")

                md_content = clean_text + "\n\n" if clean_text else ""
                if quoted_tweet:
                    if quoted_tweet.get('is_url_reference'):
                        md_content += f"> [Quote tweet of @{quoted_tweet['user']}]({quoted_tweet['url']})\n\n"
                    else:
                        md_content += f"> <strong>@{quoted_tweet['user']}:</strong> {quoted_tweet['text']}\n"
                        md_content += f"> [View original tweet]({quoted_tweet['url']})\n\n"
                md_content += media_markdown(media_files)
                md_path = os.path.join(content_output_dir, f"{tweet_id}.md")
                with open(md_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(md_content)

                processed_count += 1
                if processed_count % 1000 == 0:
                    print(f"Processed {processed_count} tweets...")
            except Exception as error:
                print(f"Error processing tweet {tweet.get('id_str', 'unknown')}: {error}")

        print(f"Successfully processed {processed_count} new tweets")
        print(f"Preserved {skipped_count} tweets already represented on the site")
        print(f"JSON files saved to: {output_dir}")
        print(f"Markdown files saved to: {content_output_dir}")
        if media_dir:
            print(f"Media files saved to: {media_output_dir}")


def media_markdown(media_files):
    """Render imported media references for a short-form Markdown section."""
    markdown = ""
    for media in media_files:
        if media['type'] == 'photo':
            markdown += f"![Tweet image]({media['url']})\n\n"
        elif media['type'] in {'video', 'animated_gif'}:
            markdown += f"[Video: {media['url']}]({media['url']})\n\n"
    return markdown


def process_tweet_thread(
    thread_tweets,
    archive,
    media_dir,
    media_output_dir,
    output_dir,
    content_output_dir="content/short",
    tweet_map=None,
):
    """Process a thread of tweets as a single unit"""
    
    if not thread_tweets:
        return None
    
    # Use the first tweet's ID as the thread ID
    first_tweet = thread_tweets[0]
    thread_id = first_tweet.get('id_str', first_tweet.get('id', ''))
    
    if not thread_id:
        return None
    
    # Collect all text and media from the thread
    thread_parts = []
    all_media = []
    
    for tweet in thread_tweets:
        tweet_id = tweet.get('id_str', tweet.get('id', ''))
        text = tweet.get('full_text', tweet.get('text', ''))
        clean_text = clean_tweet_text(text)
        # Check for quoted tweet and include it
        quoted_tweet = process_quoted_tweet(tweet, tweet_map)
        if quoted_tweet:
            if quoted_tweet.get('is_url_reference'):
                # For URL-only references, show a simple link
                clean_text += f"\n\n> [Quote tweet of @{quoted_tweet['user']}]({quoted_tweet['url']})"
            else:
                # For full quoted tweets with text
                clean_text += f"\n\n> <strong>@{quoted_tweet['user']}:</strong> {quoted_tweet['text']}\n> [View original tweet]({quoted_tweet['url']})"

        # Process media for this tweet
        media_files = []
        if media_dir:
            media_files = process_media(
                tweet,
                archive,
                media_dir,
                media_output_dir,
            )
            all_media.extend(media_files)

        if tweet_id:
            thread_parts.append({
                "text": clean_text.strip(),
                "media": media_files,
                "url": f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}",
            })

    thread_text_parts = [part["text"] for part in thread_parts]
    tweet_urls = [part["url"] for part in thread_parts]
    
    if not any(thread_text_parts) and not all_media:
        return None
    
    # Combine thread text
    full_thread_text = "\n\n".join(text for text in thread_text_parts if text)
    first_text = next((text for text in thread_text_parts if text), "Media post")
    
    # Create thread data
    thread_data = {
        "Title": f"Thread: {first_text[:80]}..." if len(first_text) > 80 else f"Thread: {first_text}",
        "Author": "Jake Koenig",
        "URL": str(thread_id),
        "Template": "tweet.temp",
        "Hide": True,
        "Date": parse_twitter_date(first_tweet.get('created_at', '')),
        "Content": f"short/thread_{thread_id}.md",
        "Summary": full_thread_text[:200] + "..." if len(full_thread_text) > 200 else (full_thread_text or "Media thread"),
        "Categories": ["tweets", "threads"],
        "tweet_id": thread_id,
        "posts": [[url] for url in tweet_urls],
        "original_date": first_tweet.get('created_at', ''),
        "media": all_media,
        "is_thread": True,
        "thread_length": len(thread_tweets)
    }
    
    json_path = os.path.join(output_dir, f"thread_{thread_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(thread_data, f, indent=4, ensure_ascii=False)
        f.write("\n")
    
    # Create markdown content file
    content_dir = content_output_dir
    os.makedirs(content_dir, exist_ok=True)
    
    md_content = "# Thread\n\n"
    
    for i, part in enumerate(thread_parts, 1):
        md_content += f"## Tweet {i}\n\n"
        if part["text"]:
            md_content += part["text"] + "\n\n"
        md_content += media_markdown(part["media"])
        md_content += "---\n\n"
    
    md_path = os.path.join(content_dir, f"thread_{thread_id}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return thread_data

def main():
    parser = argparse.ArgumentParser(description='Process Twitter archive into blog-like format')
    parser.add_argument('archive_path', help='Path to the Twitter archive directory')
    parser.add_argument('--output-dir', default='data/short', help='Output directory for JSON files')
    parser.add_argument('--media-dir', default='nongenerated/asset/crosspoast', help='Output directory for media files')
    parser.add_argument('--content-dir', default='content/short', help='Output directory for Markdown files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.archive_path):
        print(f"Error: Archive path '{args.archive_path}' does not exist")
        sys.exit(1)
    
    process_twitter_archive(
        args.archive_path,
        args.output_dir,
        args.media_dir,
        args.content_dir,
    )

if __name__ == "__main__":
    main()
