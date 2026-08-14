from datetime import datetime
import os
import json



def wrap(t, c, a=None):
    if a:
        return '<'+t+' '+a+'>'+c+'</'+t+'>'
    else:
        return '<'+t+'>'+c+'</'+t+'>'
def build_html(comment_data):
    ans = """
    <!DOCTYPE html><html><head>
    <link href='/css/comment.css?v=1' type='text/css' rel='stylesheet'>
<script type="text/javascript"
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
    </head><body> 
    """
    for k in sorted(comment_data.keys()):
        author = wrap("span", comment_data[k]["author"], "class='author'")
        date = wrap("span", comment_data[k]["prettytime"], "class='date'")
        rendered_comment = wrap("div", author+date, "class='comment_header'")
        for line in comment_data[k]["text"].split("\n"):
            if len(line)>0:
                rendered_comment += wrap("p", line)
        rendered_comment = wrap("div", rendered_comment, 'class="comment"')
        ans += rendered_comment
    ans += "</body></html>"
    return ans

# recursively iterate over files in the current directory
for root, dirs, files in os.walk("."):
    for file in files:
        # get the full path to the file
        path = os.path.join(root, file)
        # If it's json file open and add time
        if path.endswith(".json"):
            data = None
            with open(path, "r") as f:
                data = json.load(f)
                # add the time
                for key in data:
                    data[key]["prettytime"] = datetime.fromtimestamp(float(key)).strftime("%B %d, %Y %I:%M %p PST")
            # write the file back
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            with open(path.replace("json", "html"), "w") as f:
                f.write(build_html(data))




