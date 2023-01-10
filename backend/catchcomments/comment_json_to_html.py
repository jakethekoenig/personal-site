def wrap(t, c, a=None):
    if a:
        return '<'+t+' '+a+'>'+c+'</'+t+'>'
    else:
        return '<'+t+'>'+c+'</'+t+'>'

def build_html(comment_data):
    ans = """
    <!DOCTYPE html><html><head>
    <link href='/css/comment.css' type='text/css' rel='stylesheet'>
<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
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
