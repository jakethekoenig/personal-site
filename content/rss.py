from datetime import datetime
import os

def generate(data, index):
    ans = ""
    for (path, entry) in dict(index)[data["Indexes"]][:data["Limit"]]:
        ans += rss_entry(entry)
    return ans

# Returns the xml snippet which describes the entry in the rss file.
def rss_entry(entry):
    ans = "<item>"
    ans+= "\n<title>"+entry["Title"]+"</title>"
    ans+= "\n<link>"+entry["permalink"]+"</link>"
    ans+= "\n<guid isPermaLink=\"true\">"+entry["permalink"]+"</guid>"
    ans += "\n<pubDate>" + datetime.strptime(entry["Date"], "%Y-%m-%d").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    if "Summary" in entry:
        ans+= "\n<description>"+entry["Summary"]+"</description>"
    ans += "\n<content:encoded><![CDATA[" + entry["RenderedContent"] + "]]></content:encoded>"
    ans += "\n</item>\n"
    return ans

