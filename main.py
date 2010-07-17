#!/usr/bin/env python

import sys, os
os.chdir(sys.path[0])
sys.path.append(os.path.join(sys.path[0], "..", "fsmonitor"))

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
