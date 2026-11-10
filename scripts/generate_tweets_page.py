#!/usr/bin/env python3
"""
Generate a static HTML page displaying all tweets.
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
import html

def load_tweets(tweets_dir):
    """Load all tweet JSON files from the tweets directory."""
    tweets = []
    tweets_path = Path(tweets_dir)
    
    # Try to load from master file first
    master_file = tweets_path.parent / 'all_tweets.json'
    if master_file.exists():
        with open(master_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Otherwise load individual files
    for tweet_file in tweets_path.glob('*.json'):
        with open(tweet_file, 'r', encoding='utf-8') as f:
            tweets.append(json.load(f))
    
    # Sort by timestamp
    tweets.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    return tweets

def process_tweet_text(text):
    """Process tweet text to add links and formatting."""
    # Escape HTML
    text = html.escape(text)
    
    # Convert URLs to links
    url_pattern = r'(https?://[^\s]+)'
    text = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)
    
    # Convert @mentions to links
    mention_pattern = r'@(\w+)'
    text = re.sub(mention_pattern, r'<a href="https://twitter.com/\1" target="_blank">@\1</a>', text)
    
    # Convert #hashtags to links
    hashtag_pattern = r'#(\w+)'
    text = re.sub(hashtag_pattern, r'<a href="https://twitter.com/hashtag/\1" target="_blank">#\1</a>', text)
    
    # Convert newlines to <br>
    text = text.replace('\n', '<br>')
    
    return text

def generate_tweet_html(tweet, is_in_thread=False):
    """Generate HTML for a single tweet."""
    tweet_id = tweet.get('id', 'unknown')
    text = tweet.get('text', '')
    pretty_time = tweet.get('pretty_time', '')
    url = tweet.get('url', '#')
    is_retweet = tweet.get('is_retweet', False)
    in_reply_to_user = tweet.get('in_reply_to_user')
    is_self_reply = tweet.get('is_self_reply', False)
    media = tweet.get('processed_media', [])
    thread_position = tweet.get('thread_position', 0)
    thread_length = tweet.get('thread_length', 1)
    is_thread = tweet.get('is_thread', False)
    
    # Process text
    processed_text = process_tweet_text(text)
    
    # Build HTML
    tweet_class = 'tweet'
    if is_retweet:
        tweet_class += ' retweet'
    if in_reply_to_user and not is_self_reply:
        tweet_class += ' reply'
    if is_in_thread:
        tweet_class += ' in-thread'
        if thread_position == 0:
            tweet_class += ' thread-start'
        elif thread_position == thread_length - 1:
            tweet_class += ' thread-end'
        else:
            tweet_class += ' thread-middle'
    
    html_parts = [f'<div class="{tweet_class}" id="tweet-{tweet_id}" data-thread-position="{thread_position}" data-thread-length="{thread_length}">']
    
    # Add metadata
    html_parts.append('<div class="tweet-header">')
    
    if is_retweet:
        html_parts.append('<span class="tweet-type">🔁 Retweet</span>')
    elif is_thread and thread_position == 0:
        html_parts.append(f'<span class="tweet-type">🧵 Thread ({thread_length} tweets)</span>')
    elif in_reply_to_user and not is_self_reply:
        html_parts.append(f'<span class="tweet-type">↩️ Reply to @{in_reply_to_user}</span>')
    
    html_parts.append(f'<span class="tweet-time">{pretty_time}</span>')
    
    if url:
        html_parts.append(f'<a href="{url}" target="_blank" class="tweet-link">View on Twitter ↗</a>')
    
    html_parts.append('</div>')
    
    # Add tweet content
    html_parts.append(f'<div class="tweet-content">{processed_text}</div>')
    
    # Add media if present
    if media:
        html_parts.append('<div class="tweet-media">')
        for media_item in media:
            if media_item['type'] == 'photo':
                local_path = media_item['local_path']
                html_parts.append(f'<img src="{local_path}" alt="Tweet media" loading="lazy">')
            elif media_item['type'] == 'video':
                local_path = media_item['local_path']
                html_parts.append(f'<video controls><source src="{local_path}" type="video/mp4"></video>')
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def organize_tweets_with_threads(tweets):
    """Organize tweets, grouping threads together."""
    organized = []
    seen_ids = set()
    
    # Group tweets by thread_id
    threads = {}
    standalone = []
    
    for tweet in tweets:
        if tweet['id'] in seen_ids:
            continue
            
        if tweet.get('is_thread') and tweet.get('thread_id'):
            thread_id = tweet['thread_id']
            if thread_id not in threads:
                threads[thread_id] = []
            threads[thread_id].append(tweet)
        else:
            standalone.append(tweet)
    
    # Sort threads by their first tweet's timestamp
    for thread_tweets in threads.values():
        thread_tweets.sort(key=lambda x: x.get('thread_position', 0))
    
    # Combine threads and standalone tweets, sorted by timestamp
    all_items = []
    
    # Add threads as single items with their first tweet's timestamp
    for thread_id, thread_tweets in threads.items():
        if thread_tweets:
            first_tweet_time = thread_tweets[0].get('timestamp') or 0
            all_items.append(('thread', first_tweet_time, thread_tweets))
    
    # Add standalone tweets
    for tweet in standalone:
        tweet_time = tweet.get('timestamp') or 0
        all_items.append(('single', tweet_time, tweet))
    
    # Sort all items by timestamp (newest first)
    all_items.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
    
    # Build final organized list
    for item_type, _, item_data in all_items:
        if item_type == 'thread':
            for tweet in item_data:
                organized.append(tweet)
                seen_ids.add(tweet['id'])
        else:
            organized.append(item_data)
            seen_ids.add(item_data['id'])
    
    return organized

def generate_page_html(tweets, standalone=False):
    """Generate the complete HTML page.
    
    Args:
        tweets: List of tweet dictionaries
        standalone: If True, generate a complete HTML page. If False, generate just the content.
    """
    
    # Organize tweets with threads grouped
    organized_tweets = organize_tweets_with_threads(tweets)
    
    # Count statistics
    total_tweets = len(tweets)
    retweets = sum(1 for t in tweets if t.get('is_retweet', False))
    replies = sum(1 for t in tweets if t.get('in_reply_to_user') and not t.get('is_self_reply'))
    threads_count = len(set(t.get('thread_id') for t in tweets if t.get('is_thread')))
    original = total_tweets - retweets - replies
    
    # Start building HTML
    if standalone:
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jake's Tweets - Complete Archive</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        
        h1 {
            color: #1da1f2;
            border-bottom: 3px solid #1da1f2;
            padding-bottom: 10px;
        }
        
        .stats {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stats span {
            margin-right: 20px;
            font-weight: bold;
        }
        
        .filters {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .filter-button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .filter-button:hover {
            background: #0d8bd9;
        }
        
        .filter-button.active {
            background: #0d8bd9;
        }
        
        .tweet {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .tweet:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .tweet.retweet {
            border-left: 4px solid #19cf86;
        }
        
        .tweet.reply {
            border-left: 4px solid #ffa500;
        }
        
        .tweet.in-thread {
            margin-left: 20px;
            position: relative;
        }
        
        .tweet.in-thread::before {
            content: '';
            position: absolute;
            left: -20px;
            top: -15px;
            bottom: -15px;
            width: 2px;
            background: #1da1f2;
        }
        
        .tweet.thread-start::before {
            top: 50%;
        }
        
        .tweet.thread-end::before {
            bottom: 50%;
        }
        
        .tweet-header {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .tweet-type {
            color: #19cf86;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .reply .tweet-type {
            color: #ffa500;
        }
        
        .tweet-time {
            color: #999;
        }
        
        .tweet-link {
            color: #1da1f2;
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .tweet-link:hover {
            text-decoration: underline;
        }
        
        .tweet-content {
            margin: 10px 0;
            word-wrap: break-word;
        }
        
        .tweet-content a {
            color: #1da1f2;
            text-decoration: none;
        }
        
        .tweet-content a:hover {
            text-decoration: underline;
        }
        
        .tweet-media {
            margin-top: 10px;
        }
        
        .tweet-media img, .tweet-media video {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .hidden {
            display: none;
        }
        
        #load-more {
            display: block;
            margin: 20px auto;
            padding: 10px 30px;
            background: #1da1f2;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
        }
        
        #load-more:hover {
            background: #0d8bd9;
        }
        
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            
            .tweet-header {
                font-size: 0.8em;
            }
        }
    </style>
</head>
<body>
    <h1>Jake's Complete Tweet Archive</h1>"""
    else:
        # For integration with site template, just provide the content and inline styles
        html = """
    <style>
        .tweet {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .tweet:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .tweet.retweet {
            border-left: 4px solid #19cf86;
        }
        
        .tweet.reply {
            border-left: 4px solid #ffa500;
        }
        
        .tweet.in-thread {
            margin-left: 20px;
            position: relative;
        }
        
        .tweet.in-thread::before {
            content: '';
            position: absolute;
            left: -20px;
            top: -15px;
            bottom: -15px;
            width: 2px;
            background: #1da1f2;
        }
        
        .tweet.thread-start::before {
            top: 50%;
        }
        
        .tweet.thread-end::before {
            bottom: 50%;
        }
        
        .tweet-header {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .tweet-type {
            color: #19cf86;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .reply .tweet-type {
            color: #ffa500;
        }
        
        .tweet-time {
            color: #999;
        }
        
        .tweet-link {
            color: #1da1f2;
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .tweet-link:hover {
            text-decoration: underline;
        }
        
        .tweet-content {
            margin: 10px 0;
            word-wrap: break-word;
        }
        
        .tweet-content a {
            color: #1da1f2;
            text-decoration: none;
        }
        
        .tweet-content a:hover {
            text-decoration: underline;
        }
        
        .tweet-media {
            margin-top: 10px;
        }
        
        .tweet-media img, .tweet-media video {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .stats {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stats span {
            margin-right: 20px;
            font-weight: bold;
        }
        
        .filters {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .filter-button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .filter-button:hover {
            background: #0d8bd9;
        }
        
        .filter-button.active {
            background: #0d8bd9;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        #load-more {
            display: block;
            margin: 20px auto;
            padding: 10px 30px;
            background: #1da1f2;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
        }
        
        #load-more:hover {
            background: #0d8bd9;
        }
    </style>
    <h1>Complete Tweet Archive</h1>"""
    
    html += """
    
    <div class="stats">
        <span>Total: """ + str(total_tweets) + """</span>
        <span>Original: """ + str(original) + """</span>
        <span>Retweets: """ + str(retweets) + """</span>
        <span>Threads: """ + str(threads_count) + """</span>
    </div>
    
    <div class="filters">
        <input type="text" class="search-box" id="search" placeholder="Search tweets...">
        <div>
            <button class="filter-button active" data-filter="all">All</button>
            <button class="filter-button" data-filter="original">Original</button>
            <button class="filter-button" data-filter="retweet">Retweets</button>
            <button class="filter-button" data-filter="thread">Threads</button>
        </div>
    </div>
    
    <div id="tweets-container">
"""
    
    # Add tweets (initially show first 100)
    prev_thread_id = None
    for i, tweet in enumerate(organized_tweets[:100]):
        is_in_thread = tweet.get('is_thread', False)
        html += generate_tweet_html(tweet, is_in_thread)
        prev_thread_id = tweet.get('thread_id')
    
    html += """
    </div>
    
    <button id="load-more">Load More Tweets</button>
    
    <script>
        // Store all tweets for client-side filtering
        const allTweets = """ + json.dumps([generate_tweet_html(t, t.get('is_thread', False)) for t in organized_tweets], ensure_ascii=False) + """;
        let currentIndex = 100;
        const tweetsPerLoad = 100;
        
        // Load more functionality
        document.getElementById('load-more').addEventListener('click', function() {
            const container = document.getElementById('tweets-container');
            const endIndex = Math.min(currentIndex + tweetsPerLoad, allTweets.length);
            
            for (let i = currentIndex; i < endIndex; i++) {
                container.insertAdjacentHTML('beforeend', allTweets[i]);
            }
            
            currentIndex = endIndex;
            
            if (currentIndex >= allTweets.length) {
                this.style.display = 'none';
            }
            
            applyCurrentFilter();
        });
        
        // Filter functionality
        let currentFilter = 'all';
        
        document.querySelectorAll('.filter-button').forEach(button => {
            button.addEventListener('click', function() {
                document.querySelectorAll('.filter-button').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.dataset.filter;
                applyCurrentFilter();
            });
        });
        
        function applyCurrentFilter() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            const tweets = document.querySelectorAll('.tweet');
            
            tweets.forEach(tweet => {
                let show = true;
                
                // Apply type filter
                if (currentFilter !== 'all') {
                    if (currentFilter === 'original') {
                        show = !tweet.classList.contains('retweet') && !tweet.classList.contains('reply') && !tweet.classList.contains('in-thread');
                    } else if (currentFilter === 'thread') {
                        show = tweet.classList.contains('in-thread');
                    } else {
                        show = tweet.classList.contains(currentFilter);
                    }
                }
                
                // Apply search filter
                if (show && searchTerm) {
                    const content = tweet.querySelector('.tweet-content').textContent.toLowerCase();
                    show = content.includes(searchTerm);
                }
                
                tweet.style.display = show ? 'block' : 'none';
            });
        }
        
        // Search functionality
        document.getElementById('search').addEventListener('input', applyCurrentFilter);
    </script>"""
    
    if standalone:
        html += """
</body>
</html>"""
    
    return html

