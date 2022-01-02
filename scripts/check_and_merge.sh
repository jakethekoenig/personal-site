#!/bin/bash
echo $1
echo $2
files=$(gh pr diff $1 --name-only)
count=$(gh pr diff $1 --name-only | wc -l)
status=$(gh pr diff $1 --name-status)
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
