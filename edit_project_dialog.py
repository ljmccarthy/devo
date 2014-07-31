import os
import wx
from file_picker import DirPicker

class EditProjectDialog(wx.Dialog):
    def __init__(self, parent, project):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Edit Project", style=style)

        self.text_name = wx.TextCtrl(self, value=project["name"], size=(250, -1))
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1)
        grid.Add(wx.StaticText(self, label="Project Name"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.text_name, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)

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
        self.SetMinSize(self.Size)
        self.SetMaxSize((-1, self.Size.height))

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_OK, id=wx.ID_OK)

    def OnUpdateUI_OK(self, evt):
        evt.Enable(bool(self.text_name.Value.strip()))

    def UpdateProject(self, project):
        name = self.text_name.Value.strip()
        if name:
            project["name"] = name

if __name__ == "__main__":
    app = wx.App()
    dlg = EditProjectDialog(None, {"name": "Foo Bar"})
    dlg.ShowModal()
