import os
import requests
import scrython

#TODO: consider organizing directory by set?
def file_name(s):
    s = s.replace("'","").replace(",","").replace(" ","").replace('/','-')
    return "<$Depth$>./asset/cards/" + s.lower() + ".png"

def local_file_name(s):
    s = s.replace("'","").replace(",","").replace(" ","").replace('/','-')
    return "nongenerated/asset/cards/" + s.lower() + ".png"

def downloadCard(s):
    filename = local_file_name(s)
    if not os.path.exists(filename):
        print("downloading %s"%filename)
        card = scrython.cards.Search(q=s).data()[0]
        if 'card_faces' not in card and 'image_uris' not in card:
            print("Could not download image")
            return
        if 'card_faces' in card:
            image_uri = card['card_faces'][0]['image_uris']['normal']
        else:
            image_uri = card['image_uris']['normal']
        response = requests.get(image_uri)
        with open(filename, 'wb') as f:
            f.write(response.content)

def make_hover(name):
    downloadCard(name)
    img_file = file_name(name)
    return '<span class="hover_img"><a href="https://scryfall.com/search?q='+name+'">'+name+'<span> <img src="' + img_file + '" alt="image" height="300" /></span></a></span>'

def make_block(name):
    downloadCard(name)
    img_file = file_name(name)
    return '<div class="centered"><a class="#"><span><br> <img src="' + img_file + '" alt="image" height="300" /></span></a></div>'

def insert_autocard(text):
    while "[h[" in text:
        start = text.find("[h[")
        end = text.find("]]", start+1)
        text = text[:start] + make_hover(text[start+3:end]) + text[end+2:]
    while "[b[" in text:
        start = text.find("[b[")
        end = text.find("]]", start+1)
        text = text[:start] + make_block(text[start+3:end]) + text[end+2:]
    return text
