#!/bin/bash
echo $1
files=$(git diff --name-only HEAD^..HEAD)
commit_count=$(gh pr view $1 --json commits --jq '. | length')
file_count=$(gh pr view $1 --json files --jq '. | length')
status=$(git diff --name-status HEAD^..HEAD)
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
first=${status:0:1}
if [ $first != "A" ]
then
	echo "File not added"
	exit
fi

valid=$(python ./scripts/comment_check.py $files)
echo $valid
if [ $valid -eq 1 ]
then
	echo "merging"
	gh pr merge $1 --merge
fi
