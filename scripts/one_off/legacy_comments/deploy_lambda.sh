#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../../.." && pwd )"

# Deploy lambda endpoint that catches comments
cd "$REPO_ROOT/backend/catchcomments"
code="cloudtmp.zip"
trap 'rm -f "$code"' EXIT
zip -r "$code" .
aws lambda update-function-code --function-name arn:aws:lambda:us-east-2:472039641776:function:addComment --zip-file "fileb://$code" --region us-east-2
