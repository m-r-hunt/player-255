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


def generateWebsite(full_regen=False):
    if full_regen:
        if os.path.isfile("docs") or os.path.isdir("docs"):
            shutil.rmtree("docs")
        shutil.copytree("static-assets", "docs")
    else:
        rec_copy("static-assets", "docs")

    played_games = {}
    with open("played-games.edn", "r") as file:
        data = file.read()
        played_games = edn_format.loads(data)
    played_games = utils.unednize(played_games)
    website.sortScreenshots(
        played_games, os.listdir("static-assets/images/screenshots")
    )

    games = {}
    with open("games.edn", "r") as file:
        data = file.read()
        games = edn_format.loads(data)
    games = utils.unednize(games)

    files = website.functionalGenerateWebsite(games, played_games, full_regen)
    for filename, content in files.items():
        with open(filename, "w") as file:
            file.write(content)


def copyScreenshots(shortname, screenshots):
    for (src, dest) in utils.mapScreenshotNames(shortname, screenshots):
        shutil.copyfile(src, dest)


def write_data(guidata):
    played_games = {}
    with open("played-games.edn", "r") as file:
        data = file.read()
        played_games = edn_format.loads(data)
    played_games = played_games[:]
    pg = dict(played_games[-1])
    pg[edn_format.Keyword("shortname")] = guidata["shortname"]
    pg[edn_format.Keyword("rating")] = guidata["rating"]
    pg[edn_format.Keyword("status")] = edn_format.Keyword(
        guidata["status"].lower().replace(" ", "-")
    )
    if guidata["status"] == "Other" and guidata["status_note"] != "":
        pg[edn_format.Keyword("status-note")] = guidata["status_note"]
    pg[edn_format.Keyword("notes")] = guidata["notes"]
    pg[edn_format.Keyword("completion-date")] = str(datetime.datetime.now().date())
    played_games[-1] = pg

    games = {}
    with open("games.edn", "r") as file:
        data = file.read()
        games = edn_format.loads(data)
    games = games[:]

    if len(games) == 0:
        with open("played-games.edn", "w") as file:
            file.write(utils.dump_edn(played_games))
        mb = wx.MessageDialog(None, "Woah, challenge done?!")
        mb.ShowModal()
        quit()

    r = random.randrange(len(games))
    next_game = games[r]
    games.remove(next_game)
    next_game = dict(next_game)
    next_game[edn_format.Keyword("rating")] = edn_format.Keyword("na")
    played_games.append(next_game)

    with open("games.edn", "w") as file:
        file.write(utils.dump_edn(games))

    with open("played-games.edn", "w") as file:
        file.write(utils.dump_edn(played_games))

    copyScreenshots(guidata["shortname"], guidata["screenshots"])

    generateWebsite()
    return next_game


def mock_write_data(data):
    print(data)
    return {"name": "Test game"}


if __name__ == "__main__":
    django.conf.settings.configure()

    if len(sys.argv) >= 2 and sys.argv[1] == "-regen":
        print("Doing a full website generation")
        generateWebsite(True)
    else:
        played_games = {}
        with open("played-games.edn", "r") as file:
            data = file.read()
            played_games = edn_format.loads(data)
        now_playing = played_games[-1]
        all_shortnames = [
            game[edn_format.Keyword("shortname")] for game in played_games[:-1]
        ]

        app = wx.App(
            False
        )  # Create a new app, don't redirect stdout/stderr to a window.

        fn = write_data
        if len(sys.argv) >= 2 and sys.argv[1] == "-guitest":
            fn = mock_write_data

        frame = gui.P255Frame(None, now_playing, all_shortnames, fn)
        app.MainLoop()
