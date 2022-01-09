#!/bin/bash
echo $1

echo "merging"
gh pr merge $1 --merge
