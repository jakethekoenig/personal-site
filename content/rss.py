from datetime import datetime
import os

def generate(data, index):
    ans = ""
    # Get blogs and sort by date (newest first), then limit to 30 most recent
    blogs = dict(index)["blog"]
    sorted_blogs = sorted(blogs, key=lambda x: parse_date_for_sorting(x[1].get("Date", "")), reverse=True)
    recent_blogs = sorted_blogs[:30]
    
    for (path, blog) in recent_blogs:
        ans += rss_entry(blog)
    return ans

def parse_date_for_sorting(date_str):
    """Parse date string for sorting purposes"""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        return datetime.min

# Returns the xml snippet which describes the blogs entry in the rss file.
def rss_entry(blog):
    ans = "<item>"
    ans+= "<title>"+blog["Title"]+"</title>"
    ans+= "<link>"+blog["permalink"]+"</link>"
    ans+= "<guid isPermaLink=\"true\">"+blog["permalink"]+"</guid>"
    if "Summary" in blog:
        ans+= "<description>"+blog["Summary"]+"</description>"
    
    # Include full content for RSS readers
    if "Content" in blog:
        content_path = os.path.join("content", blog["Content"])
        try:
            with open(content_path, "r", encoding='utf-8') as f:
                content = f.read()
            ans += "<content:encoded><![CDATA[" + content + "]]></content:encoded>"
        except (FileNotFoundError, UnicodeDecodeError):
            pass  # Skip content if file can't be read
    ans += "<pubDate>" + datetime.strptime(blog["Date"],"%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S -0500") + "</pubDate>"
    ans += "</item>\n"
    return ans


