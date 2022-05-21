from imp import find_module, load_module
from my_auto_card import insert_autocard
import json
import os
import re
from url_tools import relative_path, file_name


def generate_content(data, index, content_dir="content/"):
    content = get_content(data, index, content_dir)
    # Post processing on the content html
    # Should there be a more stylized way to do this? Maybe the desired post processing should be listed in the blog's data dir.
    content = generate_footers(content)
    content = insert_autocard(content)
    return content

# TODO: handle .md files as well as py and html
# TODO: seperate footer, autocard into a 'post processing' system
# Make the content for a specified webpage. If it's an html file just get it. If it's a python file run it's generate method.
# TODO: How should global config be handled? How should global index be handled?
def get_content(data, index, content_dir):
    path = data["Content"]
    ext = os.path.splitext(path)[1]
    if ext==".py":
        name = path[path.rfind("/")+1:path.rfind(".")]
        if path.rfind("/")!=-1:
            dire = content_dir + path[:path.rfind("/")]
        else:
            dire = content_dir
        fp,pathname,desc = find_module(name, [dire])
        mod = load_module(name,fp,pathname,desc)
        return mod.generate(data, index)
    elif ext==".md":
        with open(content_dir + path) as c:
            return md2html(c.read())
    else: # raw:
        with open(content_dir + path) as c:
            return c.read()


def wrap(t, c, a=None):
    if a:
        return '<'+t+' '+a+'>'+c+'</'+t+'>'
    else:
        return '<'+t+'>'+c+'</'+t+'>'

def replacelinks(line):
    at = 0
    while line.find('[', at) != -1:
        ope = line.find('[', at)
        clos = line.find(']', ope)
        if clos==-1:
            break
        if line[clos+1]=='(':
            text=line[ope+1:clos]
            clos2 = line.find(')', clos)
            link=line[clos+2:clos2]
            if link[0]=='/':
                attr='href=%s'%link
            else:
                attr='href=%s target=_blank'%link
            htmllink = wrap('a', text, attr)
            line = line[:ope]+htmllink+line[clos2+1:]
            at = ope + len(htmllink)
        else:
            at = clos
    return line
def md2html(content):
    ans = ""
    lines = content.split('\n')
    codemode=False
    for line in lines:
        tokens = line.split()
        if len(tokens)==0:
            continue
        depth = len(tokens[0])
        if tokens[0] == '#'*depth:
            ans += wrap('h'+str(depth), line.strip()[depth:].strip())
        elif tokens[0][:2] == '![':
            tokens = re.split(' |\[|\]|\!|\(|\)', line)
            tokens = [t for t in tokens if len(t)>0]
            source = tokens[1]
            alt = tokens[0]
            title = tokens[2]
            ans += wrap('p', '<img src="%s" alt="%s" title="%s"/>'%(source, alt, title))
        elif tokens[0] == '```':
            codemode = not codemode
            if codemode:
                ans+='<code>\n'
            else:
                ans+='</code>\n'
        elif codemode:
            ans += line+'<br>\n'
        else:
            ans+=wrap('p',replacelinks(line))+'\n'
    return ans


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
    # TODO: think about disabling comments in some places.
    return get_comments(data["comment_path"])

def get_comments(comment_dir, depth=0):
    comm = ""
    # TODO: make recursive
    if not os.path.isdir(comment_dir):
        try:
            os.mkdir(comment_dir)
        except:
            return ""
    if not os.path.isdir(comment_dir):
        return comm
    for f1 in os.listdir(comment_dir):
        f = os.path.join(comment_dir, f1)
        if os.path.isfile(f):
            with open(f) as c:
                comm += render_comment(f, depth)
            end = f.index('.')
            if os.path.isdir(f[:end]):
                comm += get_comments(f[:end], depth+1)
    return comm

def render_comment(f, depth):
    with open(f) as data:
        comment = json.load(data)
        rendered_comment = '<div class="comment" style="margin-left:%dpx;">'%(50*depth)
        for line in comment["Body"].split("\n"):
            rendered_comment += "<p>" + line + "</p>"
        rendered_comment += "<p>" + comment["Author"] + "</p>"
        rendered_comment += "</div>"
        return rendered_comment
