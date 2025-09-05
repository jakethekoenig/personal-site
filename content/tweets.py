import os
import json
from datetime import datetime

def generate(data, index):
    """Generate the tweets page content"""
    
    # Get all tweets from the index
    tweets_index = dict(index).get("tweets", [])
    
    if not tweets_index:
        return "<p>No tweets found. Run the Twitter archive processing script first.</p>"
    
    # Sort tweets by date (newest first)
    sorted_tweets = sorted(tweets_index, key=lambda x: parse_date_for_sorting(x[1].get("Date", "")), reverse=True)
    
    # Generate HTML
    html = f"<p>{data['Summary']}</p>\n"
    html += f"<p><strong>Total tweets:</strong> {len(sorted_tweets)}</p>\n"
    html += "<div class='tweets-container'>\n"
    
    for path, tweet_data in sorted_tweets:
        html += generate_tweet_html(tweet_data)
    
    html += "</div>\n"
    
    return html

def parse_date_for_sorting(date_str):
    """Parse date string for sorting purposes"""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        return datetime.min

def generate_tweet_html(tweet_data):
    """Generate HTML for a single tweet"""
    
    # Read the tweet content
    content_path = os.path.join("content", tweet_data.get("Content", ""))
    tweet_content = ""
    
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            tweet_content = f.read()
    else:
        tweet_content = tweet_data.get("Summary", "")
    
    # Remove the "View original tweet" link from content since we'll add our own
    lines = tweet_content.split('\n')
    filtered_lines = [line for line in lines if not line.startswith('[View original tweet]')]
    tweet_content = '\n'.join(filtered_lines).strip()
    
    # Convert markdown images to HTML
    import re
    tweet_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="tweet-image">', tweet_content)
    
    # Convert newlines to <br> tags for display
    tweet_content = tweet_content.replace('\n\n', '</p><p>').replace('\n', '<br>')
    
    # Wrap in paragraph tags if not empty
    if tweet_content and not tweet_content.startswith('<'):
        tweet_content = f"<p>{tweet_content}</p>"
    
    html = f"""
    <div class="tweet" id="tweet-{tweet_data.get('tweet_id', '')}">
        <div class="tweet-header">
            <span class="tweet-date">{tweet_data.get('Date', '')}</span>
            <a href="{tweet_data.get('tweet_url', '#')}" target="_blank" class="tweet-link">View on Twitter</a>
        </div>
        <div class="tweet-content">
            {tweet_content}
        </div>
    </div>
    """
    
    return html
