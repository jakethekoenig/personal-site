from imp import find_module, load_module

# TODO: make this a more comprehensive utility. Methods should somehow be able
# to dynamically figure out a relative path. Fill in utils such as "file name"
# full url and relative url.
# TODO: make sense of legacy vs. normal urls. with respect to .html extension.


def file_name(data):
    if "URL" in data:
        url = data["URL"]
    else:
        url = data["Title"].replace(" ","").replace(",","")
    if "." not in url:
        url = url+".html"
    return url

def relative_path(data):
    return data["relative_path"]

def permalink(data):
    return "http://www.ja3k.com/"+relative_path(data)

