import json
import os
import sys
from datetime import datetime

# Add the exhibit scripts directory to the path to import markdown processor
sys.path.append('../exhibit/scripts')
from content import md2html

# Twitter icon SVG constant to avoid duplication
TWITTER_ICON_SVG = '''<svg class="twitter-icon" viewBox="0 0 24 24" width="16" height="16">
    <path fill="#1da1f2" d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
</svg>'''

def generate(data, index):
    """Generate the tweets page content"""
    
    # Get all tweets from the index
    tweets_index = dict(index).get("short", [])
    
    if not tweets_index:
        return "<p>No tweets found. Run the Twitter archive processing script first.</p>"
    
    # Sort tweets by date (newest first)
    sorted_tweets = sorted(tweets_index, key=lambda x: parse_date_for_sorting(x[1].get("Date", "")), reverse=True)
    
    # Generate HTML
    html = f"<p>A mirror of short posts form other platforms. This site has already outlived Twitter. Best to start keeping a record now.</p>\n"
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
    """Generate HTML for a single tweet or thread"""
    
    # Check if this is a thread
    is_thread = tweet_data.get('is_thread', False)
    
    if is_thread:
        return generate_thread_html(tweet_data)
    else:
        return generate_single_tweet_html(tweet_data)

def generate_single_tweet_html(tweet_data):
    """Generate HTML for a single tweet"""
    
    # Read the tweet content
    content_path = os.path.join("content", tweet_data.get("Content", ""))
    tweet_content = ""
    
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            tweet_content = f.read()
    else:
        tweet_content = tweet_data.get("Summary", "")
    
    # Clean up the content
    tweet_content = tweet_content.strip()
    
    # Process markdown content properly
    if tweet_content:
        tweet_content = md2html(tweet_content)
        # Add tweet-specific image class to any images
        tweet_content = tweet_content.replace('<img ', '<img class="tweet-image" ')
    
    # Generate individual page link
    individual_page_url = f"/{tweet_data.get('relative_path', '')}"
    
    html = f"""
    <div class="tweet" id="tweet-{tweet_data.get('tweet_id', '')}">
        <div class="tweet-header">
            <span class="tweet-date">{tweet_data.get('Date', '')}</span>
            <div class="tweet-links">
                <a href="{individual_page_url}" class="tweet-page-link" title="View individual page">
                    <img src="/asset/favicon.png" alt="Individual page" class="favicon-icon">
                </a>
                <a href="{tweet_data.get('tweet_url', '#')}" target="_blank" class="tweet-twitter-link" title="View on Twitter">
                    {TWITTER_ICON_SVG}
                </a>
            </div>
        </div>
        <div class="tweet-content">
            {tweet_content}
        </div>
    </div>
    """
    
    return html

def generate_thread_html(thread_data):
    """Generate HTML for a tweet thread"""
    
    # Read the thread content
    content_path = os.path.join("content", thread_data.get("Content", ""))
    thread_content = ""
    
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            thread_content = f.read()
    else:
        thread_content = thread_data.get("Summary", "")
    
    # Parse the thread content to extract individual tweets
    thread_parts = []
    if thread_content.startswith("# Thread"):
        # Split by "## Tweet" sections
        sections = thread_content.split("## Tweet ")[1:]  # Skip the "# Thread" part
        
        for section in sections:
            if section.strip():
                lines = section.split('\n')
                # Extract tweet number and content
                tweet_num = lines[0].strip()
                
                # Find content between the tweet number and the separator
                content_lines = []
                for line in lines[1:]:
                    if line.strip() == '---':
                        break
                    if line.strip():
                        content_lines.append(line)
                
                if content_lines:
                    tweet_text = '\n'.join(content_lines).strip()
                    # Process markdown content properly
                    tweet_text = md2html(tweet_text)
                    # Add tweet-specific image class to any images
                    tweet_text = tweet_text.replace('<img ', '<img class="tweet-image" ')
                    
                    thread_parts.append({
                        'number': tweet_num,
                        'content': tweet_text
                    })
    
    # If we couldn't parse the thread content, fall back to summary
    if not thread_parts:
        thread_parts = [{'number': '1', 'content': thread_data.get("Summary", "")}]
    
    # Generate HTML for the thread
    thread_length = thread_data.get('thread_length', len(thread_parts))
    thread_urls = thread_data.get('thread_urls', [])
    first_url = thread_urls[0] if thread_urls else '#'
    
    # Generate individual page link for thread
    individual_page_url = f"/{thread_data.get('relative_path', '')}"
    
    html = f"""
    <div class="tweet thread" id="thread-{thread_data.get('tweet_id', '')}">
        <div class="thread-header">
            <div class="thread-info">
                <span class="thread-indicator">🧵 Thread ({thread_length} tweets)</span>
                <span class="tweet-date">{thread_data.get('Date', '')}</span>
            </div>
            <div class="tweet-links">
                <a href="{individual_page_url}" class="tweet-page-link" title="View individual page">
                    <img src="/asset/favicon.png" alt="Individual page" class="favicon-icon">
                </a>
                <a href="{first_url}" target="_blank" class="tweet-twitter-link" title="View thread on Twitter">
                    {TWITTER_ICON_SVG}
                </a>
            </div>
        </div>
        <div class="thread-content">
    """
    
    for i, part in enumerate(thread_parts, 1):
        content = part['content']
        # Content is already processed as HTML from markdown
            
        html += f"""
            <div class="thread-tweet">
                <div class="thread-tweet-number"></div>
                <div class="thread-tweet-content">
                    {content}
                </div>
            </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html
