#!/bin/bash
set -e

# TODO: look into shellcheck

# A script for building the website

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
PYTHON=python3
if [ -x "$REPO_ROOT/venv/bin/python" ]; then
	PYTHON="$REPO_ROOT/venv/bin/python"
fi

cd "$REPO_ROOT"
LIVE="$("$PYTHON" -c 'import json; print(json.load(open("config.json"))["live"])')"
case "$LIVE" in
	/*) ;;
	*) LIVE="$REPO_ROOT/$LIVE";;
esac

INSTALLED_LOCK="$REPO_ROOT/node_modules/.package-lock.json"
MATHJAX_PAGE="$REPO_ROOT/node_modules/mathjax-node-page/bin/mjpage"
if [ ! -f "$INSTALLED_LOCK" ] || \
	[ ! -x "$MATHJAX_PAGE" ] || \
	[ "$REPO_ROOT/package.json" -nt "$INSTALLED_LOCK" ] || \
	[ "$REPO_ROOT/package-lock.json" -nt "$INSTALLED_LOCK" ]; then
	echo "Installing npm dependencies..."
	npm ci
fi

# Remove the current live directory.
mkdir -p "$LIVE"
find "$LIVE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
# Copy the nongenerated directory, the skeleton of the website, to live.
# TODO: <08-05-20, Jake> I need to add a -n here but only to assets to prevent AWS#
# From syncing everything.
cp -r "$REPO_ROOT"/nongenerated/. "$LIVE"
# Build the blogs from templates
"$PYTHON" "$SCRIPT_DIR"/make.py

find "$LIVE" -type f ! -name '*.*' -print0 | while read -d $'\0' file
do
	cp "$file" "$file.html"
done
