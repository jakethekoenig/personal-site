from url_tools import relative_path

def blogLi(blog):
    cats = blogCategories(blog)
    if "Summary" in blog:
        ans = "<a href='" + relative_path(blog) + "' class='blogstub " + cats + "'><li><h2>"+ blog["Title"]+"</h2>"
        ans += "<p>" + blog["Summary"] + "</p>"
        ans += "</li></a>"
        return ans
    return "<a href='" + relative_path(blog) + "' class='blogstub "+cats+ "'><li><h2>"+ blog["Title"] +"</h2></li></a>"

def blogCategories(blog):
    if "Categories" in blog:
        return " ".join(blog["Categories"])
    else:
        return ""

def allCategories(data, index):
    cats = set()
    for blog in dict(index)[data["Indexes"]]:
        blog = blog[1]
        if "Categories" in blog:
            cats = cats|set(blog["Categories"])
    return cats

def categoriesElement(data, index):
    cats = allCategories(data, index)
    ans = "<div class='category_menu'>"
    
    for cat in cats:
        ans += "<button class='filter_button " +cat + "'>"+cat+"</button>" 

    return ans + "</div>"

def generate(data, index):
    ans = "<p>"+data["Summary"]+"</p>"
    ans += categoriesElement(data, index)
    ans += "<ul class=\"links_menu\">"
    index = dict(index)
    for blog in dict(index)[data["Indexes"]]:
        ans = ans + blogLi(blog[1])
    ans +="</ul>"
    return ans
