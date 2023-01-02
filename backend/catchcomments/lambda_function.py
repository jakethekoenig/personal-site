import json
import html
import time
import boto3

s3 = boto3.client("s3")
cf = boto3.client("cloudfront")

# The bucket holding comments
# TODO: use environment variable
site = "ja3k.com"

# UTILITIES
# TODO: split utils, and the distinct paths into different files
def send_email(body, subject):
    client = boto3.client('ses',region_name='us-east-1')
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': ['jakethekoenig@gmail.com']
                },
            Message={
                'Body': {
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body,
                        },
                    },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                    },
                },
            Source="jake@ja3k.com"
            )
    except Exception as e:
        print(e)


# COMMENT CODE
# A comment add request has the following fields:
# Required:
# url: The relative path to the commtned on resource. Should not start with /.
# Suffixes ignored.
# text: The comment text. At most 3000 Characters. html.escape used to ensure
# safe to display.
# Optional:
# author: At most 30 Characters. Also escaped. Anonymous if left blank
# Link: an e-mail, website, twitter profile, etc. At most 50 characters,
# escaped.
def valid_comment_params(event):
    if len(event.keys())>10:
        return False
    if "text" not in event.keys() or "author" not in event.keys() or "url" not in event.keys():
        return False
    if len(event["text"])>3000 or len(event["author"])>50:
        return False
    if not (event["url"].startswith("comments/") and event["url"].endswith(".html")):
        return False
    for k,v in event.items():
        if len(v)>3000:
            return False
    return True

def build_html(json):
    ans = ""
    for k in sorted(json.keys()):
        rendered_comment = '<div class="comment">'
        for line in json[k]["text"].split("\n"):
            rendered_comment += "<p>" + line + "</p>"
        rendered_comment += "<p>" + json[k]["author"] + "</p>"
        rendered_comment += "</div>"
        ans += rendered_comment
    ans = "<!DOCTYPE html><html><head><link href='/css/comment.css' type='text/css' rel='stylesheet'></head><body>" + ans + "</body></html>"
    return ans

def handle_addcomment(event):
    if not valid_comment_params(event):
        print("Invalid comment params")
        return {  'statusCode': 404  }
    # Open file
    jsonfile = event["url"][:-5] + ".json"
    if "?" in jsonfile:
        jsonfile = jsonfile[:jsonfile.index("?")]
    try:
        comments = json.loads(s3.get_object(Bucket=site, Key=jsonfile)['Body'].read().decode("utf-8"))
    except Exception as e:
        comments = {}
    print(comments)
    # Append Comment
    comment = {
            "text": html.escape(event["text"]),
            "author": html.escape(event["author"])
            }
    comments[str(time.time())] = comment
    if "link" in event.keys():
        comments[str(time.time())]["link"] = html.escape(event["link"])
    send_email(comment["author"] + "wrote: " + comment["text"], "New Comment on ja3k.com")
    # Write comment file
    s3.put_object(Body=json.dumps(comments).encode("utf-8"), Bucket=site, Key=jsonfile)
    # Write html
    htm = build_html(comments)
    htmf = event["url"]
    print(htmf)
    s3.put_object(Body=htm.encode("utf-8"), Bucket=site, Key=htmf, ContentType='text/html')
    # Invalidate cache
    cf.create_invalidation(
            DistributionId='E3RFZ3RTME1070',
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': [
                        "/" + htmf
                    ]
                },
                'CallerReference': str(time.time()).replace(".","")
            })
    return {
        'statusCode': 200
    }


# SUBSCRIPTION CODE
# A subscription add request only requires an e-mail address.
def valid_subscribe_params(event):
    if len(event.keys())>10:
        return False
    if "email" not in event.keys():
        return False
    for k,v in event.items():
        if len(v)>300:
            return False
    return True

def handle_newsletter_subscribe(event):
    if not valid_subscribe_params(event):
        print('Invalid subscribe params')
        return {  'statusCode': 404  }
    send_email("New Newsletter Subscriber: %s"%event["email"], event["email"])
    return {
        'statusCode': 200
    }

###############################################################################
# Lambda Handler
#
# My website has one lambda to handle all backend requests. At the moment there
# are N types of requests:
# * addcomment
# * newsletter_subscribe
#
# These and future events are distinguished by the "type" field in the json
# body of the request. addcomment is the default if the field is not present.
###############################################################################
def lambda_handler(event, context):
    event = json.loads(event['body'])
    print(event)
    if "type" not in event.keys() or event["type"] == "addcomment":
        return handle_addcomment(event)
    elif event["type"] == "newsletter_subscribe":
        return handle_newsletter_subscribe(event)
