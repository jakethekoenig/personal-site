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

def extract_tweet_data(tweet_obj, user_screen_name=None):
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
    username = user.get('screen_name', user_screen_name or 'unknown')
    
    # Check if this is a self-reply (part of a thread)
    is_self_reply = False
    if in_reply_to_user and user_screen_name:
        is_self_reply = in_reply_to_user.lower() == user_screen_name.lower()
    elif in_reply_to_user and username != 'unknown':
        is_self_reply = in_reply_to_user.lower() == username.lower()
    
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
        'is_self_reply': is_self_reply,
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

def build_thread_structure(tweets):
    """Build thread structure from tweets."""
    # Create a map of tweet_id to tweet
    tweet_map = {tweet['id']: tweet for tweet in tweets if tweet['id']}
    
    # Find thread roots and build thread chains
    threads = {}  # thread_root_id -> list of tweets in thread
    thread_membership = {}  # tweet_id -> thread_root_id
    
    for tweet in tweets:
        if not tweet['id']:
            continue
            
        # Skip if this is a reply to someone else
        if tweet.get('in_reply_to_user') and not tweet.get('is_self_reply'):
            continue
            
        # If this is not a reply, it's a potential thread root
        if not tweet.get('in_reply_to_status_id'):
            threads[tweet['id']] = [tweet]
            thread_membership[tweet['id']] = tweet['id']
    
    # Now find all self-replies and add them to threads
    for tweet in tweets:
        if not tweet['id']:
            continue
            
        if tweet.get('is_self_reply') and tweet.get('in_reply_to_status_id'):
            # Find the thread this belongs to
            parent_id = tweet['in_reply_to_status_id']
            
            # Walk up the chain to find the root
            current_id = parent_id
            visited = set()
            
            while current_id and current_id not in visited:
                visited.add(current_id)
                
                if current_id in thread_membership:
                    # Found the thread root
                    root_id = thread_membership[current_id]
                    threads[root_id].append(tweet)
                    thread_membership[tweet['id']] = root_id
                    break
                    
                # Look for parent
                if current_id in tweet_map:
                    parent_tweet = tweet_map[current_id]
                    if parent_tweet.get('in_reply_to_status_id'):
                        current_id = parent_tweet['in_reply_to_status_id']
                    else:
                        # This is a root we haven't seen yet
                        if current_id not in threads:
                            threads[current_id] = [parent_tweet]
                            thread_membership[current_id] = current_id
                        threads[current_id].append(tweet)
                        thread_membership[tweet['id']] = current_id
                        break
                else:
                    # Parent not in our dataset, make this tweet a root
                    if tweet['id'] not in threads:
                        threads[tweet['id']] = [tweet]
                        thread_membership[tweet['id']] = tweet['id']
                    break
    
    # Sort tweets within each thread by timestamp
    for thread_id in threads:
        threads[thread_id].sort(key=lambda x: x.get('timestamp', 0))
    
    # Add thread information to tweets
    for thread_id, thread_tweets in threads.items():
        for i, tweet in enumerate(thread_tweets):
            tweet['thread_id'] = thread_id
            tweet['thread_position'] = i
            tweet['thread_length'] = len(thread_tweets)
            tweet['is_thread'] = len(thread_tweets) > 1
    
    return threads, thread_membership

def process_twitter_archive(archive_path, output_dir):
    """Process the entire Twitter archive."""
    
    # Convert output_dir to Path object
    output_dir = Path(output_dir)
    
    # Create output directories
    tweets_dir = output_dir / 'tweets'
    tweets_dir.mkdir(parents=True, exist_ok=True)
    
    assets_dir = output_dir / 'assets' / 'crosspoast'
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Try to detect user's screen name from account.js
    user_screen_name = None
    account_file = Path(archive_path) / 'data' / 'account.js'
    if account_file.exists():
        account_data = parse_js_file(account_file)
        if account_data and len(account_data) > 0:
            user_screen_name = account_data[0].get('account', {}).get('username')
            print(f"Detected username: @{user_screen_name}")
    
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
                tweet_data = extract_tweet_data(tweet_obj, user_screen_name)
                
                # Process media
                if tweet_data['media']:
                    tweet_data['processed_media'] = download_media(
                        tweet_data['media'], 
                        assets_dir, 
                        tweet_data['id']
                    )
                
                all_tweets.append(tweet_data)
    
    # Build thread structure
    print("Building thread structure...")
    threads, thread_membership = build_thread_structure(all_tweets)
    
    # Filter tweets: only include non-replies OR self-replies (threads)
    filtered_tweets = []
    for tweet in all_tweets:
        # Skip retweets if desired
        # if tweet['is_retweet']:
        #     continue
        
        # Include if: not a reply, OR is a self-reply (part of a thread)
        if not tweet.get('in_reply_to_user') or tweet.get('is_self_reply'):
            filtered_tweets.append(tweet)
    
    # Sort tweets by timestamp (newest first)
    filtered_tweets.sort(key=lambda x: x['timestamp'] or 0, reverse=True)
    
    print(f"Found {len(all_tweets)} total tweets")
    print(f"Filtered to {len(filtered_tweets)} tweets (excluding replies to others)")
    print(f"Found {len(threads)} threads")
    
    # Save individual tweet files
    for tweet in filtered_tweets:
        if tweet['id']:
            tweet_file = tweets_dir / f"{tweet['id']}.json"
            with open(tweet_file, 'w', encoding='utf-8') as f:
                json.dump(tweet, f, indent=2, ensure_ascii=False)
    
    # Save master file with filtered tweets
    master_file = output_dir / 'all_tweets.json'
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_tweets, f, indent=2, ensure_ascii=False)
    
    # Save threads file
    threads_file = output_dir / 'threads.json'
    threads_list = []
    for thread_id, thread_tweets in threads.items():
        if len(thread_tweets) > 1:  # Only save actual threads
            threads_list.append({
                'thread_id': thread_id,
                'tweets': thread_tweets
            })
    with open(threads_file, 'w', encoding='utf-8') as f:
        json.dump(threads_list, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(filtered_tweets)} tweets to {tweets_dir}")
    print(f"Master file saved to {master_file}")
    print(f"Threads file saved to {threads_file}")
    
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
    
    return filtered_tweets

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
