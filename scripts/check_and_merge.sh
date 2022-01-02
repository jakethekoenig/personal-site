#!/bin/bash

files=$(git diff origin --name-only)
count=$(git diff origin --name-only | wc -l)
status=$(git diff origin --name-status)
if [ $count -eq 1]
	exit
fi
first = ${status:0:1}
if [ $first != "A" ]
	exit
fi

valid=$(python ./scripts/comment_check.py files)
if [ $valid -eq 1 ]
	gh pr merge $1
fi
