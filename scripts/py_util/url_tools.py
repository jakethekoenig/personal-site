from imp import find_module, load_module

# TODO: make this a more comprehensive utility. Methods should somehow be able
# to dynamically figure out a relative path. Fill in utils such as "file name"
# full url and relative url.
# TODO: make sense of legacy vs. normal urls. with respect to .html extension.


def url(data):
    if "URL" in data:
        url = data["URL"]
    else:
        url = data["Title"].replace(" ","").replace(",","")
    return url

def legacy_url(data):
    my_url = url(data)
    if "." in my_url:
        return my_url
    else:
        return my_url+".html"

def blogFullUrl(blog):
    return "http://www.ja3k.com/blog/"+url(blog)

# Make the content for a specified webpage
# TODO: should this be a general util file now? Or should this method be somewhere else? Maybe the index elements should have their content pregenerated?
# TODO: How should global config be handled? How should global index be handled?
def get_content(data, index, content_dir="content/"):
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
   

