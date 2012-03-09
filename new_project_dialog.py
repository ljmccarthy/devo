import os
import wx
from file_picker import DirPicker

class NewProjectDialog(wx.Dialog):
    def __init__(self, parent, path=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="New Project", style=style)
        self.text_name = wx.TextCtrl(self, size=(380, -1))
        self.fp_root = DirPicker(self, value=path)
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1)
        grid.Add(wx.StaticText(self, label="Project Name"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.text_name, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(wx.StaticText(self, label="Root Folder"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.fp_root, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        btnsizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btnsizer.Realize()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.Centre()
        self.text_name.SetFocus()
        self.Bind(wx.EVT_UPDATE_UI, self.__OnUpdateUI_OK, id=wx.ID_OK)

    def __OnUpdateUI_OK(self, evt):
        evt.Enable(bool(self.GetName()) and os.path.isdir(self.GetRoot()))

    def GetName(self):
        return self.text_name.GetValue().strip()

    def GetRoot(self):
        return self.fp_root.GetValue()

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = NewProjectDialog(None)
    dlg.ShowModal()
