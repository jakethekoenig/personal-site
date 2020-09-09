import sys

file_in = sys.argv[1]
file_out = sys.argv[2]

with open(file_in) as c:
    content = c.read()

content = content.replace("[[","<auto-card>")
content = content.replace("]]","</auto-card>")

with open(file_out, "w+") as out:
    out.write(content)
