#!/bin/bash

# TODO: look into shellcheck

# A script for building the website

npm ci

RUN_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$RUN_DIR"

live="$RUN_DIR"/../live
# Remove the current live directory.
rm -rf "$live/*"
# Copy the nongenerated directory, the skeleton of the website, to live.
# TODO: <08-05-20, Jake> I need to add a -n here but only to assets to prevent AWS#
# From syncing everything.
cp -r "$RUN_DIR"/nongenerated/ "$live"
# Build the blogs from templates
python3 "$SCRIPT_DIR"/make.py 

find "$live" -type f ! -name '*.*' -print0 | while read -d $'\0' file
do
	cp "$file" "$file.html"
done


