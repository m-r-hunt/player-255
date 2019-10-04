#!/usr/bin/env python
import wx
import django.template

if __name__ == "__main__":
    engine = django.template.Engine(["resources"])
    template = engine.get_template("templates/index.html")
    context = django.template.Context({"recent-games": [], "next_up": {"game": "foo"}})
    print(template.render(context))
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = wx.Frame(None, wx.ID_ANY, "Hello World") # A Frame is a top-level window.
    frame.Show(True)     # Show the frame.
    app.MainLoop()
