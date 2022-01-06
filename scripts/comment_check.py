import json
import datetime
import sys

sys.stderr.write("python running\n")

def fail():
    print(0)
    quit()

def safe(text):
    unsafe = ["<",">"]
    for c in unsafe:
        if c in text:
            return False
    return True

f=sys.argv[1]
sys.stderr.write(f)
if not f.startswith("comments/") or not f.endswith(".json"):
    sys.stderr.write("Not in comments dir\n")
    fail()
try:
    with open(f) as data:
        comment = json.load(data)
        required = ["Author", "Body"]
        optional = ["Page", "Date"]
        displayed = ["Author", "Body", "Date"]
        for field in required:
            if not field in comment:
                fail()
        for field in displayed:
            if field in comment and not safe(comment[field]):
                fail()
        for field in comment.keys():
            if not field in required and not field in optional:
                fail()
        if "Date" in comment:
            int(comment["Date"])
        reserved_names = ["jake", "jakekoenig", "ja3k", "jaek", "jakethekoenig"]
        if comment["Author"].lower() in reserved_names:
            fail()
        if len(comment["Body"])>5000 or len(comment["Author"])>100:
            fail()
        print(1)
except Exception as e:
    fail()

