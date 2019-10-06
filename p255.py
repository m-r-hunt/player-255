#!/usr/bin/env python
import wx
import django.template
import wx.lib.mixins.listctrl
import edn_format
import datetime
import random
import shutil
import os


def rec_copy(src, dest):
    for f in os.listdir(src):
        srcf = src + "/" + f
        destf = dest + "/" + f
        if os.path.isdir(srcf):
            rec_copy(srcf, destf)
        else:
            if not os.path.isfile(destf):
                shutil.copyfile(srcf, destf)


def unednize(l):
    out = []
    for item in l:
        d = {}
        for key, value in item.items():
            d[key.name.replace("-", "_")] = value
        out.append(d)
    return out


# Not at all general purpose, only formats [{}, {}, ...] correctly.
# Mostly matches clojure edn pretty printing in this one case, for good compatibility/diffs.
def dump_edn(l):
    out = "["
    for item in l:
        out += "{"
        for k, v in item.items():
            out += "" + edn_format.dumps(k) + " " + edn_format.dumps(v) + ",\n  "
        out = out[0:-4] + "}\n "
    out = out[0:-2] + "]\n"
    return out


def generateWebsite():
    # shutil.rmtree("docs")
    # shutil.copytree("static-assets", "docs")
    rec_copy("static-assets", "docs")

    played_games = {}
    with open("played-games.edn", "r") as file:
        data = file.read()
        played_games = edn_format.loads(data)
    played_games = unednize(played_games)

    games = {}
    with open("games.edn", "r") as file:
        data = file.read()
        games = edn_format.loads(data)
    games = unednize(games)

    engine = django.template.Engine(["resources"], builtins=["filters"])
    template = engine.get_template("templates/lists.html")
    context = django.template.Context(
        {"remaining_games": games, "played_games": played_games}
    )
    with open("docs/lists.html", "w") as file:
        file.write(template.render(context))

    game_template = engine.get_template("templates/game-page.html")

    game = dict(played_games[0])
    shortname = game.get("shortname", False)
    screenshots = []
    for f in os.listdir("static-assets/images/screenshots"):
        if shortname in f.split("-"):
            screenshots.append(f)
    game["screenshots"] = screenshots
    game["next"] = played_games[1]["shortname"]
    context = django.template.Context(game)
    with open("docs/" + shortname + ".html", "w") as file:
        file.write(game_template.render(context))

    for i in range(1, len(played_games) - 2):
        game = dict(played_games[i])
        shortname = game["shortname"]
        screenshots = []
        for f in os.listdir("static-assets/images/screenshots"):
            if shortname in f.split("-"):
                screenshots.append(f)
        game["screenshots"] = screenshots
        game["prev"] = played_games[i - 1]["shortname"]
        game["next"] = played_games[i + 1]["shortname"]
        context = django.template.Context(game)
        with open("docs/" + shortname + ".html", "w") as file:
            file.write(game_template.render(context))

    game = dict(played_games[len(played_games) - 2])
    shortname = game["shortname"]
    screenshots = []
    for f in os.listdir("static-assets/images/screenshots"):
        if shortname in f.split("-"):
            screenshots.append(f)
    game["screenshots"] = screenshots
    game["prev"] = played_games[len(played_games) - 3]["shortname"]
    context = django.template.Context(game)
    with open("docs/" + shortname + ".html", "w") as file:
        file.write(game_template.render(context))

    context = django.template.Context({})
    template = engine.get_template("templates/about.html")
    with open("docs/about.html", "w") as file:
        file.write(template.render(context))

    count = len(played_games) - 1
    percent = int(count / 255 * 100)
    recent = played_games[-11:-1]
    recent.reverse()
    context = django.template.Context(
        {
            "recent_games": recent,
            "next_up": played_games[-1],
            "count": count,
            "percent": percent,
        }
    )
    template = engine.get_template("templates/index.html")
    with open("docs/index.html", "w") as file:
        file.write(template.render(context))


def copyScreenshots(shortname, screenshots):
    for (path, title) in screenshots:
        shutil.copyfile(
            path,
            "static-assets/images/screenshots/"
            + shortname
            + "-"
            + title
            + "."
            + path.split(".")[-1].lower(),
        )


class FileDropper(wx.FileDropTarget):
    def __init__(self, list):
        wx.FileDropTarget.__init__(self)
        self.list = list

    def OnDropFiles(self, x, y, filenames):
        for file in sorted(filenames):
            title = ""
            if self.list.GetItemCount() == 0:
                title = "title"
            elif self.list.GetItemCount() == 1:
                title = "gameplay"
            elif self.list.GetItemCount() == 2:
                title = "credits"
            self.list.Append([file, title])
        return True


class ScreenshotList(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, size=(250, 100), style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.TextEditMixin.__init__(self)

        self.AppendColumn("File")
        self.AppendColumn("Title")
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnUpdate)
        self.SetDropTarget(FileDropper(self))

    def OnUpdate(self, event):
        self.SetItem(event.GetIndex(), event.GetColumn(), event.GetLabel())


