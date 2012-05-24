# Monkey patches for wxPython

import wx

if wx.VERSION < (2,9):
    wx.MouseState.LeftIsDown = wx.MouseState.LeftDown
    wx.MouseState.MiddleIsDown = wx.MouseState.MiddleDown
    wx.MouseState.RightIsDown = wx.MouseState.RightDown
