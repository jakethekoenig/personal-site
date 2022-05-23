import json
import os
from datetime import datetime
from config import default_config as config
from content import generate_content, generate_comments

# From a websites template and its specified data (which has a link to the content)
# create a filled out webpage.
def replaceTags(template, data, index):
    tags = { "$", "[", ":", "??" }
    # TODO: Make this method robust to tags inside tags
    # replace content
    content = generate_content(data, index, config["content"])
    template = template.replace("<[Content]>", content)
    if "Commentsource" in data.keys() and data["Commentsource"] == "github":
        comments = generate_comments(data, index)
    else:
        data["Commentsource"] = "lambda"
        comments = "<:comp/commentiframe:>" # TODO: switch it around so this is what it is by default.
    template = template.replace("<[Comments]>", comments)
    # replace components
    while template.find("<:") != -1:
        start = template.find("<:")
        end   = template.find(":>")+2
        tag = template[start:end]
        comp_path = tag[2:-2]
        with open(os.path.join(config["templates"],comp_path)) as c:
            comp = c.read()
        template = template.replace(tag, comp)
    # replace tags
    for tag in data.keys():
        if type(data[tag]) == type(""):
            template = template.replace("<$"+tag+"$>", data[tag])
    # Delete all tags with no corresponding data
    while template.find("<$") != -1 and template.find("$>") != -1:
        start = template.find("<$")
        end   = template.find("$>")+2
        print("Couldn't find: %s"%template[start:end])
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

# More complicated than it should be for legacy reasons
def file_name(data):
    if "URL" in data:
        url = data["URL"]
    else:
        url = data["Title"].replace(" ","").replace(",","")
    if "." not in url:
        url = url+".html"
    return url


# From the data directory create an index of the site. It'll be a list of tuples. Each with
# first parameter the name of the page or directory and second parameter another list if it
# was a directory else the associated data object. The lists will be sorted by date if one is
# present else alphabetically.
def make_index(index_path="."):
    index = []
    defaults = {}
    default_file = os.path.join(index_path, 'default.json')
    if os.path.exists(default_file):
        with open(default_file) as data_file:
            defaults = json.load(data_file)
    for page in os.listdir(index_path):
        if page=='default.json' or  page.find("swp")!=-1:
            continue
        new_index_path = os.path.join(index_path,page)
        if os.path.isdir(new_index_path):
            index+=[(page, make_index(new_index_path))]
        else:
            with open(new_index_path) as data_file:
                data = json.load(data_file)
                data["relative_path"] = os.path.join(index_path, file_name(data))
                data["comment_path"] = os.path.join("comments/", os.path.splitext(data["relative_path"])[0])
                data["permalink"] = os.path.join(config.get("base_url", "/"), data["relative_path"])
                data1 = dict(defaults)
                data1.update(data)
                index+=[(page,data1)]
    index.sort(key=lambda t: datetime.strptime(t[1]["Date"] if "Date" in t[1] else "1/1/2000", "%m/%d/%Y"), reverse=True)
    return index


def make_site(target_dir, index, global_index, cur_path=""):
    for (path, data) in index:
        if isinstance(data, list):
            nex = os.path.join(cur_path, path)
            os.mkdir(os.path.join(target_dir,nex))
            make_site(target_dir, data, index, nex)
        else:
            make_page(os.path.join(target_dir, data["relative_path"]), data, index)


def make_page(path, data, index):
    with open(os.path.join(config["templates"], data["Template"]), 'r') as f:
        temp = f.read()
    with open(path, "w") as out:
        out.write(replaceTags(temp, data, index))


if os.path.exists("config.json"):
    with open("config.json") as f:
        config.update(json.load(f))

src_dir = os.getcwd()
os.chdir(config["pages"])
index = make_index()
os.chdir(src_dir)
make_site(config["live"], index, index)
