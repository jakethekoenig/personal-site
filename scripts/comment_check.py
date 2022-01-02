import json
import system

def safe(text):
    unsafe = ["<",">"]
    for c in unsafe:
        if c in text:
            return False
    return True

f=system.argv[1]
if "comments/" != f[:len("comments/")]:
    print(0)
    quit()
try:
    comment = json.load(f)
    if len(comment.keys)>2:
        print(0)
        quit()
    if not "Author" in comment or not "Body" in comment:
        print(0)
        quit()
    print(1)
except e:
    print(0)
    quit()

