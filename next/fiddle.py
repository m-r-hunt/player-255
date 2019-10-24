import edn_format

def dump_edn(l):
    out = "["
    for item in l:
        out += "{"
        for k, v in item.items():
            out += "" + edn_format.dumps(k) + " " + edn_format.dumps(v) + ",\n  "
        if out[-4:] == ",\n  ":
            out = out[:-4]
        out += "}\n "
    if out[-2:] == "\n ":
        out = out[:-2]
    out += "]\n"
    return out

lines = []
with open("list_raw.txt", "r") as file:
    lines = file.read().split("\n")
lines = lines[:-1]

i = 0
games = []
ninety_games = 0
eighty_games = 0
seventy5_games = 0
extras = 0
while i < len(lines):
    while lines[i] == "": i += 1
    game = lines[i]
    i += 1
    while lines[i] == "": i += 1
    score = int(lines[i])
    if score >= 90:
        ninety_games += 1
    elif score >= 80:
        eighty_games += 1
    elif score >= 75:
        seventy5_games += 1
    else:
        extras += 1
    i += 1
    while lines[i] == "": i += 1
    user =lines[i].strip()[6:]
    i += 1
    while lines[i] == "": i += 1
    date =lines[i].strip()
    i += 1
    print(game)
    print(i)
    games.append({edn_format.Keyword("game"): game, edn_format.Keyword("meta-rating"): score, edn_format.Keyword("meta-user"): user, edn_format.Keyword("date"): date})
print(dump_edn(games))
print(len(games))
print(extras, seventy5_games, eighty_games, ninety_games)

with open("games.edn", "w") as file:
    file.write(dump_edn(games))