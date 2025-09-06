import json
import os
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
    html = f"<p><strong>Total tweets:</strong> {len(sorted_tweets)}</p>\n"
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
                    # Convert markdown images to HTML
                    import re
                    tweet_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="tweet-image">', tweet_text)
                    
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
    
    html = f"""
    <div class="tweet thread" id="thread-{thread_data.get('tweet_id', '')}">
        <div class="thread-header">
            <div class="thread-info">
                <span class="thread-indicator">🧵 Thread ({thread_length} tweets)</span>
                <span class="tweet-date">{thread_data.get('Date', '')}</span>
            </div>
            <a href="{first_url}" target="_blank" class="tweet-link">View thread on Twitter</a>
        </div>
        <div class="thread-content">
    """
    
    for i, part in enumerate(thread_parts, 1):
        content = part['content'].replace('\n\n', '</p><p>').replace('\n', '<br>')
        if content and not content.startswith('<'):
            content = f"<p>{content}</p>"
            
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
