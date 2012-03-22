import os
import wx
from file_picker import DirPicker
from util import get_combo_history

class SearchDetails(object):
    def __init__(self, case=False, regexp=False, find="", find_history=(),
                 path="", path_history=()):
        self.case = case
        self.regexp = regexp
        self.find = find
        self.find_history = find_history
        self.path = path
        self.path_history = path_history

class SearchDialog(wx.Dialog):
    def __init__(self, parent, details=None):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Search", style=style)

        self.combo_find = wx.ComboBox(self, size=(300, -1))
        self.dir_picker = DirPicker(self, size=(300, -1), combo=True)
        self.check_case = wx.CheckBox(self, wx.ID_ANY, "&Case sensitive")
        self.check_regexp = wx.CheckBox(self, label="Regular e&xpression")

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

        btn_find = wx.Button(self, wx.ID_OK, label="&Search")
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

        if details is not None:
            self.combo_find.SetItems(details.find_history)
            self.combo_find.SetValue(details.find)
            self.dir_picker.SetHistory(details.path_history)
            self.dir_picker.SetValue(details.path)
            self.check_case.SetValue(details.case)
            self.check_regexp.SetValue(details.regexp)

        self.combo_find.SetFocus()
        self.combo_find.SetMark(0, len(self.combo_find.GetValue()))

        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, btn_find)

    @property
    def find(self):
        return self.combo_find.GetValue()

    @find.setter
    def find(self, value):
        self.combo_find.SetValue(value)

    @property
    def path(self):
        return os.path.expanduser(self.dir_picker.GetValue().strip())

    @path.setter
    def path(self, value):
        self.dir_picker.SetValue(value.strip())

    def GetDetails(self):
        return SearchDetails(
            case = self.check_case.GetValue(), regexp = self.check_regexp.GetValue(),
            find = self.find, find_history = get_combo_history(self.combo_find),
            path = self.path, path_history = self.dir_picker.GetHistory())

    def OnUpdateFind(self, evt):
        find = self.find
        path = self.path
        evt.Enable(bool(find and path and os.path.isdir(path)))

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = SearchDialog(None)
    dlg.ShowModal()
    print dlg.GetDetails()
