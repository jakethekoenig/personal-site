#!/usr/bin/env python3
"""
Process Twitter archive and extract tweets to JSON format.
This script expects the Twitter archive to be extracted in a directory.
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path
import shutil
import hashlib

def parse_js_file(filepath):
    """Parse Twitter's JavaScript file format to extract JSON data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Twitter archive files start with a variable assignment like:
    # window.YTD.tweets.part0 = [ ... ]
    # We need to extract just the JSON array part
    match = re.search(r'=\s*(\[.*\])', content, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {filepath}: {e}")
            return None
    return None

def extract_tweet_data(tweet_obj):
    """Extract relevant data from a tweet object."""
    tweet = tweet_obj.get('tweet', tweet_obj)
    
    # Extract basic info
    tweet_id = tweet.get('id_str', tweet.get('id'))
    created_at = tweet.get('created_at')
    
    # Parse timestamp
    if created_at:
        # Twitter format: "Wed Oct 10 20:19:24 +0000 2018"
        dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        timestamp = dt.timestamp()
        pretty_time = dt.strftime("%B %d, %Y %I:%M %p")
    else:
        timestamp = None
        pretty_time = None
    
    # Get tweet text - handle both old and new formats
    text = tweet.get('full_text', tweet.get('text', ''))
    
    # Extract media if present
    media = []
    entities = tweet.get('entities', {})
    extended_entities = tweet.get('extended_entities', entities)
    
    if 'media' in extended_entities:
        for media_item in extended_entities['media']:
            media_info = {
                'type': media_item.get('type'),
                'url': media_item.get('media_url_https', media_item.get('media_url')),
                'display_url': media_item.get('display_url'),
                'expanded_url': media_item.get('expanded_url')
            }
            media.append(media_info)
    
    # Check if it's a retweet or reply
    is_retweet = text.startswith('RT @') or 'retweeted_status' in tweet
    in_reply_to = tweet.get('in_reply_to_status_id_str')
    in_reply_to_user = tweet.get('in_reply_to_screen_name')
    
    # Get user info (for building URLs)
    user = tweet.get('user', {})
    username = user.get('screen_name', 'unknown')
    
    # Build tweet URL
    if tweet_id and username:
        tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
    else:
        tweet_url = None
    
    return {
        'id': tweet_id,
        'text': text,
        'created_at': created_at,
        'timestamp': timestamp,
        'pretty_time': pretty_time,
        'url': tweet_url,
        'is_retweet': is_retweet,
        'in_reply_to_status_id': in_reply_to,
        'in_reply_to_user': in_reply_to_user,
        'media': media,
        'username': username
    }

def download_media(media_list, output_dir, tweet_id):
    """
    Process media URLs and prepare them for local storage.
    Note: Actual downloading would require the files to be present in the archive.
    """
    processed_media = []
    
    for media in media_list:
        if media['url']:
            # Get file extension from URL
            url = media['url']
            ext = os.path.splitext(url)[1] or '.jpg'
            
            # Create a filename based on tweet ID and media index
            filename = f"{tweet_id}_{len(processed_media)}{ext}"
            local_path = f"/assets/crosspoast/{filename}"
            
            processed_media.append({
                'type': media['type'],
                'original_url': url,
                'local_path': local_path,
                'filename': filename
            })
    
    return processed_media

def process_twitter_archive(archive_path, output_dir):
    """Process the entire Twitter archive."""
    
    # Create output directories
    tweets_dir = Path(output_dir) / 'tweets'
    tweets_dir.mkdir(parents=True, exist_ok=True)
    
    assets_dir = Path(output_dir) / 'assets' / 'crosspoast'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Look for tweet data files
    tweet_files = []
    data_dir = Path(archive_path) / 'data'
    
    if data_dir.exists():
        # Find all tweet.js or tweets.js files
        for file in data_dir.glob('**/*tweet*.js'):
            tweet_files.append(file)
    
    if not tweet_files:
        print(f"No tweet files found in {archive_path}/data/")
        print("Make sure you've extracted the Twitter archive and it contains a 'data' directory.")
        return
    
    all_tweets = []
    
    # Process each tweet file
    for tweet_file in tweet_files:
        print(f"Processing {tweet_file}...")
        tweets_data = parse_js_file(tweet_file)
        
        if tweets_data:
            for tweet_obj in tweets_data:
                tweet_data = extract_tweet_data(tweet_obj)
                
                # Skip retweets if desired (optional)
                # if tweet_data['is_retweet']:
                #     continue
                
                # Process media
                if tweet_data['media']:
                    tweet_data['processed_media'] = download_media(
                        tweet_data['media'], 
                        assets_dir, 
                        tweet_data['id']
                    )
                
                all_tweets.append(tweet_data)
    
    # Sort tweets by timestamp (newest first)
    all_tweets.sort(key=lambda x: x['timestamp'] or 0, reverse=True)
    
    print(f"Found {len(all_tweets)} tweets")
    
    # Save individual tweet files
    for tweet in all_tweets:
        if tweet['id']:
            tweet_file = tweets_dir / f"{tweet['id']}.json"
            with open(tweet_file, 'w', encoding='utf-8') as f:
                json.dump(tweet, f, indent=2, ensure_ascii=False)
    
    # Also save a master file with all tweets
    master_file = output_dir / 'all_tweets.json'
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(all_tweets, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_tweets)} tweets to {tweets_dir}")
    print(f"Master file saved to {master_file}")
    
    # Copy media files if they exist in the archive
    media_source = Path(archive_path) / 'data' / 'tweets_media'
    if media_source.exists():
        print(f"Copying media files from {media_source}...")
        for media_file in media_source.glob('*'):
            dest = assets_dir / media_file.name
            shutil.copy2(media_file, dest)
        print(f"Media files copied to {assets_dir}")
    else:
        print("Note: No media directory found in archive. You'll need to manually add media files.")
    
    return all_tweets

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_twitter_archive.py <path_to_twitter_archive> [output_directory]")
        print("\nExample: python process_twitter_archive.py ~/Downloads/twitter-archive ./")
        sys.exit(1)
    
    archive_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    if not os.path.exists(archive_path):
        print(f"Error: Archive path '{archive_path}' does not exist")
        sys.exit(1)
    
    process_twitter_archive(archive_path, output_dir)

if __name__ == "__main__":
    main()
