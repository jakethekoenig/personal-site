#!/bin/bash
echo $1
echo $2
gh pr diff $1
files=$(git diff --name-only origin/main origin/$1)
count=$(git diff --name-only origin/main origin/$1 | wc -l)
status=$(git diff --name-statu origin/main origin/$1s)
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
