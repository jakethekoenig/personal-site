from datetime import datetime

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
    
    ans += "<pubDate>" + datetime.strptime(podcast["Date"], "%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    ans += "</item>\n"
    return ans
