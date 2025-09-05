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
    
    if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
        for media in tweet['extended_entities']['media']:
            if 'media_url' in media:
                # Extract filename from URL
                filename = os.path.basename(urlparse(media['media_url']).path)
                
                # Look for the file in the archive's media directory
                source_path = os.path.join(media_dir, filename)
                if os.path.exists(source_path):
                    # Copy to output directory
                    os.makedirs(output_media_dir, exist_ok=True)
                    dest_path = os.path.join(output_media_dir, filename)
                    shutil.copy2(source_path, dest_path)
                    
                    # Store relative path for the JSON
                    media_files.append({
                        'type': media.get('type', 'photo'),
                        'url': f"/assets/crosspoast/{filename}",
                        'original_url': media['media_url']
                    })
    
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
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    if media_dir:
        os.makedirs(media_output_dir, exist_ok=True)
    
    processed_count = 0
    
    for tweet in tweets:
        try:
            # Extract basic tweet info
            tweet_id = tweet.get('id_str', tweet.get('id', ''))
            text = tweet.get('full_text', tweet.get('text', ''))
            created_at = tweet.get('created_at', '')
            
            if not tweet_id or not text:
                continue
            
            # Skip retweets (they start with "RT @")
            if text.startswith('RT @'):
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
                "Template": "tweet.temp",  # We'll create this template
                "Date": parse_twitter_date(created_at),
                "Content": f"tweets/{tweet_id}.md",  # We'll create markdown files
                "Summary": clean_text,
                "Categories": ["tweets"],
                "tweet_id": tweet_id,
                "tweet_url": f"https://twitter.com/ja3k_/status/{tweet_id}",
                "original_date": created_at,
                "media": media_files
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
            
            md_content += f"[View original tweet]({tweet_data['tweet_url']})\n"
            
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
