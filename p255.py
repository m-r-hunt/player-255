#!/usr/bin/env python
import wx
import django.template
import wx.lib.mixins.listctrl


class FileDropper(wx.FileDropTarget):
    def __init__(self, list):
        wx.FileDropTarget.__init__(self)
        self.list = list

    def OnDropFiles(self, x, y, filenames):
        print(filenames)
        for file in filenames:
            self.list.Append([file, ""])
        return True


class ScreenshotList(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, size=(250, 100), style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.TextEditMixin.__init__(self)

        self.AppendColumn("File")
        self.AppendColumn("Title")
        self.Append(["c:/foo", ""])
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnUpdate)
        self.SetDropTarget(FileDropper(self))

    def OnUpdate(self, event):
        self.SetItem(event.GetIndex(), event.GetColumn(), event.GetLabel())


class P255Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Player 255", size=(500, 800))
        panel = wx.Panel(self)
        self.grid = wx.FlexGridSizer(2, 10, 10)
        self.grid.AddGrowableCol(0)

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
        print("Going:")
        print("shortname:", self.shortname.GetValue())
        print("status:", self.choice_list[self.choice.GetSelection()])
        print("status note:", self.status_note_box.GetValue())
        for i in range(0, 5):
            if self.rating_buttons[i].GetValue():
                print("rating:", "*" * (i + 1))

        for i in range(0, self.screenshot_list.GetItemCount()):
            print(
                "a screenshot:",
                self.screenshot_list.GetItem(i).GetText(),
                self.screenshot_list.GetItem(i, 1).GetText(),
            )
        print("notes:", self.note_box.GetValue())


if __name__ == "__main__":
    engine = django.template.Engine(["resources"])
    template = engine.get_template("templates/index.html")
    context = django.template.Context({"recent-games": [], "next_up": {"game": "foo"}})
    # print(template.render(context))
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = P255Frame(None)
    app.MainLoop()
