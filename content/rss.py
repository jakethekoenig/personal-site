from url_tools import url, blogFullUrl
from datetime import datetime

def generate(data, index):
    ans = ""
    for (path, blog) in dict(index)["blog"]:
        ans += rss_entry(blog)
    return ans

# Returns the xml snippet which describes the blogs entry in the rss file.
def rss_entry(blog):
    ans = "<item>"
    ans+= "<title>"+blog["Title"]+"</title>"
    ans+= "<link>"+blogFullUrl(blog)+"</link>"
    ans+= "<guid isPermaLink=\"true\">"+blogFullUrl(blog)+"</guid>"
    if "Summary" in blog:
        ans+= "<description>"+blog["Summary"]+"</description>"
    ans += "<pubDate>" + datetime.strptime(blog["Date"],"%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    ans += "</item>\n"
    return ans


