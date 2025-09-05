import os
import json
from datetime import datetime

TWEET_DATA_DIR = os.path.join("data", "tweets")

def generate(data, index):
    """
    Generates the HTML content for the tweets page by reading all tweet
    JSON files.
    """
    if not os.path.exists(TWEET_DATA_DIR):
        return "<p>Tweet data not found. Please run the `scripts/process_tweets.py` script first.</p>"

    all_tweets = []
    for filename in os.listdir(TWEET_DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TWEET_DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    tweet_data = json.load(f)
                    # Twitter's created_at format is 'Wed Jan 21 20:53:38 +0000 2009'
                    # We parse it to a datetime object for sorting.
                    tweet_data['created_at_dt'] = datetime.strptime(tweet_data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                    all_tweets.append(tweet_data)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Could not process file {filename}. Error: {e}")

    # Sort tweets by date, newest first
    all_tweets.sort(key=lambda x: x['created_at_dt'], reverse=True)

    if not all_tweets:
        return "<p>No tweets found to display.</p>"

    # Generate HTML for all tweets
    html_output = ""
    for tweet in all_tweets:
        # Format the date for display
        display_date = tweet['created_at_dt'].strftime('%B %d, %Y at %I:%M %p %Z')
        
        # Sanitize text for HTML display
        tweet_text_html = tweet.get('text', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        html_output += '<div class="tweet-container">\n'
        html_output += f'  <div class="tweet-header"><a href="{tweet["url"]}" target="_blank" rel="noopener noreferrer">Tweeted on {display_date}</a></div>\n'
        html_output += f'  <div class="tweet-text">{tweet_text_html}</div>\n'
        
        if tweet.get('media'):
            html_output += '  <div class="tweet-media">\n'
            for media_path in tweet['media']:
                html_output += f'    <img src="{media_path}" alt="Tweet media">\n'
            html_output += '  </div>\n'
            
        html_output += '</div>\n'

    return html_output
