#!/bin/bash
echo $1
files=$(git diff --name-only HEAD^..HEAD)
count=$(git diff --name-only HEAD^..HEAD | wc -l)
status=$(git diff --name-status HEAD^..HEAD)
echo $files
echo $count
echo $status
if [ $count -gt 1 ]
then
	echo "Count not 1"
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
	gh pr merge $1
fi
