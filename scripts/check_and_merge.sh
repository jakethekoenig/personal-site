#!/bin/bash
echo $1
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
file=$(gh pr view $1 --json files --jq '.files[0]["path"]')
deletions=$(gh pr view $1 --json files --jq '.files[0]["deletions"]')
if [ $deletions != "0" ]
then
	echo "Not a new file"
	exit
fi

gh pr diff $1 --color never > tmp	
valid=$(python ./scripts/comment_check.py $file)
echo $valid
if [ $valid -eq 1 ]
then
	echo "merging"
	gh pr merge $1 --merge
fi
