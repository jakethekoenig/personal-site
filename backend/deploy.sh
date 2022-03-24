#!/bin/bash

RUN_DIR=$(pwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

# Deploy lambda endpoint that catches comments
cd catchcomments
code="cloudtmp.zip" # TODO: ensure this doesn't already exist
zip $code -r *
aws lambda update-function-code --function-name arn:aws:lambda:us-east-2:472039641776:function:addComment --zip-file fileb://$code --region us-east-2
rm $code
cd ..
