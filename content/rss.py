from datetime import datetime
import os

def generate(data, index):
    ans = ""
    for (path, blog) in dict(index)["blog"][:20]:
        ans += rss_entry(blog)
    return ans

# Returns the xml snippet which describes the blogs entry in the rss file.
def rss_entry(blog):
    ans = "<item>"
    ans+= "\n<title>"+blog["Title"]+"</title>"
    ans+= "\n<link>"+blog["permalink"]+"</link>"
    ans+= "\n<guid isPermaLink=\"true\">"+blog["permalink"]+"</guid>"
    ans += "\n<pubDate>" + datetime.strptime(blog["Date"], "%Y-%m-%d").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    if "Summary" in blog:
        ans+= "\n<description>"+blog["Summary"]+"</description>"
    ans += "\n<content:encoded><![CDATA[" + blog["RenderedContent"] + "]]></content:encoded>"
    ans += "\n</item>\n"
    return ans

