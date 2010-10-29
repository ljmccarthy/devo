#!/usr/bin/env python2

import sys, os
os.chdir(sys.path[0])
sys.path.append(os.path.join(sys.path[0], "..", "fsmonitor"))

import wx

def main():
    wx.InitAllImageHandlers()
    app = wx.PySimpleApp()
    app.SetAppName("Devo")
    import async_wx
    async_wx.set_wx_scheduler()
    from mainframe import MainFrame
    mainframe = MainFrame()
    app.SetTopWindow(mainframe)
    app.MainLoop()

if __name__ == "__main__":
    main()
