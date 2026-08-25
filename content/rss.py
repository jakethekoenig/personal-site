from datetime import datetime
import os
from xml.sax.saxutils import escape

def generate(data, index):
    ans = ""
    for (path, entry) in dict(index)[data["Indexes"]][:data["Limit"]]:
        ans += rss_entry(entry)
    return ans

# Returns the xml snippet which describes the entry in the rss file.
def rss_entry(entry):
    ans = "<item>"
    ans+= "\n<title>"+escape(entry["Title"])+"</title>"
    ans+= "\n<link>"+escape(entry["permalink"])+"</link>"
    ans+= "\n<guid isPermaLink=\"true\">"+escape(entry["permalink"])+"</guid>"
    ans += "\n<pubDate>" + datetime.strptime(entry["Date"], "%Y-%m-%d").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    if "Summary" in entry:
        ans+= "\n<description>"+escape(entry["Summary"])+"</description>"
    rendered_content = entry["RenderedContent"].replace("]]>", "]]]]><![CDATA[>")
    ans += "\n<content:encoded><![CDATA[" + rendered_content + "]]></content:encoded>"
    ans += "\n</item>\n"
    return ans
