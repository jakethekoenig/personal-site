#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PR_REF="$1"

echo "$PR_REF"
commit_count=$(gh pr view "$PR_REF" --json commits --jq '. | length')
file_count=$(gh pr view "$PR_REF" --json files --jq '. | length')
if [ $file_count -gt 1 ]
then
	echo "File count not 1"
	exit
fi
if [ $commit_count -gt 1 ]
then
	echo "Commit count not 1"
	exit
fi
file=$(gh pr view "$PR_REF" --json files --jq '.files[0]["path"]')
deletions=$(gh pr view "$PR_REF" --json files --jq '.files[0]["deletions"]')
if [ $deletions != "0" ]
then
	echo "Not a new file"
	exit
fi

DIFF_FILE="$(mktemp)"
trap 'rm -f "$DIFF_FILE"' EXIT
gh pr diff "$PR_REF" --color never > "$DIFF_FILE"
valid=$(python3 "$SCRIPT_DIR/comment_check.py" "$file" "$DIFF_FILE")
echo "$valid"
if [ $valid -eq 1 ]
then
	echo "merging"
	gh pr merge "$PR_REF" --merge
fi
