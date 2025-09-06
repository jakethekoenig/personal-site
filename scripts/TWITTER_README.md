# Twitter Archive Processing

This directory contains scripts to process your Twitter archive and integrate it into your personal site.

## Overview

The Twitter functionality consists of:
- **Archive Processing**: Extract tweets from Twitter archive into site-compatible format
- **Tweet Pages**: Individual pages for each tweet (similar to blog posts)
- **Tweets Index**: A single page displaying all tweets chronologically
- **Media Handling**: Automatic processing and hosting of tweet images/videos

## Quick Start

1. **Download your Twitter archive** from Twitter's settings
2. **Set up the tweets functionality**:
   ```bash
   python scripts/setup_tweets.py
   ```

3. **Process your Twitter archive**:
   ```bash
   python scripts/process_twitter_archive.py /path/to/your/twitter-archive
   ```

4. **Build your site** (using exhibit):
   ```bash
   # Your normal site build process
   ./exhibit/scripts/build_live.sh
   ```

5. **Visit `/tweets`** on your site to see all your tweets!

## Scripts

### `process_twitter_archive.py`

The main script that processes your Twitter archive.

**Usage:**
```bash
python scripts/process_twitter_archive.py <archive_path> [options]
```

**Options:**
- `--output-dir`: Directory for tweet JSON files (default: `data/tweets`)
- `--media-dir`: Directory for tweet media files (default: `nongenerated/assets/crosspoast`)

**What it does:**
- Finds and parses `tweets.js` from your Twitter archive
- Extracts tweet content, dates, and metadata
- Downloads and processes media files (images, videos)
- Creates JSON files compatible with your site's structure
- Creates markdown content files for each tweet
- Skips retweets (only processes original tweets)
- **Identifies and processes tweet threads**: Groups replies to your own tweets into threads
- **Renders threads nicely**: Displays connected tweets as a cohesive thread with visual indicators

**Example:**
```bash
python scripts/process_twitter_archive.py ~/Downloads/twitter-2023-12-01-abc123/
```

### `setup_tweets.py`

Sets up the directory structure and validates the tweets functionality.

**Usage:**
```bash
python scripts/setup_tweets.py
```

**What it does:**
- Creates necessary directories (`data/tweets`, `content/tweets`, etc.)
- Validates that all required template files exist
- Creates an example tweet if no tweets are found
- Counts existing processed tweets

## File Structure

After processing, your site will have:

```
data/tweets/           # Tweet JSON metadata files
├── 1234567890.json   # Individual tweet data
├── 1234567891.json
└── ...

content/tweets/        # Tweet markdown content
├── 1234567890.md     # Tweet content in markdown
├── 1234567891.md
└── ...

nongenerated/assets/crosspoast/  # Tweet media files
├── image1.jpg        # Tweet images
├── video1.mp4        # Tweet videos
└── ...

template/
├── tweet.temp        # Template for individual tweets
├── tweets.temp       # Template for tweets index page
└── css/tweets.css    # Styling for tweets

data/tweets.json      # Index page configuration
content/tweets.py     # Tweets page generator
```

## Tweet Data Format

### Individual Tweets

Each tweet is stored as a JSON file with this structure:

```json
{
    "Title": "Tweet preview text...",
    "Author": "Jake Koenig",
    "URL": "tweet_1234567890",
    "Template": "tweet.temp",
    "Date": "12/01/2023",
    "Content": "tweets/1234567890.md",
    "Summary": "Full tweet text",
    "Categories": ["tweets"],
    "tweet_id": "1234567890",
    "tweet_url": "https://twitter.com/ja3k_/status/1234567890",
    "original_date": "Fri Dec 01 15:30:00 +0000 2023",
    "is_thread": false,
    "media": [
        {
            "type": "photo",
            "url": "/assets/crosspoast/image.jpg",
            "original_url": "https://pbs.twimg.com/media/..."
        }
    ]
}
```

### Tweet Threads

Tweet threads are stored with additional metadata:

```json
{
    "Title": "Thread: First tweet text...",
    "Author": "Jake Koenig",
    "URL": "thread_1234567890",
    "Template": "tweet.temp",
    "Date": "12/01/2023",
    "Content": "tweets/thread_1234567890.md",
    "Summary": "Combined thread text preview...",
    "Categories": ["tweets", "threads"],
    "tweet_id": "1234567890",
    "thread_urls": [
        "https://twitter.com/ja3k_/status/1234567890",
        "https://twitter.com/ja3k_/status/1234567891"
    ],
    "original_date": "Fri Dec 01 15:30:00 +0000 2023",
    "is_thread": true,
    "thread_length": 3,
    "media": [...]
}
```

## Customization

### Styling

Edit `template/css/tweets.css` to customize the appearance of your tweets page.

### Templates

- `template/tweet.temp`: Individual tweet page layout
- `template/tweets.temp`: All tweets page layout

### Content Generation

Edit `content/tweets.py` to customize how the tweets index page is generated.

## Troubleshooting

### "Could not find tweets.js file"

Your Twitter archive might have a different structure. The script looks for:
- `data/tweets.js`
- `data/tweet.js`
- `tweets.js`
- `tweet.js`

Check your archive and adjust the script if needed.

### "No media directory found"

This is normal if your tweets don't contain images/videos. The script will still process text tweets.

### Large number of tweets

The script processes tweets in batches and shows progress every 1000 tweets. For very large archives (100k+ tweets), this may take several minutes.

### Memory usage

For very large archives, the script loads all tweets into memory. If you encounter memory issues, you may need to modify the script to process tweets in smaller batches.

## Integration with Site

The tweets functionality integrates seamlessly with your existing site:

- Uses the same JSON + markdown structure as blog posts
- Follows the same template system
- Supports comments (if enabled)
- Includes in site search and navigation
- Works with your existing build process

## Thread Handling

The script intelligently handles tweet threads:

- **Identifies threads**: Detects when you reply to your own tweets
- **Groups threads**: Combines related tweets into a single thread unit
- **Visual distinction**: Threads are displayed with special styling and thread indicators
- **Preserves order**: Tweets within threads are ordered chronologically
- **Individual links**: Each tweet in a thread maintains its original Twitter URL

### Thread Detection Logic

- Replies to other users are skipped (not included)
- Replies to your own tweets are identified as thread continuations
- Threads are grouped starting from the original tweet
- Each thread gets a unique identifier based on the first tweet

## Privacy Notes

- Only processes tweets from your own account
- Skips retweets (doesn't republish others' content)
- Skips replies to other users (respects privacy)
- Includes replies only when they're part of your own threads
- Media files are copied locally (no external dependencies)
- Original Twitter URLs are preserved for reference
