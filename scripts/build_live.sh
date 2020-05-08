#!/bin/bash

# A script for building the website

# Remove the current live directory.
rm -rf ../live
# Copy the nongenerated directory, the skeleton of the website, to live.
# TODO: <08-05-20, Jake> I need to add a -n here but only to assets to prevent AWS#
# From syncing everything.
cp -r ./nongenerated/ ../live
# Build the blogs from templates
python3 ./scripts/make.py 
