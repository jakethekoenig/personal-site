import json
import html
import time
import boto3

s3 = boto3.client("s3")

# TODO: When I get a post request I want to verify it has the following attributes:
# Required:
# url: A string which is the path to the resource being commented on. Should be normalized: Should  not start with /. Suffixes ignored
# text: A string. At most 500 Characters. html.escape used to ensure safe to display.
# Optional:
# author: A string. At most 30 Characters. Also escaped. Anonymous if left blank
# Link: an e-mail, website, twitter profile, etc. At most 50 characters, escaped.

# It opens the json file of "url" name, or creates it if it does not exist, It appends an entry $timestamp: { comment: $comment, name: $name, link?: $link }


def safe_args(event):
    if len(event.keys())>10: # I may support other optional fields later. But I don't want people putting to much data in. TODO: rate limit.
        return False
    if "text" not in event.keys() or "author" not in event.keys() or "url" not in event.keys():
        print("unsafe 1")
        return False
    if len(event["text"])>3000 or len(event["author"])>50:
        print("unsafe 2")
        return False
    if not (event["url"].startswith("comments/") and event["url"].endswith(".html")):
        print("unsafe 3")
        return False
    for k,v in event.items():
        if len(v)>3000:
            return False
    return True

def send_email(comment):
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name='us-east-1')

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': ['jakethekoenig@gmail.com']
                },
            Message={
                'Body': {
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': comment,
                        },
                    },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': "New Comment on ja3k.com",
                    },
                },
            Source="jake@ja3k.com"
            )
    except Exception as e:
        print(e)


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


def lambda_handler(event, context):
    event = json.loads(event['body'])
    print(event)

    if not safe_args(event):
        print("unsafe")
        return {  'statusCode': 404  }

    # Open file
    jsonfile = event["url"][:-5] + ".json"
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

    send_email(comment["author"] + "\n wrote \n" + comment["text"])

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
