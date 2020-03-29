
# TODO: make this a more comprehensive utility. Methods should somehow be able
# to dynamically figure out a relative path. Fill in utils such as "file name"
# full url and relative url.


def url(data):
    if "URL" in data:
        url = data["URL"]
    else:
        url = data["Title"].replace(" ","").replace(",","")
    if "." in url:
        return url
    else:
        return url + ".html"

def blogFullUrl(blog):
    return "http://www.ja3k.com/blog/"+url(blog)

