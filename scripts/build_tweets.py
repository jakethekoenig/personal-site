#!/usr/bin/env python3
"""
Build tweets page integrated with the site's build system.
This script should be run after process_twitter_archive.py
"""

import json
import os
import sys
from pathlib import Path
from generate_tweets_page import load_tweets, generate_page_html

def integrate_tweets_into_site():
    """Integrate tweets into the existing site structure."""
    
    # Check if tweets have been processed
    if not os.path.exists('all_tweets.json'):
        print("Error: all_tweets.json not found. Run process_twitter_archive.py first.")
        sys.exit(1)
    
    # Load tweets
    print("Loading tweets...")
    with open('all_tweets.json', 'r', encoding='utf-8') as f:
        tweets = json.load(f)
    
    print(f"Found {len(tweets)} tweets")
    
    # Generate HTML content
    print("Generating tweets HTML...")
    html_content = generate_page_html(tweets)
    
    # Save to content directory
    content_path = Path('content/tweets.html')
    content_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Saved HTML to {content_path}")
    
    # Create/update data JSON for the site's build system
    data_path = Path('data/tweets.json')
    data_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Count statistics for the data file
    retweets = sum(1 for t in tweets if t.get('is_retweet', False))
    replies = sum(1 for t in tweets if t.get('in_reply_to_user') and not t.get('is_self_reply'))
    threads_count = len(set(t.get('thread_id') for t in tweets if t.get('is_thread')))
    original = len(tweets) - retweets - replies
    
    data = {
        "Title": "Tweets",
        "Author": "Jake Koenig",
        "URL": "tweets",
        "Template": "toplevel.temp",
        "Date": tweets[0].get('created_at', '').split()[1:4] if tweets else "01/01/2024",
        "Content": "tweets.html",
        "Summary": f"Archive of {len(tweets)} tweets: {original} original, {retweets} retweets, {threads_count} threads",
        "Categories": ["social"],
        "og_image": "/asset/pic/twitter_archive.png"  # You can add a custom image
    }
    
    # Convert date format if needed
    if tweets and tweets[0].get('created_at'):
        # Parse Twitter date format to site format
        from datetime import datetime
        date_str = tweets[0]['created_at']
        try:
            dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
            data["Date"] = dt.strftime("%m/%d/%Y")
        except:
            data["Date"] = "01/01/2024"
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Created data file at {data_path}")
    
    # Add tweets to the main index if needed
    index_path = Path('data/index.json')
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Check if tweets is already in the index
        if "Indexes" in index_data and "tweets" not in index_data.get("Indexes", ""):
            print("Note: You may want to add 'tweets' to your index.json Indexes field")
    
    print("\nTweets page integrated successfully!")
    print("The tweets page will be available at /tweets when you build your site")
    
    return True

def main():
    """Main entry point."""
    integrate_tweets_into_site()

if __name__ == "__main__":
    main()
