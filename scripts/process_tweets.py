import json
import os
import argparse
import datetime
import requests
import sys

# --- Configuration ---
# Assumed Twitter username for constructing tweet URLs.
# The user can change this if their handle is different.
TWITTER_USERNAME = "jakethekoenig"

# Output directories
TWEET_DATA_DIR = os.path.join("data", "tweets")
MEDIA_ASSETS_DIR = os.path.join("assets", "crosspost")

def process_tweets(tweets_js_path):
    """
    Processes a Twitter archive's tweets.js file to extract tweets into individual
    JSON files and download associated media.
    """
    print("Starting tweet processing...")

    # --- 1. Create output directories if they don't exist ---
    os.makedirs(TWEET_DATA_DIR, exist_ok=True)
    os.makedirs(MEDIA_ASSETS_DIR, exist_ok=True)
    print(f"Output directories '{TWEET_DATA_DIR}' and '{MEDIA_ASSETS_DIR}' are ready.")

    # --- 2. Read and parse the tweets.js file ---
    try:
        with open(tweets_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{tweets_js_path}' was not found.")
        sys.exit(1)

    # The .js file is not pure JSON, it starts with an assignment. We strip it.
    json_str = content.split('=', 1)[1].strip()
    try:
        tweets_data = json.loads(json_str)
    except json.JSONDecodeError:
        print("Error: Could not parse the tweets.js file. It might not be a valid JSON format after stripping the header.")
        sys.exit(1)

    print(f"Successfully parsed {len(tweets_data)} tweets.")

    # --- 3. Process each tweet ---
    for item in tweets_data:
        tweet = item.get('tweet', {})
        tweet_id = tweet.get('id_str')
        
        if not tweet_id:
            print("Skipping an item with no tweet ID.")
            continue

        # --- 4. Extract core tweet data ---
        created_at = tweet.get('created_at')
        full_text = tweet.get('full_text')
        
        # Construct the tweet URL
        tweet_url = f"https://twitter.com/{TWITTER_USERNAME}/status/{tweet_id}"

        # --- 5. Handle media ---
        media_paths = []
        if 'entities' in tweet and 'media' in tweet['entities']:
            for media_item in tweet['entities']['media']:
                media_url = media_item.get('media_url_https')
                if media_url:
                    try:
                        response = requests.get(media_url, stream=True)
                        response.raise_for_status() # Raise an exception for bad status codes
                        
                        # Create a unique filename
                        file_name = f"{tweet_id}_{os.path.basename(media_url)}"
                        local_path = os.path.join(MEDIA_ASSETS_DIR, file_name)
                        
                        with open(local_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        # Store the relative path for use on the website
                        media_paths.append(f"/{local_path}")
                        print(f"Downloaded media for tweet {tweet_id} to {local_path}")

                    except requests.exceptions.RequestException as e:
                        print(f"Warning: Could not download media {media_url} for tweet {tweet_id}. Error: {e}")

        # --- 6. Prepare JSON output ---
        output_data = {
            "id": tweet_id,
            "created_at": created_at,
            "text": full_text,
            "url": tweet_url,
            "media": media_paths
        }

        # --- 7. Save to file ---
        output_filename = os.path.join(TWEET_DATA_DIR, f"{tweet_id}.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)

    print(f"\nProcessing complete. All tweets have been saved to '{TWEET_DATA_DIR}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a Twitter archive's tweets.js file into a JSON format for a static site."
    )
    parser.add_argument(
        "tweets_js_path",
        help="Path to the tweets.js file from your Twitter archive (e.g., 'path/to/archive/data/tweets.js')."
    )
    args = parser.parse_args()
    
    process_tweets(args.tweets_js_path)
