#!/usr/bin/env python3
"""
Script to process Twitter archive and extract tweets into JSON format
similar to the blog post structure used by this site.

Usage: python process_twitter_archive.py <path_to_twitter_archive>
"""

import json
import os
import sys
import shutil
import re
from datetime import datetime
from urllib.parse import urlparse
import argparse

def parse_twitter_date(date_str):
    """Parse Twitter's date format to a readable format"""
    # Twitter dates are typically in format: "Wed Oct 05 19:41:02 +0000 2011"
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%m/%d/%Y")
    except ValueError:
        # Try ISO format as backup
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            return date_str

def extract_tweet_id_from_url(url):
    """Extract tweet ID from Twitter URL"""
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else None

def clean_tweet_text(text):
    """Clean tweet text for display"""
    # Remove t.co links that are just URL shorteners
    text = re.sub(r'https://t\.co/\w+', '', text)
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text.strip()

def process_media(tweet, media_dir, output_media_dir):
    """Process media files associated with a tweet"""
    media_files = []
    
    # Check multiple possible locations for media in the tweet data
    media_sources = []
    
    # Extended entities (most common)
    if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
        media_sources.extend(tweet['extended_entities']['media'])
    
    # Regular entities (fallback)
    if 'entities' in tweet and 'media' in tweet['entities']:
        media_sources.extend(tweet['entities']['media'])
    
    for media in media_sources:
        if 'media_url' in media:
            # Extract filename from URL
            media_url = media['media_url']
            filename = os.path.basename(urlparse(media_url).path)
            
            # Try different possible filenames and extensions
            possible_filenames = [
                filename,
                filename.replace('.jpg', '.png'),
                filename.replace('.png', '.jpg'),
                filename + '.jpg',
                filename + '.png'
            ]
            
            source_path = None
            for possible_filename in possible_filenames:
                test_path = os.path.join(media_dir, possible_filename)
                if os.path.exists(test_path):
                    source_path = test_path
                    filename = possible_filename
                    break
            
            if source_path:
                # Copy to output directory
                os.makedirs(output_media_dir, exist_ok=True)
                dest_path = os.path.join(output_media_dir, filename)
                shutil.copy2(source_path, dest_path)
                
                # Store relative path for the JSON
                media_files.append({
                    'type': media.get('type', 'photo'),
                    'url': f"/assets/crosspoast/{filename}",
                    'original_url': media_url
                })
            else:
                print(f"Warning: Could not find media file for {filename}")
    
    return media_files

def process_tweets_js_file(file_path):
    """Process tweets.js file from Twitter archive"""
    tweets = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Twitter archive files often start with "window.YTD.tweets.part0 = "
        # Remove this prefix to get valid JSON
        if content.startswith('window.YTD.tweets.part0 = '):
            content = content[len('window.YTD.tweets.part0 = '):]
        elif content.startswith('window.YTD.tweet.part0 = '):
            content = content[len('window.YTD.tweet.part0 = '):]
        
        # Remove trailing semicolon if present
        content = content.rstrip(';')
        
        try:
            data = json.loads(content)
            
            for item in data:
                if 'tweet' in item:
                    tweets.append(item['tweet'])
                else:
                    tweets.append(item)
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {file_path}: {e}")
            return []
    
    return tweets

def identify_tweet_threads(tweets, username="ja3k_"):
    """Identify which tweets are part of threads by the same user"""
    
    # Create a mapping of tweet_id -> tweet for quick lookup
    tweet_map = {}
    for tweet in tweets:
        tweet_id = tweet.get('id_str', tweet.get('id', ''))
        if tweet_id:
            tweet_map[tweet_id] = tweet
    
    # First pass: identify all replies to the same user
    replies_to_user = {}  # original_tweet_id -> list of reply tweets
    
    for tweet in tweets:
        tweet_id = tweet.get('id_str', tweet.get('id', ''))
        if not tweet_id:
            continue
            
        # Check if this is a reply to the same user
        reply_to_id = tweet.get('in_reply_to_status_id_str')
        reply_to_user = tweet.get('in_reply_to_screen_name')
        
        if reply_to_id and reply_to_user and reply_to_user.lower() == username.lower():
            if reply_to_id not in replies_to_user:
                replies_to_user[reply_to_id] = []
            replies_to_user[reply_to_id].append(tweet)
    
    # Second pass: build threads by following the chain of replies
    threads = {}  # thread_id -> list of tweets in thread
    tweet_to_thread = {}  # tweet_id -> thread_id
    
    def build_thread_chain(start_tweet_id, visited=None):
        """Recursively build a thread chain starting from a tweet"""
        if visited is None:
            visited = set()
        
        if start_tweet_id in visited or start_tweet_id not in tweet_map:
            return []
        
        visited.add(start_tweet_id)
        chain = [tweet_map[start_tweet_id]]
        
        # Add all direct replies to this tweet
        if start_tweet_id in replies_to_user:
            for reply_tweet in replies_to_user[start_tweet_id]:
                reply_id = reply_tweet.get('id_str', reply_tweet.get('id', ''))
                if reply_id and reply_id not in visited:
                    chain.append(reply_tweet)
                    # Recursively add replies to this reply
                    chain.extend(build_thread_chain(reply_id, visited))
        
        return chain
    
    # Find all tweets that have replies (potential thread starters)
    for original_tweet_id in replies_to_user.keys():
        if original_tweet_id not in tweet_to_thread:  # Not already processed
            thread_chain = build_thread_chain(original_tweet_id)
            
            if len(thread_chain) > 1:  # Only consider it a thread if it has multiple tweets
                # Sort by creation date to maintain chronological order
                thread_chain.sort(key=lambda t: t.get('created_at', ''))
                
                thread_id = original_tweet_id
                threads[thread_id] = thread_chain
                
                # Mark all tweets in this thread
                for tweet in thread_chain:
                    tweet_id = tweet.get('id_str', tweet.get('id', ''))
                    if tweet_id:
                        tweet_to_thread[tweet_id] = thread_id
    
    return threads, tweet_to_thread

