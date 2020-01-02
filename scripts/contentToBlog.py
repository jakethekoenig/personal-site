import json
import os
import sys
from datetime import datetime

def replaceTags(line, tags):
    for tag in tags.keys():
        line = line.replace("<$"+tag+"$>", tags[tag])
    return line

def getContent(line, tags):
    if line.find("<[") != -1:
        return line[line.find("<[")+2:line.find("]>")]
    return ""

def titleToUrl(title):
    return "blog/"+title.replace(" ","").replace(",","")+".html"

def lookUp(index, blog):
    for i,b in enumerate(index):
        if b[0]==blog:
            return i
    return -1

def derivedTags(line, index, blog):
    ind = lookUp(index,blog)
    while line.find("<:")!=-1:
        derived = line[line.find("<:")+2:line.find(":>")]
        if derived == "prev":
            if ind +1 == len(index):
                insert = "../index.html"
            else:
                insert = "../"+titleToUrl(index[ind+1][0])
        if derived == "nex":
            if ind == 0:
                insert = "../index.html"
            else:
                insert = "../"+titleToUrl(index[ind-1][0])
        line = line[:line.find("<:")] + insert + line[line.find(":>")+2:]
    return line

# Takes a file path to my own ad hoc file format
# and makes a bespoke html page for my personal
# website. 
def process(post_path, index):
    with open(post_path) as post_json:
        data = json.load(post_json)
        template = data["Template"]
        content  = data["Content"]
        out = open("../live/"+titleToUrl(data["Title"]),"w+")
        with open(template) as temp:
            with open(content) as cont:
                for line in temp:
                    line = replaceTags(line, data)
                    line = derivedTags(line, index, data["Title"])
                    content = getContent(line,data)
                    if len(content)>0:
                        with open(data[content]) as cont:
                           for line in cont:
                               out.write(line)
                    else:
                        out.write(line)
    out.close()
                    

def blogLi(blog):
    return "<a href=" + titleToUrl(blog[0]) + "><li>"+ blog[0] +"</li>"

# Make a html document from index.temp filling in titles of all my blogs
# in order of date given in their json metadata. Complete with links to them.
# Returns a list of blogs in chronological order.
def make_index(blog_dir):
    blogs = []
    for blog in os.listdir(blog_dir):
        if blog.find("swp") != -1:
            continue
        with open(blog_dir+"/"+blog) as post_json:
            data = json.load(post_json)
            blogs.append((data["Title"],datetime.strptime(data["Date"],"%m/%d/%Y")))
    blogs.sort(key= lambda x : x[1])
    blogs.reverse()
    out = open("../live/index.html", "w")
    with open("templates/index.temp") as temp:
        for line in temp:
            if line.find("<:")!=-1:
                for blog in blogs:
                    out.write(blogLi((blog)))
            else:
                out.write(line)
    out.close()
    return blogs


def make_blogs(blog_dir,index):
    blogs = []
    for blog in os.listdir(blog_dir):
        if blog.find("swp") != -1:
            continue
        process(blog_dir+"/"+blog, index)

blog_dir = sys.argv[1]
os.mkdir("../live/blog")
index = make_index(blog_dir)
make_blogs(blog_dir, index)
