from url_tools import url

def blogLi(blog):
    cats = blogCategories(blog)
    if "Summary" in blog:
        ans = "<a href='blog/" + url(blog) + "' class='blogstub " + cats + "'><li><h2>"+ blog["Title"]+"</h2>"
        ans += "<p>" + blog["Summary"] + "</p>"
        ans += "</li></a>"
        return ans
    return "<a href='blog/" + url(blog) + "' class='blogstub "+cats+ "'><li><h2>"+ blog["Title"] +"</h2></li></a>"

def blogCategories(blog):
    if "Categories" in blog:
        return " ".join(blog["Categories"])
    else:
        return ""

def allCategories(index):
    cats = set()
    for blog in dict(index)["blog"]:
        blog = blog[1]
        if "Categories" in blog:
            cats = cats|set(blog["Categories"])
    return cats

def categoriesElement(index):
    cats = allCategories(index)
    ans = "<div class='category_menu'>"
    
    for cat in cats:
        ans += "<button class='filter_button " +cat + "'>"+cat+"</button>" 

    return ans + "</div>"

def generate(data, index):
    ans = "<p>"+data["Summary"]+"</p>"
    ans += categoriesElement(index)
    ans += "<ul class=\"links_menu\">"
    index = dict(index)
    for blog in dict(index)["blog"]:
        ans = ans + blogLi(blog[1])
    ans +="</ul>"
    return ans
