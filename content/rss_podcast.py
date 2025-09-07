from datetime import datetime
import os

def generate(data, index):
    ans = ""
    for (path, podcast) in dict(index)["pod"]:
        ans += rss_entry(podcast)
    return ans

# Returns the xml snippet which describes the podcast entry in the rss file.
def rss_entry(podcast):
    ans = "<item>"
    ans += "<title>" + podcast["Title"] + "</title>"
    ans += "<link>" + podcast["permalink"] + "</link>"
    ans += "<guid isPermaLink=\"true\">" + podcast["permalink"] + "</guid>"
    if "Summary" in podcast:
        ans += "<description>" + podcast["Summary"] + "</description>"
    
    # Include full content for RSS readers
    if "Content" in podcast:
        content_path = os.path.join("content", podcast["Content"])
        try:
            with open(content_path, "r", encoding='utf-8') as f:
                content = f.read()
            ans += "<content:encoded><![CDATA[" + content + "]]></content:encoded>"
        except (FileNotFoundError, UnicodeDecodeError):
            pass  # Skip content if file can't be read
    
    ans += "<pubDate>" + datetime.strptime(podcast["Date"], "%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S -0500") + "</pubDate>"
    ans += "</item>\n"
    return ans
