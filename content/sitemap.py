def generate(data, index):
    perms = list_permalinks(index)
    perms = filter(lambda p: p.endswith('.html'), perms)
    perms = map(lambda p: p[:-5], perms)
    return "\n".join(perms)

def list_permalinks(index):
    ans = []
    if type(index) is dict:
        return [ index['permalink'] ]
    for entry in index:
        ans.extend(list_permalinks(entry[1]))
    return ans
            
