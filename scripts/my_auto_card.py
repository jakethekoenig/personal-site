import sys

file_in = sys.argv[1]
file_out = sys.argv[2]

with open(file_in) as c:
    content = c.read()

def file_name(s):
    s = s.replace("'","")
    s = s.replace(",","")
    s = s.replace(" ","_")
    return "<$Depth$>./asset/cards/khm/" + s.lower() + ".png"

def make_hover(name):
    img_file = file_name(name)
    return '<span class="hover_img"><a href="https://scryfall.com/search?q='+name+'">'+name+'<span> <img src="' + img_file + '" alt="image" height="300" /></span></a></span>'

def make_block(name):
    img_file = file_name(name)
    return '<div class="centered"><a class="#"><span><br> <img src="' + img_file + '" alt="image" height="300" /></span></a></div>'

while "[[" in content:
    start = content.find("[[")
    end = content.find("]]")
    content = content[:start] + make_hover(content[start+2:end]) + content[end+2:]

while "{{" in content:
    start = content.find("{{")
    end = content.find("}}")
    content = content[:start] + make_block(content[start+2:end]) + content[end+2:]

with open(file_out, "w+") as out:
    out.write(content)
