#!/bin/bash
set -e

# Just a simple script for now but as my build process becomes
# more complicated may come in handy later.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$REPO_ROOT"
LIVE="$(python3 -c 'import json; print(json.load(open("config.json"))["live"])')"
case "$LIVE" in
	/*) ;;
	*) LIVE="$REPO_ROOT/$LIVE";;
esac

# Sync website assets to aws
# aws s3 sync ../live/asset s3://ja3k.com/asset --size-only # Asset no longer kept in git. Should make a new bucket just for it.
aws s3 sync "$LIVE/css" s3://ja3k.com/css --size-only
aws s3 sync "$LIVE/js" s3://ja3k.com/js --size-only
aws s3 sync "$LIVE/" s3://ja3k.com/ --exclude "css*" --exclude "js*" --exclude "*.xml" --exclude "*.txt" --content-type "text/html" --size-only
aws s3 cp "$LIVE/" s3://ja3k.com/ --recursive --exclude "*" --include "*.xml" --include "*.txt"

# TODO: I want to make an invalidation for every file that's changed.
CHANGED_FILES="$(mktemp)"
trap 'rm -f "$CHANGED_FILES"' EXIT
git diff --name-only HEAD^..HEAD > "$CHANGED_FILES"
cat "$CHANGED_FILES"
python3 "$SCRIPT_DIR/makeinvalidations.py" "$CHANGED_FILES"
