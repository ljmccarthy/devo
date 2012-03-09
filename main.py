#!/usr/bin/env python2

import sys, os
os.chdir(sys.path[0])
sys.path.append(os.path.join(sys.path[0], "..", "fsmonitor"))

import wx

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.first_drop = True

    def OnInit(self):
        import async_wx
        async_wx.set_wx_scheduler()
        from mainframe import MainFrame
        self.SetAppName("Devo")
        self.mainframe = MainFrame()
        self.SetTopWindow(self.mainframe)
        return True

    def MacOpenFile(self, filename):
        if not self.first_drop or hasattr(sys, "frozen"):
            self.mainframe.OpenEditor(filename)
        self.first_drop = False

def main():
    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()
    app = App()
    app.MainLoop()

if __name__ == "__main__":
    main()
