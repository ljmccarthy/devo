#!/usr/bin/env python2

import sys, os
os.chdir(sys.path[0])
sys.path.append(os.path.join(sys.path[0], "..", "fsmonitor"))

import getopt
import wx

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.first_drop = True

    def OnInit(self):
        import async_wx
        async_wx.set_wx_scheduler()
        self.SetAppName("Devo")

        return True

    def MacOpenFile(self, filename):
        if not self.first_drop or hasattr(sys, "frozen"):
            self.mainframe.OpenEditor(filename)
        self.first_drop = False

def process_args(args):
    try:
        opts, args = getopt.gnu_getopt(args, "", ["project="])
    except getopt.GetoptError, e:
        sys.stderr.write("devo: error: %s\n" % e)
        sys.exit(1)

    project = None
    for opt, arg in opts:
        if opt == "--project":
            project = arg

    from mainframe import MainFrame
    mainframe = MainFrame(project)

    for arg in args:
        mainframe.OpenEditor(arg)

def main():
    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()
    app = App()
    mainframe = process_args(sys.argv[1:])
    app.SetTopWindow(mainframe)
    app.MainLoop()

if __name__ == "__main__":
    main()