class P255Frame(wx.Frame):
    def __init__(self, parent, now_playing):
        wx.Frame.__init__(self, parent, title="Player 255", size=(500, 800))
        panel = wx.Panel(self)
        self.grid = wx.FlexGridSizer(2, 10, 10)
        self.grid.AddGrowableCol(0)

        self.now_playing = wx.StaticText(panel, label=str(now_playing))
        self.now_playing.Wrap(250)
        self.AddLabelledControl(panel, "Now Playing", self.now_playing)

        self.shortname = wx.TextCtrl(panel)
        self.AddLabelledControl(panel, "Shortname", self.shortname)

        self.choice_list = ["Complete", "Not Complete", "Other"]
        self.choice = wx.Choice(panel, choices=self.choice_list)
        self.choice.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, self.choice)
        self.AddLabelledControl(panel, "Status", self.choice)

        self.status_note_box = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE, size=(250, 100)
        )
        self.status_note_box.Disable()
        self.AddLabelledControl(panel, "Status Note", self.status_note_box)

        rating_panel = wx.Panel(panel)
        self.rating_buttons = []
        box = wx.GridSizer(5, 0, 10)
        for i in range(0, 5):
            style = 0
            if i == 0:
                style = wx.RB_GROUP
            b = wx.RadioButton(rating_panel, style=style)
            box.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
            self.rating_buttons.append(b)
        for i in range(1, 6):
            box.Add(
                wx.StaticText(rating_panel, label="*" * i),
                0,
                wx.ALIGN_CENTER_HORIZONTAL,
                wx.ALIGN_TOP,
            )
        rating_panel.SetSizer(box)
        self.AddLabelledControl(panel, "Rating", rating_panel)

        self.screenshot_list = ScreenshotList(panel)
        self.AddLabelledControl(panel, "Screenshots", self.screenshot_list)

        self.note_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE, size=(250, 100))
        self.AddLabelledControl(panel, "Notes", self.note_box)

        go_button = wx.Button(panel, label="Enter")
        self.AddLabelledControl(panel, "", go_button)
        self.Bind(wx.EVT_BUTTON, self.OnGoButton, go_button)

        panel.SetSizer(self.grid)
        self.Layout()
        self.Show(True)

    def AddLabelledControl(self, panel, label, control):
        self.grid.Add(
            wx.StaticText(panel, label=label),
            0,
            wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.ALL,
            border=5,
        )
        self.grid.Add(
            control, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, border=5
        )

    def OnChoice(self, event):
        if event.GetSelection() == 2:
            self.status_note_box.Enable()
        else:
            self.status_note_box.Disable()

    def OnGoButton(self, event):
        shortname = self.shortname.GetValue()
        if shortname == "":
            mb = wx.MessageDialog(self, "Missing shortname")
            mb.ShowModal()
            return
        status = self.choice_list[self.choice.GetSelection()]
        status_note = self.status_note_box.GetValue()
        rating = 0
        for i in range(0, 5):
            if self.rating_buttons[i].GetValue():
                rating = i + 1

        screenshots = []
        for i in range(0, self.screenshot_list.GetItemCount()):
            screenshots.append(
                [
                    self.screenshot_list.GetItem(i).GetText(),
                    self.screenshot_list.GetItem(i, 1).GetText(),
                ]
            )
        if len(screenshots) < 2:
            mb = wx.MessageDialog(
                self, "Not enough screenshots, do at least title and gameplay."
            )
            mb.ShowModal()
            return
        for (_, title) in screenshots:
            if title == "":
                mb = wx.MessageDialog(self, "Untitled screenshot.")
                mb.ShowModal()
                return

        notes = self.note_box.GetValue()
        if notes == "":
            mb = wx.MessageDialog(self, "Missing notes")
            mb.ShowModal()
            return

        played_games = {}
        with open("played-games.edn", "r") as file:
            data = file.read()
            played_games = edn_format.loads(data)
        played_games = played_games[:]
        pg = dict(played_games[-1])
        pg[edn_format.Keyword("shortname")] = shortname
        pg[edn_format.Keyword("rating")] = rating
        pg[edn_format.Keyword("status")] = edn_format.Keyword(
            status.lower().replace(" ", "-")
        )
        if status == "Other" and status_note != "":
            pg[edn_format.Keyword("status-note")] = status_note
        pg[edn_format.Keyword("notes")] = notes
        pg[edn_format.Keyword("completion-date")] = str(datetime.datetime.now().date())
        played_games[-1] = pg

        games = {}
        with open("games.edn", "r") as file:
            data = file.read()
            games = edn_format.loads(data)
        games = games[:]

        if len(games) == 0:
            with open("played-games.edn", "w") as file:
                file.write(dump_edn(played_games))
            mb = wx.MessageDialog(self, "Woah, challenge done?!")
            mb.ShowModal()
            quit()

        r = random.randrange(len(games))
        next_game = games[r]
        games.remove(next_game)
        next_game = dict(next_game)
        next_game[edn_format.Keyword("rating")] = edn_format.Keyword("na")
        played_games.append(next_game)

        with open("games.edn", "w") as file:
            file.write(dump_edn(games))

        with open("played-games.edn", "w") as file:
            file.write(dump_edn(played_games))

        self.now_playing.SetLabel(str(next_game))
        self.now_playing.Wrap(250)
        self.shortname.SetValue("")
        self.status_note_box.SetValue("")
        self.note_box.SetValue("")
        self.screenshot_list.DeleteAllItems()

        copyScreenshots(shortname, screenshots)

        mb = wx.MessageDialog(self, "Next up:" + str(next_game))
        mb.ShowModal()

        generateWebsite()


if __name__ == "__main__":
    django.conf.settings.configure()

    played_games = {}
    with open("played-games.edn", "r") as file:
        data = file.read()
        played_games = edn_format.loads(data)
    now_playing = played_games[-1]

    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = P255Frame(None, now_playing)
    app.MainLoop()
