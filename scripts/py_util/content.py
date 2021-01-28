from imp import find_module, load_module


def generate_content(data, index, content_dir="content/"):
    content = get_content(data, index, content_dir)
    # Post processing on the content html
    content = generate_footers(content)
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
def generate_footers(content):
    i = 1
    if "[[" in content:
        content += "<div style='border-bottom:1px Black solid;'></div>"
    while "[[" in content:
        start = content.find("[[")
        end = content.find("]]")
        footer = content[start+2:end]
        content = content[:start] + "<a id='anchor_%d' href='#footer_%d'>[%d]</a>"%(i,i,i) + content[end+2:] + "<p><a id='footer_%d' href='#anchor_%d'>[%d]</a> %s</p>"%(i,i,i,footer)
        i+=1
    return content
