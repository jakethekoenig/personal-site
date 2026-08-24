import json
import os
import sys
from pathlib import Path

# Add the integrated build scripts to the path to import the markdown processor.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "build"))
from content import md2html
from shortform_render import (
    render_thread_content,
    shortform_sort_key,
    source_links_html,
    thread_indicator_text,
)


def generate(data, index):
    """Generate the tweets page content"""
    
    # Get all tweets from the index
    tweets_index = dict(index).get("short", [])
    
    if not tweets_index:
        return "<p>No tweets found. Run the Twitter archive processing script first.</p>"
    
    # Sort tweets by date (newest first)
    sorted_tweets = sorted(
        tweets_index,
        key=lambda item: shortform_sort_key(item[1]),
        reverse=True,
    )
    
    # Generate HTML
    html = f"<p>A mirror of short posts form other platforms. This site has already outlived Twitter. Best to start keeping a record now.</p>\n"
    html += "<div class='tweets-container'>\n"
    
    for path, tweet_data in sorted_tweets:
        html += generate_tweet_html(tweet_data)
    
    html += "</div>\n"
    
    return html

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
    badge = source_links_html(tweet_data) or '<a href="#">Unknown source</a>'
    
    html = f"""
    <div class="tweet" id="tweet-{tweet_data.get('tweet_id', '')}">
        <div class="tweet-header">
            <span class="tweet-date">{tweet_data.get('Date', '')}</span>
            <div class="tweet-links">
                <a href="{individual_page_url}" class="tweet-page-link" title="View individual page">
                    <img src="/asset/favicon.png" alt="Individual page" class="favicon-icon">
                </a>
                {badge}
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
    
    rendered_thread = render_thread_content(
        thread_content,
        md2html,
        thread_data.get("Summary", ""),
    )
    
    # Generate HTML for the thread
    individual_page_url = f"/{thread_data.get('relative_path', '')}"
    badge = source_links_html(thread_data) or '<a href="#">Unknown source</a>'
    
    html = f"""
    <div class="tweet thread" id="thread-{thread_data.get('tweet_id', '')}">
        <div class="thread-header">
            <div class="thread-info">
                <span class="thread-indicator">{thread_indicator_text(thread_data)}</span>
                <span class="tweet-date">{thread_data.get('Date', '')}</span>
            </div>
            <div class="tweet-links">
                <a href="{individual_page_url}" class="tweet-page-link" title="View individual page">
                    <img src="/asset/favicon.png" alt="Individual page" class="favicon-icon">
                </a>
                {badge}
            </div>
        </div>
        {rendered_thread}
    """
    html += """
    </div>
    """
    
    return html
