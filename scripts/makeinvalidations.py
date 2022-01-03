import json
import os
import sys

with open("tmp") as changed:
    for line in changed:
        sys.stderr.write(line)
        if line.startswith("comments/") and ".json" in line:
            try:
                with open(line) as l:
                    data = json.load(l)
                    print(data)
                    if "Page" in data:
                        sys.stderr.write(data["Page"])
                        page = data["Page"]
                        if page.endswith(".html"):
                            page = page[:-5]
                        pagehtml = page + ".html"
                        os.system('aws cloudfront create-invalidation --distribution-id E3RFZ3RTME1070 --paths "%s" "%s"'%(page, pagehtml))
                        sys.stderr.write('aws cloudfront create-invalidation --distribution-id E3RFZ3RTME1070 --paths "%s" "%s"'%(page, pagehtml))
            except Exception as e:
                print(e)
                continue

