#!/usr/bin/env python
import wx
import edn_format
import datetime
import random
import shutil
import os
import sys
import gui
import website
import utils
import django


def rec_copy(src, dest):
    for f in os.listdir(src):
        srcf = src + "/" + f
        destf = dest + "/" + f
        if os.path.isdir(srcf):
            rec_copy(srcf, destf)
        else:
            if not os.path.isfile(destf):
                shutil.copyfile(srcf, destf)


played_games_file = "played-games.edn"


def readPlayedGames():
    with open(played_games_file, "r") as file:
        return edn_format.loads(file.read())


def writePlayedGames(data):
    with open(played_games_file, "w") as file:
        file.write(utils.dump_edn(data))


games_file = "games.edn"


def readGames():
    with open(games_file, "r") as file:
        return edn_format.loads(file.read())


def writeGames(data):
    with open(games_file, "w") as file:
        file.write(utils.dump_edn(data))


def generateWebsite(full_regen=False):
    if full_regen:
        if os.path.isfile("docs") or os.path.isdir("docs"):
            shutil.rmtree("docs")
        shutil.copytree("static-assets", "docs")
    else:
        rec_copy("static-assets", "docs")

    played_games = utils.unednize(readPlayedGames())
    website.sortScreenshots(
        played_games, os.listdir("static-assets/images/screenshots")
    )

    games = utils.unednize(readGames())

    files = website.renderWebsite(games, played_games, full_regen)
    for filename, content in files.items():
        with open(filename, "w") as file:
            file.write(content)


def copyScreenshots(shortname, screenshots):
    for (src, dest) in utils.mapScreenshotNames(shortname, screenshots):
        shutil.copyfile(src, dest)


def write_data(guidata):
    played_games = [dict(game) for game in readPlayedGames()]

    shortname = utils.updateLastPlayed(
        played_games, guidata, str(datetime.datetime.now().date())
    )

    games = readGames()[:]

    if len(games) == 0:
        writePlayedGames(played_games)
        mb = wx.MessageDialog(None, "Woah, challenge done?!")
        mb.ShowModal()
        quit()

    r = random.randrange(len(games))
    next_game = games[r]
    games.remove(next_game)
    next_game = dict(next_game)
    next_game[edn_format.Keyword("rating")] = edn_format.Keyword("na")
    played_games.append(next_game)

    writeGames(games)
    writePlayedGames(played_games)

    copyScreenshots(shortname, guidata["screenshots"])

    generateWebsite()
    return next_game


def mock_write_data(data):
    print(data)
    return {"name": "Test game"}


def testAllShortnames():
    played_games = readPlayedGames()
    games = readGames()
    all_shortnames = []
    generated_shortnames = []
    for g in played_games[:-1]:
        sn = utils.makeShortname(g, all_shortnames)
        all_shortnames.append(sn)
        generated_shortnames.append(
            (g[edn_format.Keyword("game")], sn, g[edn_format.Keyword("shortname")])
        )
    g = played_games[-1]
    sn = utils.makeShortname(g, all_shortnames)
    all_shortnames.append(sn)
    generated_shortnames.append((g[edn_format.Keyword("game")], sn))
    for g in games[:-1]:
        sn = utils.makeShortname(g, all_shortnames)
        all_shortnames.append(sn)
        generated_shortnames.append((g[edn_format.Keyword("game")], sn))
    return generated_shortnames


if __name__ == "__main__":
    django.conf.settings.configure()

    if len(sys.argv) >= 2 and sys.argv[1] == "-regen":
        print("Doing a full website generation")
        generateWebsite(True)
    else:
        played_games = readPlayedGames()
        if len(played_games) == 0:
            games = readGames()[:]
            r = random.randrange(len(games))
            next_game = games[r]
            games.remove(next_game)
            next_game = dict(next_game)
            next_game[edn_format.Keyword("rating")] = edn_format.Keyword("na")
            played_games = played_games[:]
            played_games.append(next_game)
            writeGames(games)
            writePlayedGames(played_games)
            print("Starting new challenge with: " + str(next_game))
            played_games = readPlayedGames()

        now_playing = played_games[-1]
        fn = write_data
        if len(sys.argv) >= 2 and sys.argv[1] == "-guitest":
            fn = mock_write_data
        gui.runGUI(now_playing, fn)
