import os, collections
import wx
from file_picker import DirPicker

FindInFilesDetails = collections.namedtuple("FindInFilesDetails", "find path case regexp")

class FindInFilesDialog(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Find in Files", style=style)

        self.combo_find = wx.ComboBox(self, size=(300, -1))
        self.dir_picker = DirPicker(self, size=(300, -1), combo=True)
        self.check_case = wx.CheckBox(self, wx.ID_ANY, "&Case sensitive")
        self.check_regexp = wx.CheckBox(self, label="Regular &expression")

        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Find"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.combo_find, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Directory"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.dir_picker, 0, wx.EXPAND)
        grid.AddSpacer(0)
        chksizer = wx.BoxSizer(wx.VERTICAL)
        chksizer.Add(self.check_case, 0, wx.ALL, 2)
        chksizer.Add(self.check_regexp, 0, wx.ALL, 2)
        grid.Add(chksizer)

        btn_find = wx.Button(self, wx.ID_OK, label="&Find in Files")
        btn_find.SetDefault()
        btn_cancel = wx.Button(self, wx.ID_CANCEL)

        btnsizer = wx.StdDialogButtonSizer()
        btnsizer.AddButton(btn_find)
        btnsizer.AddButton(btn_cancel)
        btnsizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.Size)
        self.SetMaxSize((-1, self.Size.height))
        self.Centre()

        self.combo_find.SetFocus()
        self.combo_find.SetMark(0, len(self.combo_find.GetValue()))

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, btn_find)

    @property
    def find(self):
        return self.combo_find.GetValue().strip()

    @find.setter
    def find(self, value):
        self.combo_find.SetValue(value.strip())

    @property
    def path(self):
        return self.dir_picker.GetValue().strip()

    @path.setter
    def path(self, value):
        self.dir_picker.SetValue(value.strip())

    def GetDetails(self):
        return FindInFilesDetails(
            self.find, self.path, self.check_case.GetValue(), self.check_regexp.GetValue())

    def OnUpdateFind(self, evt):
        find = self.find
        path = self.path
        evt.Enable(bool(find and path and os.path.isdir(path)))

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = FindInFilesDialog(None)
    dlg.ShowModal()
    print dlg.GetDetails()
