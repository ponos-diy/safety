
def make_unique(l: list):
    result = []
    for item in l:
        if item not in result:
            result.append(item)
    return result


