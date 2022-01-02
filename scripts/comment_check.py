import json
import sys

sys.stderr.write("python running\n")

def safe(text):
    unsafe = ["<",">"]
    for c in unsafe:
        if c in text:
            return False
    return True

f=sys.argv[1]
sys.stderr.write(f)
if not f.startswith("comments/"):
    sys.stderr.write("Not in comments dir\n")
    print(0)
    quit()
try:
    with open(f) as data:
        comment = json.load(data)
        sys.stderr.write(comment)
        if len(comment.keys)>2:
            print(0)
            quit()
        if not "Author" in comment or not "Body" in comment:
            print(0)
            quit()
        print(1)
except:
    sys.stderr.write("exception")
    print(0)
    quit()

