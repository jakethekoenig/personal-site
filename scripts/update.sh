#!/bin/bash

# Just a simple script for now but as my build process becomes
# More complicated may come in handy later.

# Push current git status to github
git push origin master
# Sync website assets to aws
aws s3 sync live/ s3://ja3k.com/ --exclude "*git/*" --exclude "*scripts/*"
