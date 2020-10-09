import json
import os
from imp import find_module, load_module
from datetime import datetime
from url_tools import url, legacy_url

# From a websites template and its specified data (which has a link to the content)
# create a filled out webpage.
def replaceTags(template, data, index):
    # TODO: Make this method robust to tags inside tags
    # replace content
    path = data["Content"]
    if path[-3:]==".py":
        name = path[path.rfind("/")+1:path.rfind(".")]
        if path.rfind("/")!=-1:
            dire = content_dir + path[:path.rfind("/")]
        else:
            dire = content_dir
        fp,pathname,desc = find_module(name, [dire])
        mod = load_module(name,fp,pathname,desc)
        content = mod.generate(data, index)
    else:
        with open(content_dir + path) as c:
            content = c.read()
    template = template[:template.find("<[")]+content+template[template.find("]>")+2:]
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


# There are some features of files in the index which are implicit in their relative position
# in the index so not manually added to the files. They are added in this method.
# The current list of such attributes is:
# * depth:     a string which gives a relative path to the top level i.e. "../../"
# * next:      the next file. Chronologically if 'Date' is present else alphabetically.
# * previous:  the previous file. Chronologically if 'Date' is present else alphabetically.
# * index:     If there is a file with attribute "indexes" then the files in the directory
#              pointed to have their attribute "index" filled in with a back reference. Then
#              index is updated to be the actual list of files instead of a pointer.
# TODO: Should the url bookkeeping be done here?
def addDerivedAttributes(index, depth=0):
    sortByDate = False
    for entry in index:
        data = entry[1]
        if isinstance(data, list):
            continue
        if "Date" in data:
            sortByDate = True
        if "Indexes" in data:
            for item in dict(index)[data["Indexes"]]: #TODO: handle case where index isn't one level up from files.
                item[1]["Index"] = "../"*(depth+1)+url(data)
        data["Depth"] = "../"*depth
    if sortByDate: #TODO: are there other cases where content should be sorted?
        index.sort(key=lambda t: datetime.strptime(t[1]["Date"], "%m/%d/%Y"), reverse=True)
    if len(index)>0 and "Index" in index[0][1]:
        for i,blog in enumerate(index):
            if i!=0:
                blog[1]["next"] = url(index[i-1][1])
            else:
                blog[1]["next"] = blog[1]["Index"]
            if i+1<len(index):
                blog[1]["previous"] = url(index[i+1][1])
            else:
                blog[1]["previous"] = blog[1]["Index"]
    for entry in index:
        if isinstance(entry[1], list):
            addDerivedAttributes(entry[1], depth+1)
    

# From the data directory create an index of the cite. It'll be a list of tuples. Each with
# first parameter the name of the page or directory and second parameter another list if it
# was a directory else the associated data object. The lists will be sorted by date if one is
# present else alphabetically.
def make_index(data_dir):
    index = []
    for page in os.listdir(data_dir):
        if page.find("swp")!=-1:
            continue
        path = data_dir+"/"+page
        if os.path.isdir(path):
            index+=[(page, make_index(path))]
        else:
            with open(path) as data_file:
                index+=[(page,json.load(data_file))]
    return index


def make_site(target_dir, index, global_index):
    for (path, data) in index:
        if isinstance(data, list):
            nex = target_dir+"/"+path
            os.mkdir(nex)
            make_site(nex, data, index)
        else:
            nex = target_dir+"/"+legacy_url(data)
            make_page(nex, data, index)


def make_page(path, data, index):
    with open(template_dir + data["Template"], 'r') as f:
        temp = f.read()
    with open(path, "w+") as out:
        out.write(replaceTags(temp, data, index))


# Hard Coded Locations of data, templates and content. Relative to src/
data_dir     = "data/"
template_dir = "template/"
content_dir  = "content/"
live_dir     = "../live/"
index = make_index(data_dir)
addDerivedAttributes(index)
make_site("../live", index, index)
