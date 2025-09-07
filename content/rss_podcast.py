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
    
    # Add podcast-specific content if available
    if "Content" in podcast:
        content_path = os.path.join("content", podcast["Content"])
        if os.path.exists(content_path):
            with open(content_path, "r") as f:
                content = f.read()
            ans += "<content:encoded><![CDATA[" + content + "]]></content:encoded>"
    
    ans += "<pubDate>" + datetime.strptime(podcast["Date"], "%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    ans += "</item>\n"
    return ans
