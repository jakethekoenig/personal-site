#!/bin/bash

# This utility copies an html file to my s3 bucket with its
# extension stripped and Content-Type set.

stripped=${1%.html}
stripped=${stripped:2}

aws s3 cp $1 s3://ja3k.com/$stripped --content-type "text/html"
