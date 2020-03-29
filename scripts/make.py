import json
import os
from imp import find_module, load_module
from datetime import datetime
from url_tools import url

# From a websites template and its specified data (which has a link to the content)
# create a filled out webpage.
def replaceTags(template, data, index):
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
        template = template.replace("<$"+tag+"$>", data[tag])
    return template


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
    index = sorted(index, key=lambda t: datetime.strptime(t[1]["Date"],"%m/%d/%Y") if "Date" in t[1] else datetime.now())[::-1]
    # TODO: Logically this should go somewhere else. But where? I guess I somehow need to pass
    # the whole index around later?
    if len(index)>0 and "Date" in index[0][1]:
        for i,blog in enumerate(index):
            if i!=0:
                blog[1]["next"] = url(index[i-1][1])
            if i+1<len(index):
                blog[1]["previous"] = url(index[i+1][1])
    return index


def make_site(target_dir, index, global_index):
    for (path, data) in index:
        if isinstance(data, list):
            nex = target_dir+"/"+path
            os.mkdir(nex)
            make_site(nex, data, index)
        else:
            nex = target_dir+"/"+url(data)
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
make_site("../live", index, index)
