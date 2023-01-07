from imp import find_module, load_module
from my_auto_card import insert_autocard
from my_mathjax import mathjax
import json
import os
import re

def generate_content(data, index, content_dir="content/"):
    content = get_content(data, index, content_dir)
    # Post processing on the content html
    # Should there be a more stylized way to do this? Maybe the desired post processing should be listed in the blog's data dir.
    content = generate_footers(content)
    content = insert_autocard(content)
    content = mathjax(content)
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
    else:
        with open(os.path.join(content_dir, path)) as c:
            if ext==".md":
                return md2html(c.read())
            else: # raw:
                return c.read()


def wrap(t, c, a=None):
    if a:
        return '<'+t+' '+a+'>'+c+'</'+t+'>'
    else:
        return '<'+t+'>'+c+'</'+t+'>'

def replacelinks(line):
    while line.find('](') != -1:
        nex = line.find('](')
        ope = line.rfind('[', 0, nex)
        clos = line.find(')', nex)
        if clos==-1 or ope==-1:
            break
        text=line[ope+1:nex]
        link=line[nex+2:clos]
        if link[0]=='/':
            attr='href=%s'%link
        else:
            attr='href=%s target=_blank'%link
        htmllink = wrap('a', text, attr)
        line = line[:ope]+htmllink+line[clos+1:]
    return line

def replaceinlinecode(line):
    at = 0
    while line.find('`', at) != -1:
        ope = line.find('`', at)
        clos = line.find('`', ope+1)
        if clos==-1:
            break
        text=line[ope+1:clos]
        text = wrap('code', text, a='class="inline"')
        line = line[:ope]+text+line[clos+1:]
        at = ope + len(text)
    return line

def replaceInlineFeatures(line):
    line = replaceinlinecode(line)
    line = replacelinks(line)
    return line

# TODO: automatically make index
def md2html(content):
    ans = ""
    lines = content.split('\n')
    codemode=False
    list_depth = []
    for line in lines:
        if line.startswith('<') or line.startswith("[b["):
            ans+=replaceInlineFeatures(line)+'\n'
            continue
        tokens = line.split()
        if len(list_depth)>0 and (len(tokens)==0 or tokens[0] not in {'-', '*', '+'}):
            for _ in list_depth:
                ans+= '</ul>'
            list_depth = []
        if len(tokens)==0:
            continue
        depth = len(tokens[0])
        if tokens[0] == '#'*depth:
            header = line.strip()[depth:].strip()
            ans += wrap('h'+str(depth), header, a='id="'+ header.lower().replace(" ","_") +'"')
        elif tokens[0][:2] == '![':
            tokens = re.split('\[|\]|\!|\(|\)|"|\'', line)
            tokens = [t for t in tokens if len(t)>0]
            source = tokens[1].rstrip()
            alt = tokens[0]
            if len(tokens)>2:
                title = tokens[2]
            else:
                title = alt
            ans += wrap('p', '<img src="%s" alt="%s" title="%s"/>'%(source, alt, title))
        elif tokens[0] == '```':
            codemode = not codemode
            if codemode:
                ans+='<pre><code>'
            else:
                ans+='</code></pre>\n'
        elif codemode:
            ans += line+'\n'
        elif tokens[0] in {'-', '*', '+'}:
            cur_depth = len(line) - len(line.lstrip())
            if len(list_depth) == 0:
                ans+= '<ul>'
                list_depth += [cur_depth]
            elif list_depth[-1] > cur_depth:
                while list_depth[-1] > cur_depth:
                    list_depth = list_depth[:-1]
                    ans += '</ul>'
            elif list_depth[-1] < cur_depth:
                list_depth += [cur_depth]
                ans += '<ul>'
            ans+=wrap('li',replaceInlineFeatures(line.strip()[1:].strip()))+'\n'
        else:
            ans+=wrap('p',replaceInlineFeatures(line))+'\n'
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
