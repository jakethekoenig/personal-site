#!/bin/bash

# Just a simple script for now but as my build process becomes
# more complicated may come in handy later.

AT=$(pwd)
live=~/personal-site/live
scripts=~/personal-site/src/scripts

cd $live

# Sync website assets to aws
aws s3 sync ../live/ s3://ja3k.com/

# Produce html stripped of ending with correct content-type
find . -name '*.html' -exec $scripts/nicecopy.sh {}  \;


cd $AT
