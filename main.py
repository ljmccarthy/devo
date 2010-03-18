import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "fsmonitor"))

import wx

def main():
    wx.InitAllImageHandlers()
    app = wx.PySimpleApp()
    app.SetAppName("Devo")
    from mainframe import MainFrame
    mainframe = MainFrame()
    app.SetTopWindow(mainframe)
    app.MainLoop()

if __name__ == "__main__":
    main()
