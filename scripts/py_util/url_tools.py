
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

