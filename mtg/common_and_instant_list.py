#!/usr/bin/env python3
import sys
import pickle

colors = ["W","U","B","R","G","","BW","RU","BG","RW","GU", "UW", "BU", "BR", "GR", "GW", "BUW", "BRU", "BGR", "GRW", "GUW"]
color_full_name = {
    "W":"White",
    "U":"Blue",
    "B":"Black",
    "R":"Red",
    "G":"Green",
    "":"Artifact",
    "BW":"White/Black",
    "RU":"Red/Blue",
    "BG":"Black/Green",
    "RW":"Red/White",
    "GU":"Green/Blue",
    "UW":"Blue/White",
    "BU":"Blue/Black",
    "BR":"Black/Red",
    "GR":"Green/Red",
    "GW":"Green/White",
    "BUW":"Blue/White/Black",
    "BRU":"Black/Red/Blue",
    "BGR":"Black/Green/Red",
    "GRW":"Green/Red/White",
    "GUW":"Green/Blue/White"
}
rarities = ["common", "uncommon", "rare", "mythic"]

def get_cards_with_prop_byR_byC(prop,cards):
    card_dict = {}
    for card in cards:
        if not prop(card):
            continue
        print(card["name"])
        color = ""
        if ("colors" not in card):
            face = card["card_faces"][0]
            color = "".join(sorted(face["colors"]))
        else:
            color = "".join(sorted(card["colors"]))
        rarity = card["rarity"]
        if rarity not in card_dict.keys():
            card_dict[rarity] = {}
        if color not in card_dict[rarity].keys():
            card_dict[rarity][color] = []
        card_dict[rarity][color].append(card['name'])
    return card_dict

def common(card):
    return card["rarity"] == "common"

def instant(card):
    print(card)
    if "card_faces" in card.keys():
        for face in card["card_faces"]:
            if instant(face):
                return True
        return False
    if "Instant" in card["type_line"]:
        return True
    if "Flash" in card["oracle_text"]:
        return True
    return False

def html_print_organized_list(card_dict):
    ans = "<h2 id='instants'>Instants</h2>"
    for rarity in rarities:
        if rarity not in card_dict.keys():
            continue
        d2 = card_dict[rarity]
        ans += "<p>%s</p>"%rarity
        ans += '<ul style="list-style-type: none;">'
        for color in colors:
            if color not in d2.keys():
                continue
            cards = d2[color]
            ans += "<li> <b>%s: </b>"%color
            ans += ", ".join(["[h[%s]]"%card for card in cards])
            ans += "</li>"
        ans += "</ul>"
    return ans

def block_list(card_dict):
    ans = "# Commons Ranking\n"
    for color in colors:
        if color not in card_dict.keys():
            continue
        ans += """
<h3 class="collapsible" id="%s_commons">%s [+]</h3>
<div class="collapsed">
"""%(color_full_name[color].lower(),color_full_name[color])
        cards = card_dict[color]
        ans += "\n".join(["[b[%s]]"%card for card in cards])
        ans += "\n"
    return ans

            
            
code = sys.argv[1]
card_list_objects = pickle.load(open("%s.pickle"%code, "rb"))

sorted_instants = get_cards_with_prop_byR_byC(instant, card_list_objects)
commons = get_cards_with_prop_byR_byC(common, card_list_objects)["common"]

print(block_list(commons))
print()
print(html_print_organized_list(sorted_instants))
