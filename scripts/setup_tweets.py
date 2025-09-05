#!/usr/bin/env python3
"""
Setup script to prepare the tweets functionality after processing Twitter archive.

This script:
1. Creates the necessary directory structure
2. Sets up default files if they don't exist
3. Validates the tweets data structure

Usage: python setup_tweets.py
"""

import os
import json

def create_directory_structure():
    """Create necessary directories for tweets functionality"""
    directories = [
        "data/tweets",
        "content/tweets", 
        "nongenerated/assets/crosspoast",
        "comments/tweets"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def create_default_tweet_data():
    """Create a default tweet data file if no tweets exist"""
    tweets_dir = "data/tweets"
    
    if not os.path.exists(tweets_dir) or not os.listdir(tweets_dir):
        print("No tweets found. Creating example tweet...")
        
        # Create example tweet
        example_tweet = {
            "Title": "Welcome to my tweets archive!",
            "Author": "Jake Koenig",
            "URL": "tweet_example",
            "Template": "tweet.temp",
            "Date": "09/05/2025",
            "Content": "tweets/example.md",
            "Summary": "This is an example tweet to show how the tweets page works.",
            "Categories": ["tweets"],
            "tweet_id": "example",
            "tweet_url": "https://twitter.com/ja3k_/status/example",
            "original_date": "Thu Sep 05 16:00:00 +0000 2025",
            "media": []
        }
        
        # Save example tweet JSON
        with open(os.path.join(tweets_dir, "example.json"), 'w') as f:
            json.dump(example_tweet, f, indent=4)
        
        # Create example tweet content
        os.makedirs("content/tweets", exist_ok=True)
        with open("content/tweets/example.md", 'w') as f:
            f.write("This is an example tweet to show how the tweets page works.\n\n")
            f.write("Run the Twitter archive processing script to populate this with your real tweets!\n\n")
            f.write("[View original tweet](https://twitter.com/ja3k_/status/example)\n")
        
        print("Created example tweet")

def validate_tweets_structure():
    """Validate that the tweets structure is correct"""
    required_files = [
        "data/tweets.json",
        "content/tweets.py",
        "template/tweet.temp",
        "template/tweets.temp",
        "template/css/tweets.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Warning: Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("All required files are present!")
        return True

def count_tweets():
    """Count how many tweets have been processed"""
    tweets_dir = "data/tweets"
    if os.path.exists(tweets_dir):
        tweet_files = [f for f in os.listdir(tweets_dir) if f.endswith('.json')]
        print(f"Found {len(tweet_files)} processed tweets")
        return len(tweet_files)
    return 0

def main():
    print("Setting up tweets functionality...")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    print()
    
    # Validate structure
    validate_tweets_structure()
    print()
    
    # Count existing tweets
    tweet_count = count_tweets()
    print()
    
    # Create default data if needed
    if tweet_count == 0:
        create_default_tweet_data()
        print()
    
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Run: python scripts/process_twitter_archive.py <path_to_twitter_archive>")
    print("2. Build your site with exhibit")
    print("3. Your tweets will be available at /tweets")

if __name__ == "__main__":
    main()
