#!/bin/bash
files=$(git diff --name-only HEAD^..HEAD)
count=$(git diff --name-only HEAD^..HEAD)
status=$(git diff --name-statu HEAD^..HEAD)
echo $files
echo $count
echo $status
if [ $count -eq 1 ]
then
	exit
fi
first=${status:0:1}
if [ $first != "A" ]
then
	exit
fi

valid=$(python ./scripts/comment_check.py files)
if [ $valid -eq 1 ]
then
	gh pr merge $1
fi
