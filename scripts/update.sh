#!/bin/bash

# Just a simple script for now but as my build process becomes
# more complicated may come in handy later.

# Must run Personal_Site directory

# Push current git status to github
git push origin master
# Sync website assets to aws
aws s3 sync ../live/ s3://ja3k.com/ --delete 
