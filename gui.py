import wx
import wx.lib.mixins.listctrl


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
    def __init__(self, parent, now_playing, write_data_fn):
        wx.Frame.__init__(self, parent, title="Player 255", size=(500, 800))
        panel = wx.Panel(self)

        self.write_data_fn = write_data_fn

        self.grid = wx.FlexGridSizer(2, 10, 10)
        self.grid.AddGrowableCol(0)

        self.now_playing = wx.StaticText(panel, label=str(now_playing))
        self.now_playing.Wrap(250)
        self.AddLabelledControl(panel, "Now Playing", self.now_playing)

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

        data = {
            "rating": rating,
            "notes": notes,
            "screenshots": screenshots,
            "status": status,
            "status_note": status_note,
        }
        next_game = self.write_data_fn(data)

        self.now_playing.SetLabel(str(next_game))
        self.now_playing.Wrap(250)
        self.status_note_box.SetValue("")
        self.note_box.SetValue("")
        self.screenshot_list.DeleteAllItems()

        mb = wx.MessageDialog(self, "Next up:" + str(next_game))
        mb.ShowModal()


def runGUI(now_playing, fn):
    app = wx.App(False)
    frame = P255Frame(None, now_playing, fn)
    app.MainLoop()