def process_twitter_archive(archive_path, output_dir="data/tweets", media_output_dir="nongenerated/assets/crosspoast"):
    """Process the entire Twitter archive"""
    
    # Look for tweets data file
    tweets_file = None
    possible_paths = [
        os.path.join(archive_path, 'data', 'tweets.js'),
        os.path.join(archive_path, 'data', 'tweet.js'),
        os.path.join(archive_path, 'tweets.js'),
        os.path.join(archive_path, 'tweet.js')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            tweets_file = path
            break
    
    if not tweets_file:
        print("Could not find tweets.js or tweet.js file in the archive")
        print("Looked in:", possible_paths)
        return
    
    print(f"Processing tweets from: {tweets_file}")
    
    # Find media directory
    media_dir = None
    possible_media_dirs = [
        os.path.join(archive_path, 'data', 'tweets_media'),
        os.path.join(archive_path, 'data', 'tweet_media'),
        os.path.join(archive_path, 'tweets_media'),
        os.path.join(archive_path, 'tweet_media')
    ]
    
    for path in possible_media_dirs:
        if os.path.exists(path):
            media_dir = path
            break
    
    if media_dir:
        print(f"Found media directory: {media_dir}")
    else:
        print("No media directory found")
    
    # Process tweets
    tweets = process_tweets_js_file(tweets_file)
    print(f"Found {len(tweets)} tweets")
    
    # Identify tweet threads
    threads, tweet_to_thread = identify_tweet_threads(tweets)
    print(f"Found {len(threads)} tweet threads")
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    if media_dir:
        os.makedirs(media_output_dir, exist_ok=True)
    
    processed_count = 0
    processed_tweets = set()  # Track which tweets we've already processed
    
    # Process threads first
    for thread_id, thread_tweets in threads.items():
        try:
            # Sort thread tweets by date
            thread_tweets.sort(key=lambda t: t.get('created_at', ''))
            
            # Process the thread as a single unit
            thread_data = process_tweet_thread(thread_tweets, media_dir, media_output_dir, output_dir)
            if thread_data:
                processed_count += len(thread_tweets)
                for tweet in thread_tweets:
                    tweet_id = tweet.get('id_str', tweet.get('id', ''))
                    if tweet_id:
                        processed_tweets.add(tweet_id)
                        
        except Exception as e:
            print(f"Error processing thread {thread_id}: {e}")
            continue
    
    # Process individual tweets (not part of threads)
    for tweet in tweets:
        try:
            # Extract basic tweet info
            tweet_id = tweet.get('id_str', tweet.get('id', ''))
            text = tweet.get('full_text', tweet.get('text', ''))
            created_at = tweet.get('created_at', '')
            
            if not tweet_id or not text:
                continue
                
            # Skip if already processed as part of a thread
            if tweet_id in processed_tweets:
                continue
            
            # Skip retweets (they start with "RT @")
            if text.startswith('RT @'):
                continue
                
            # Skip replies that are not part of our own threads
            if tweet.get('in_reply_to_status_id_str'):
                continue
            
            # Clean the text
            clean_text = clean_tweet_text(text)
            if not clean_text:
                continue
            
            # Process media
            media_files = []
            if media_dir:
                media_files = process_media(tweet, media_dir, media_output_dir)
            
            # Create JSON structure similar to blog posts
            tweet_data = {
                "Title": clean_text[:100] + "..." if len(clean_text) > 100 else clean_text,
                "Author": "Jake Koenig",
                "URL": f"tweet_{tweet_id}",
                "Template": "tweet.temp",
                "Date": parse_twitter_date(created_at),
                "Content": f"tweets/{tweet_id}.md",
                "Summary": clean_text,
                "Categories": ["tweets"],
                "tweet_id": tweet_id,
                "tweet_url": f"https://twitter.com/ja3k_/status/{tweet_id}",
                "original_date": created_at,
                "media": media_files,
                "is_thread": False
            }
            
            # Save JSON file
            json_path = os.path.join(output_dir, f"{tweet_id}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(tweet_data, f, indent=4, ensure_ascii=False)
            
            # Create markdown content file
            content_dir = os.path.join("content", "tweets")
            os.makedirs(content_dir, exist_ok=True)
            
            md_content = clean_text + "\n\n"
            
            # Add media if present
            if media_files:
                md_content += "\n"
                for media in media_files:
                    if media['type'] == 'photo':
                        md_content += f"![Tweet image]({media['url']})\n\n"
                    elif media['type'] == 'video':
                        md_content += f"[Video: {media['url']}]({media['url']})\n\n"
            
            md_path = os.path.join(content_dir, f"{tweet_id}.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            processed_count += 1
            
            if processed_count % 1000 == 0:
                print(f"Processed {processed_count} tweets...")
                
        except Exception as e:
            print(f"Error processing tweet {tweet.get('id_str', 'unknown')}: {e}")
            continue
    
    print(f"Successfully processed {processed_count} tweets")
    print(f"JSON files saved to: {output_dir}")
    print(f"Markdown files saved to: content/tweets")
    if media_dir:
        print(f"Media files saved to: {media_output_dir}")

def process_tweet_thread(thread_tweets, media_dir, media_output_dir, output_dir):
    """Process a thread of tweets as a single unit"""
    
    if not thread_tweets:
        return None
    
    # Use the first tweet's ID as the thread ID
    first_tweet = thread_tweets[0]
    thread_id = first_tweet.get('id_str', first_tweet.get('id', ''))
    
    if not thread_id:
        return None
    
    # Collect all text and media from the thread
    thread_text_parts = []
    all_media = []
    tweet_urls = []
    
    for tweet in thread_tweets:
        tweet_id = tweet.get('id_str', tweet.get('id', ''))
        text = tweet.get('full_text', tweet.get('text', ''))
        created_at = tweet.get('created_at', '')
        
        if not text:
            continue
            
        clean_text = clean_tweet_text(text)
        if clean_text:
            thread_text_parts.append(clean_text)
            
        # Process media for this tweet
        if media_dir:
            media_files = process_media(tweet, media_dir, media_output_dir)
            all_media.extend(media_files)
            
        # Add tweet URL
        if tweet_id:
            tweet_urls.append(f"https://twitter.com/ja3k_/status/{tweet_id}")
    
    if not thread_text_parts:
        return None
    
    # Combine thread text
    full_thread_text = "\n\n".join(thread_text_parts)
    
    # Create thread data
    thread_data = {
        "Title": f"Thread: {thread_text_parts[0][:80]}..." if len(thread_text_parts[0]) > 80 else f"Thread: {thread_text_parts[0]}",
        "Author": "Jake Koenig",
        "URL": f"thread_{thread_id}",
        "Template": "tweet.temp",
        "Date": parse_twitter_date(first_tweet.get('created_at', '')),
        "Content": f"tweets/thread_{thread_id}.md",
        "Summary": full_thread_text[:200] + "..." if len(full_thread_text) > 200 else full_thread_text,
        "Categories": ["tweets", "threads"],
        "tweet_id": thread_id,
        "thread_urls": tweet_urls,
        "original_date": first_tweet.get('created_at', ''),
        "media": all_media,
        "is_thread": True,
        "thread_length": len(thread_tweets)
    }
    
    # Save JSON file
    json_path = os.path.join(output_dir, f"thread_{thread_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(thread_data, f, indent=4, ensure_ascii=False)
    
    # Create markdown content file
    content_dir = os.path.join("content", "tweets")
    os.makedirs(content_dir, exist_ok=True)
    
    md_content = "# Thread\n\n"
    
    for i, (text_part, tweet_url) in enumerate(zip(thread_text_parts, tweet_urls), 1):
        md_content += f"## Tweet {i}\n\n"
        md_content += text_part + "\n\n"
        md_content += "---\n\n"
    
    md_path = os.path.join(content_dir, f"thread_{thread_id}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return thread_data

def main():
    parser = argparse.ArgumentParser(description='Process Twitter archive into blog-like format')
    parser.add_argument('archive_path', help='Path to the Twitter archive directory')
    parser.add_argument('--output-dir', default='data/tweets', help='Output directory for JSON files')
    parser.add_argument('--media-dir', default='nongenerated/assets/crosspoast', help='Output directory for media files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.archive_path):
        print(f"Error: Archive path '{args.archive_path}' does not exist")
        sys.exit(1)
    
    process_twitter_archive(args.archive_path, args.output_dir, args.media_dir)

if __name__ == "__main__":
    main()
