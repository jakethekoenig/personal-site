from imp import find_module, load_module
from my_auto_card import insert_autocard
import json
import os


def generate_content(data, index, content_dir="content/"):
    content = get_content(data, index, content_dir)
    # Post processing on the content html
    # Should there be a more stylized way to do this? Maybe the desired post processing should be listed in the blog's data dir.
    content = generate_footers(content)
    content = insert_autocard(content)
    return content

# Make the content for a specified webpage. If it's an html file just get it. If it's a python file run it's generate method.
# TODO: How should global config be handled? How should global index be handled?
def get_content(data, index, content_dir):
    path = data["Content"]
    if path[-3:]==".py":
        name = path[path.rfind("/")+1:path.rfind(".")]
        if path.rfind("/")!=-1:
            dire = content_dir + path[:path.rfind("/")]
        else:
            dire = content_dir
        fp,pathname,desc = find_module(name, [dire])
        mod = load_module(name,fp,pathname,desc)
        return mod.generate(data, index)
    else:
        with open(content_dir + path) as c:
            return c.read()


# Find tags of form [[content]] and put the content on the bottom with hyperlinks
# TODO: should this be in its own post processing file?
def generate_footers(content):
    i = 1
    if "[[" in content:
        content += "<div style='border-bottom:1px Black solid;'></div>"
    while "[[" in content:
        start = content.find("[[")
        end = content.find("]]", start+1)
        footer = content[start+2:end]
        content = content[:start] + "<a id='anchor_%d' href='#footer_%d'>[%d]</a>"%(i,i,i) + content[end+2:] + "<p><a id='footer_%d' href='#anchor_%d'>[%d]</a> %s</p>"%(i,i,i,footer)
        i+=1
    return content

def generate_comments(data, index, comment_dir="comments/"):
    if "Comments" in data:
        return get_comments(comment_dir+data["Comments"])
    return ""

def get_comments(comment_dir, depth=0):
    comm = ""
    for f1 in os.listdir(comment_dir):
        f = os.path.join(comment_dir, f1)
        if os.path.isfile(f):
            with open(f) as c:
                comm += render_comment(f, depth)
            if os.path.isdir(f[:-5]):
                comm += get_comments(f[:-5], depth+1)
    return comm

def render_comment(f, depth):
    with open(f) as data:
        comment = json.load(data)
        rendered_comment = '<div class="comment" style="margin-left:%dpx;">'%(50*depth)
        rendered_comment += "<p>" + comment["Body"] + "</p>"
        rendered_comment += "<p>" + comment["Author"] + "</p>"
        rendered_comment += "</div>"
        return rendered_comment
