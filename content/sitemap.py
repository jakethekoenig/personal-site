def generate(data, index):
    perms = list_permalinks(index)
    return "\n".join(perms)

def list_permalinks(index):
    ans = []
    if type(index) is dict:
        if index.get("Hide", False):
            return []
        else:
            return [ index['permalink'] ]
    for entry in index:
        ans.extend(list_permalinks(entry[1]))
    return ans
            
