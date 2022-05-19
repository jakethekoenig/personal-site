import json
import os
from datetime import datetime
from url_tools import relative_path, file_name, permalink
from content import generate_content, generate_comments

# From a websites template and its specified data (which has a link to the content)
# create a filled out webpage.
def replaceTags(template, data, index):
    tags = { "$", "[", ":", "??" }
    # TODO: Make this method robust to tags inside tags
    # replace content
    content = generate_content(data, index)
    content_tag_loc = template.find("<[Content]>")
    if content_tag_loc != -1:
        template = template[:content_tag_loc]+content+template[content_tag_loc+11:]
    if "Commentsource" in data.keys() and data["Commentsource"] == "github":
        comments = generate_comments(data, index)
    else:
        data["Commentsource"] = "lambda"
        comments = "<:comp/commentiframe:>" # TODO: switch it around so this is what it is by default.
    comment_tag_loc = template.find("<[Comments]>")
    if comment_tag_loc != -1:
        template = template[:comment_tag_loc]+comments+template[comment_tag_loc+12:]
    # replace components
    while template.find("<:") != -1:
        start = template.find("<:")
        end   = template.find(":>")+2
        comp_path = template[start+2:end-2]
        with open(template_dir+comp_path) as c:
            comp = c.read()
        template = template[:start] + comp + template[end:]
    # replace tags
    for tag in data.keys():
        if type(data[tag]) == type(""):
            template = template.replace("<$"+tag+"$>", data[tag])
    # Delete all tags with no corresponding data
    while template.find("<$") != -1 and template.find("$>") != -1:
        start = template.find("<$")
        end   = template.find("$>")+2
        if start>end:
            break
        template = template[:start] + template[end:]

    # delete optional tags
    while template.find("<??") != -1:
        start = template.find("<??")
        mid   = template.find("???")
        end   = template.find("??>")+3
        remove = eval(template[start+3:mid])
        if remove:
            template = template[:start] + template[end:]
        else:
            template = template[:start]+template[mid+3:end-3]+template[end:]
    return template


# From the data directory create an index of the site. It'll be a list of tuples. Each with
# first parameter the name of the page or directory and second parameter another list if it
# was a directory else the associated data object. The lists will be sorted by date if one is
# present else alphabetically.
def make_index(data_dir, relative_path):
    index = []
    defaults = {}
    new_relative_path = os.path.join(relative_path,'default.json')
    default_file = os.path.join(data_dir,new_relative_path)
    if os.path.exists(default_file):
        with open(default_file) as data_file:
            defaults = json.load(data_file)
    for page in os.listdir(os.path.join(data_dir,relative_path)):
        if page=='default.json':
            continue
        if page.find("swp")!=-1: # Should probably find a better way to avoid my swap files getting in the way. Maybe this isn't necessary anymore because my swps go in my vim/?
            continue
        new_relative_path = os.path.join(relative_path,page)
        full_path = os.path.join(data_dir,new_relative_path)
        if os.path.isdir(full_path):
            index+=[(page, make_index(data_dir,new_relative_path))]
        else:
            with open(full_path) as data_file:
                data = json.load(data_file)
                # TODO: is this a good idea? How do I want this data connected up?
                data["relative_path"] = os.path.join(relative_path, file_name(data))
                data["comment_path"] = os.path.join(comment_dir, os.path.splitext(data["relative_path"])[0])
                data["permalink"] = permalink(data)
                for k,v in defaults.items():
                    if k not in data.keys():
                        data[k] = v
                index+=[(page,data)]
    index.sort(key=lambda t: datetime.strptime(t[1]["Date"] if "Date" in t[1] else "1/1/2000", "%m/%d/%Y"), reverse=True)
    return index


def make_site(target_dir, cur_path, index, global_index):
    for (path, data) in index:
        if isinstance(data, list):
            nex = os.path.join(cur_path, path)
            os.mkdir(os.path.join(target_dir,nex))
            make_site(target_dir, nex, data, index)
        else:
            make_page(os.path.join(target_dir, relative_path(data)), data, index)


def make_page(path, data, index):
    with open(template_dir + data["Template"], 'r') as f:
        temp = f.read()
    with open(path, "w") as out:
        out.write(replaceTags(temp, data, index))


# Hard Coded Locations of data, templates and content. Relative to src/
# TODO: make them not relative?
data_dir     = "data"
template_dir = "template/"
content_dir  = "content/"
comment_dir  = "comments/"
live_dir     = "../live"
index = make_index(data_dir, "")
make_site(live_dir, "", index, index)
