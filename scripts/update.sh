#!/bin/bash

# Just a simple script for now but as my build process becomes
# more complicated may come in handy later.

AT=$(pwd)
live=~/personal-site/live
scripts=~/personal-site/src/scripts

cd $live

# Sync website assets to aws
aws s3 sync ../live/asset s3://ja3k.com/asset --size-only
aws s3 sync ../live/css s3://ja3k.com/css --size-only
aws s3 sync ../live/js s3://ja3k.com/js --size-only
aws s3 sync ../live/ s3://ja3k.com/ --exclude "asset*" --exclude "css*" --exclude "js*" --content-type "text/html" --size-only


cd $AT
