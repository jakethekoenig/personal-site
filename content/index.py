from url_tools import url

def blogLi(blog):
    if "Summary" in blog:
        ans = "<a href=blog/" + url(blog) + "><li><h2>"+ blog["Title"]+"</h2>"
        ans += "<p>" + blog["Summary"] + "</p>"
        ans += "</li></a>"
        return ans
    return "<a href=blog/" + url(blog) + "><li><h2>"+ blog["Title"] +"</h2></li></a>"


def generate(data, index):
    ans = "<ul class=\"links_menu\">"
    index = dict(index)
    for blog in dict(index)["blog"]:
        ans = ans + blogLi(blog[1])
    ans +="</ul>"
    return ans
