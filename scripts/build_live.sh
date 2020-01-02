#!/bin/bash

# A script for building the website

# Remove the current live directory.
rm -rf ../live
# Copy the nongenerated directory, the skeleton of the website, to live.
cp -r ./nongenerated/ ../live
# Build the blogs from templates
python3 ./scripts/contentToBlog.py blogs/
