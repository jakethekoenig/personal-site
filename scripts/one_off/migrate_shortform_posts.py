#!/usr/bin/env python3
"""Replace legacy short-form URL fields with a single posts array."""

import argparse
import json
from pathlib import Path


LEGACY_URL_FIELDS = {
    "bluesky_thread_urls",
    "bluesky_url",
    "thread_urls",
    "tweet_url",
    "twitter_crossposts",
    "twitter_post_uris",
    "twitter_posted",
    "twitter_urls",
}
LEGACY_SOURCE_FIELDS = {"source", "source_badge", "source_name"}


def add_url(groups, index, url):
    if not url:
        return
    while len(groups) <= index:
        groups.append([])
    if url not in groups[index]:
        groups[index].append(url)


def migrated_posts(data):
    if "posts" in data:
        return [list(urls) for urls in data["posts"]]

    post_uris = data.get("post_uris", [])
    thread_urls = data.get("thread_urls", [])
    bluesky_thread_urls = data.get("bluesky_thread_urls", [])
    group_count = max(
        len(post_uris),
        len(thread_urls),
        len(bluesky_thread_urls),
        1,
    )
    groups = [[] for _ in range(group_count)]

    if data.get("source") == "bluesky":
        for index, url in enumerate(bluesky_thread_urls or thread_urls):
            add_url(groups, index, url)
    else:
        for index, url in enumerate(thread_urls):
            add_url(groups, index, url)

    add_url(groups, 0, data.get("bluesky_url"))

    uri_indexes = {uri: index for index, uri in enumerate(post_uris)}
    crossposts = sorted(
        data.get("twitter_crossposts", []),
        key=lambda item: (
            uri_indexes.get(item.get("bluesky_uri"), group_count),
            item.get("chunk_index", 0),
        ),
    )
    for crosspost in crossposts:
        index = uri_indexes.get(crosspost.get("bluesky_uri"), 0)
        add_url(groups, index, crosspost.get("tweet_url"))

    twitter_urls = data.get("twitter_urls", [])
    if not crossposts:
        if len(groups) == len(twitter_urls):
            for index, url in enumerate(twitter_urls):
                add_url(groups, index, url)
        else:
            for url in twitter_urls:
                add_url(groups, 0, url)
    add_url(groups, 0, data.get("tweet_url"))

    if any(not urls for urls in groups):
        raise ValueError(f"Cannot create a non-empty posts entry for {data.get('URL')}")
    return groups


def migrate_data(data):
    posts = migrated_posts(data)
    migrated = {}
    inserted_posts = False
    for key, value in data.items():
        if key in LEGACY_URL_FIELDS or key in LEGACY_SOURCE_FIELDS:
            continue
        migrated[key] = value
        if key == "tweet_id":
            migrated["posts"] = posts
            inserted_posts = True
    if not inserted_posts:
        migrated["posts"] = posts
    return migrated


def migrate_directory(data_dir):
    changed = 0
    for path in sorted(data_dir.glob("*.json")):
        if path.name == "default.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        migrated = migrate_data(data)
        rendered = json.dumps(migrated, indent=4, ensure_ascii=False) + "\n"
        if path.read_text(encoding="utf-8") != rendered:
            path.write_text(rendered, encoding="utf-8")
            changed += 1
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir",
        nargs="?",
        type=Path,
        default=Path("data/short"),
    )
    args = parser.parse_args()
    changed = migrate_directory(args.data_dir)
    print(f"Migrated {changed} short-form data files.")


if __name__ == "__main__":
    main()
