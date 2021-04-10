import sys

#TODO: consider organizing directory by set?
def file_name(s):
    s = s.replace("'","").replace(",","").replace(" ","")
    return "<$Depth$>./asset/cards/" + s.lower() + ".png"

def make_hover(name):
    img_file = file_name(name)
    return '<span class="hover_img"><a href="https://scryfall.com/search?q='+name+'">'+name+'<span> <img src="' + img_file + '" alt="image" height="300" /></span></a></span>'

def make_block(name):
    img_file = file_name(name)
    return '<div class="centered"><a class="#"><span><br> <img src="' + img_file + '" alt="image" height="300" /></span></a></div>'

def insert_autocard(text):
    while "[h[" in text:
        start = content.find("[h[")
        end = content.find("]]", start+1)
        content = content[:start] + make_hover(content[start+3:end]) + content[end+2:]
    while "[b[" in text:
        start = content.find("[b[")
        end = content.find("]]", start+1)
        content = content[:start] + make_block(content[start+3:end]) + content[end+2:]
