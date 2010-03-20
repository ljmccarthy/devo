import os
import wx

from dirtree import DirTreeCtrl, DirTreeFilter, DirNode

class DirDialog(wx.Dialog):
    def __init__(self, parent, size=wx.DefaultSize, message="", path=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        if size == wx.DefaultSize:
            size = wx.Size(450, 600)
        wx.Dialog.__init__(self, parent, size=size, title=message, style=style)
        toplevel = [DirNode(path)] if path else None
        filter = DirTreeFilter(show_files=False)
        self.dirtree = DirTreeCtrl(self, self,
            toplevel=toplevel, filter=filter, show_root=True)
        btnsizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btnsizer.Realize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dirtree, 1, wx.EXPAND)
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def OpenFile(self, path):
        pass

    def GetPath(self):
        return self.dirtree.GetSelectedPath()
