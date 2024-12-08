import json
def addpurchasetojson(purchase, jsonfile):
    print(purchase)
    with open(jsonfile, "r") as file:
        buff = json.load(file)
    buff['history'].append(purchase)
    with open(jsonfile, "w") as file:
        json.dump(buff, file, indent = 4)

def recalg(userfile, recipefile, favfile):
    with open(userfile, "r") as file:
        items = json.load(file)
    with open(recipefile, "r") as file:
        recipes = json.load(file)
    for item in items['history']:
        if not item:
            continue
        for recipe in recipes['recipes']:
            if item['name'] in recipe['ingredients']:
                recipe['popularity'] += item['quantity']

    recipe1 = recipes['recipes'][0]
    recipe2 = recipes['recipes'][1]
    recipe3 = recipes['recipes'][2]

    for recipe in recipes['recipes']:
        if recipe['popularity'] > recipe1['popularity']:
            recipe3 = recipe2
            recipe2 = recipe1
            recipe1 = recipe
        elif recipe['popularity'] > recipe2['popularity']:
            recipe3 = recipe2
            recipe2 = recipe
        elif recipe['popularity'] > recipe3['popularity']:
            recipe3 = recipe
    with open(recipefile, "w") as file:
        json.dump(recipes, file, indent = 4)
    with open(favfile, "w") as file:
        json.dump({"recipes": [recipe1, recipe2, recipe3]}, file, indent = 4)