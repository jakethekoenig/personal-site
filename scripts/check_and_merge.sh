#!/bin/bash
echo $1
echo $2
gh pr diff $1
files=$(git diff --name-only HEAD^..HEAD)
count=$(git diff --name-only HEAD^..HEAD)
status=$(git diff --name-statu HEAD^..HEAD)
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
