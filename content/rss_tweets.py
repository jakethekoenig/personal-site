from datetime import datetime

def generate(data, index):
    ans = ""
    # Get tweets from the short index and sort by date (newest first)
    tweets = dict(index)["short"]
    
    # Sort tweets by date for better RSS experience
    sorted_tweets = sorted(tweets, key=lambda x: parse_date_for_sorting(x[1].get("Date", "")), reverse=True)
    
    # Limit to most recent 100 tweets to keep RSS feed manageable
    recent_tweets = sorted_tweets[:100]
    
    for (path, tweet) in recent_tweets:
        ans += rss_entry(tweet)
    return ans

def parse_date_for_sorting(date_str):
    """Parse date string for sorting purposes"""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        return datetime.min

# Returns the xml snippet which describes the tweet entry in the rss file.
def rss_entry(tweet):
    ans = "<item>"
    ans += "<title>" + tweet["Title"] + "</title>"
    ans += "<link>" + tweet["permalink"] + "</link>"
    ans += "<guid isPermaLink=\"true\">" + tweet["permalink"] + "</guid>"
    
    # Use Summary as description (consistent with other RSS feeds)
    if "Summary" in tweet:
        ans += "<description>" + tweet["Summary"] + "</description>"
    
    # Add link to original tweet if available
    if "tweet_url" in tweet:
        ans += "<comments>" + tweet["tweet_url"] + "</comments>"
    
    ans += "<pubDate>" + datetime.strptime(tweet["Date"], "%m/%d/%Y").strftime("%a, %d %b %Y %H:%M:%S %z EST") + "</pubDate>"
    ans += "</item>\n"
    return ans
