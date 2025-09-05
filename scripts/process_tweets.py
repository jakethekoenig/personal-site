import json
import os
import argparse
import datetime
import shutil
import sys

# Output directories
TWEET_DATA_DIR = os.path.join("data", "tweets")
MEDIA_ASSETS_DIR = os.path.join("assets", "crosspoast")

def copy_media(archive_media_path, tweet_id):
    """
    Copies a media file from the Twitter archive to the local assets directory
    if it doesn't already exist. Returns the local web path if successful.
    """
    try:
        # The filename in the archive is unique enough
        file_name = os.path.basename(archive_media_path)
        destination_path = os.path.join(MEDIA_ASSETS_DIR, file_name)

        # Skip copy if file already exists
        if os.path.exists(destination_path):
            # print(f"Media already exists for tweet {tweet_id}: {destination_path}")
            return f"/{destination_path}"

        # Ensure the source file exists before trying to copy
        if not os.path.exists(archive_media_path):
            print(f"Warning: Source media file not found for tweet {tweet_id} at {archive_media_path}")
            return None

        shutil.copy(archive_media_path, destination_path)
        print(f"Copied media for tweet {tweet_id} to {destination_path}")
        return f"/{destination_path}"

    except Exception as e:
        print(f"Warning: Could not copy media for tweet {tweet_id} from {archive_media_path}. Error: {e}")
        return None

def process_tweets(archive_path, twitter_username):
    """
    Processes a Twitter archive to extract tweets into individual JSON files
    and copy associated media from the archive.
    """
    print("Starting tweet processing...")

    # --- 1. Define paths and create output directories ---
    tweets_js_path = os.path.join(archive_path, 'data', 'tweets.js')
    archive_media_dir = os.path.join(archive_path, 'data', 'tweet_media')

    os.makedirs(TWEET_DATA_DIR, exist_ok=True)
    os.makedirs(MEDIA_ASSETS_DIR, exist_ok=True)
    print(f"Output directories '{TWEET_DATA_DIR}' and '{MEDIA_ASSETS_DIR}' are ready.")

    # --- 2. Read and parse the tweets.js file ---
    try:
        with open(tweets_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{tweets_js_path}' was not found. Make sure the provided path is the root of the Twitter archive.")
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
        tweet_url = f"https://twitter.com/{twitter_username}/status/{tweet_id}"

        # --- 5. Handle media ---
        media_paths = []
        if 'extended_entities' in tweet and 'media' in tweet['extended_entities']:
            for media_item in tweet['extended_entities']['media']:
                # The filename in the archive is like: <tweet_id>-<media_id>-<filename>
                # We can find it in the 'media_url_https' and take the basename.
                media_url = media_item.get('media_url_https')
                if media_url:
                    # The archive filename is the tweet ID plus the original filename from the URL
                    archive_filename = f"{tweet_id}-{os.path.basename(media_url)}"
                    source_media_path = os.path.join(archive_media_dir, archive_filename)
                    
                    local_media_path = copy_media(source_media_path, tweet_id)
                    if local_media_path:
                        media_paths.append(local_media_path)

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
        description="Process a Twitter archive into a JSON format for a static site."
    )
    parser.add_argument(
        "archive_path",
        help="Path to the root directory of your extracted Twitter archive."
    )
    parser.add_argument(
        "--username",
        default="jakethekoenig",
        help="Your Twitter username (handle) for constructing tweet URLs. Defaults to 'jakethekoenig'."
    )
    args = parser.parse_args()
    
    process_tweets(args.archive_path, args.username)
