from url_tools import url, get_content

def entry_comp(entry, index):
    cats = entryCategories(entry)
    ans = "<div>"
    ans += "<p>" + "<a href='read/"+url(entry)+"'>" + entry["Date"]+"</a>: " + entry["Title"] + "</p>" # TODO: make title a link to a standalone page? Work out best css classes.
    ans += "<div>" + get_content(entry, index) + "</div>"
    return ans + "</div>"

def entryCategories(entry):
    if "Categories" in entry:
        return " ".join(entry["Categories"])
    else:
        return ""

def allCategories(data, index):
    cats = set()
    for entry in dict(index)[data["Indexes"]]:
        entry = entry[1]
        if "Categories" in entry:
            cats = cats|set(entry["Categories"])
    return cats

def categoriesElement(data, index):
    cats = allCategories(data, index)
    ans = "<div class='category_menu'>"
    
    for cat in cats:
        ans += "<button class='filter_button " +cat + "'>"+cat+"</button>" 

    return ans + "</div>"

def generate(data, index):
    ans = data["Summary"]
    ans += categoriesElement(data, index)
    ans += "<ul class=\"reading_list\">"
    index = dict(index)
    for entry in dict(index)[data["Indexes"]]:
        ans = ans + entry_comp(entry[1], index)
    ans +="</ul>"
    return ans