def create_data_json(output_dir):
    """Create the data JSON file for the tweets page."""
    data = {
        "Title": "Tweets Archive",
        "Author": "Jake Koenig",
        "URL": "tweets",
        "Template": "empty.temp",
        "Date": datetime.now().strftime("%m/%d/%Y"),
        "Content": "tweets.html",
        "Summary": "Complete archive of all my tweets",
        "Categories": ["social"]
    }
    
    data_file = Path(output_dir) / 'data' / 'tweets.json'
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Created data file: {data_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_tweets_page.py <tweets_directory> [output_file]")
        print("\nExample: python generate_tweets_page.py ./tweets ./content/tweets.html")
        sys.exit(1)
    
    tweets_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else './content/tweets.html'
    
    if not os.path.exists(tweets_dir):
        print(f"Error: Tweets directory '{tweets_dir}' does not exist")
        print("Run process_twitter_archive.py first to extract tweets")
        sys.exit(1)
    
    print(f"Loading tweets from {tweets_dir}...")
    tweets = load_tweets(tweets_dir)
    
    if not tweets:
        print("No tweets found!")
        sys.exit(1)
    
    print(f"Generating HTML for {len(tweets)} tweets...")
    html = generate_page_html(tweets, standalone=True)
    
    # Save HTML file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated tweets page: {output_path}")
    
    # Create data JSON file
    create_data_json('.')
    
    # Print some stats
    retweets = sum(1 for t in tweets if t.get('is_retweet', False))
    replies = sum(1 for t in tweets if t.get('in_reply_to_user') and not t.get('is_self_reply'))
    threads_count = len(set(t.get('thread_id') for t in tweets if t.get('is_thread')))
    original = len(tweets) - retweets - replies
    
    print(f"\nStatistics:")
    print(f"  Total tweets: {len(tweets)}")
    print(f"  Original tweets: {original}")
    print(f"  Retweets: {retweets}")
    print(f"  Threads: {threads_count}")

if __name__ == "__main__":
    main()
