import os
import wx

from dirtree import DirTreeCtrl, DirTreeFilter, DirNode
from dirtree_constants import ID_DIRTREE_OPEN

class DirDialogTreeCtrl(DirTreeCtrl):
    def __init__(self, parent, filter):
        DirTreeCtrl.__init__(self, parent, filter=filter)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_MENU, self.OnItemActivated, id=ID_DIRTREE_OPEN)

    def OnItemActivated(self, evt):
        self.Parent.EndModal(wx.ID_OK)

class DirDialog(wx.Dialog):
    def __init__(self, parent, size=wx.DefaultSize, message="", path="", select_path=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        if size == wx.DefaultSize:
            size = wx.Size(450, 600)
        wx.Dialog.__init__(self, parent, size=size, title=message, style=style)

        toplevel = [DirNode(path)] if path else None
        filter = DirTreeFilter(show_files=False)
        self.dirtree = DirDialogTreeCtrl(self, filter)
        self.dirtree.SetTopLevel(toplevel)
        if select_path:
            self.dirtree.SelectPath(select_path)

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

        self.dirtree.SetFocus()
        self.Centre()

    def GetPath(self):
        return self.dirtree.GetSelectedPath()
