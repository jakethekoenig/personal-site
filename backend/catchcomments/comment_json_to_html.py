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
