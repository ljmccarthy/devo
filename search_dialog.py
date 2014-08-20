import sys
import os
import wx
from file_picker import DirPicker
from util import get_combo_history

file_pattern_choices = [
    "*",
    "*.py",
    "*.c;*.cc;*.cxx;*.cpp;*.h;*.hh;*.hxx;*.hpp;*.m;*.mm",
    "*.txt;*.text;*.rst;*.md;*.markdown",
    "*.html;*.htm;*.xml;*.xhtml;*.xht",
]

class SearchDetails(object):
    def __init__(self, case=False, regexp=False, hidden=False, find="", find_history=(),
                 file_patterns="*", path="", path_history=()):
        self.case = case
        self.regexp = regexp
        self.hidden = hidden
        self.find = find
        self.find_history = find_history
        self.file_patterns = file_patterns
        self.path = path
        self.path_history = path_history

    def LoadPerspective(self, p):
        try:
            self.case = bool(p.get("case_sensitive", False))
            self.regexp = bool(p.get("is_regex", False))
            self.hidden = bool(p.get("hidden", False))
            self.find = str(p.get("find", ""))
            self.find_history = p.get("find_history", [])[:10]
            self.file_patterns = str(p.get("file_patterns"))
            self.path = str(p.get("path", ""))
            self.path_history = p.get("path_history")[:10]
        except Exception:
            pass

    def SavePerspective(self):
        return {
            "case_sensitive": self.case,
            "is_regex": self.regexp,
            "hidden": self.hidden,
            "find": self.find,
            "find_history": self.find_history[:],
            "file_patterns": self.file_patterns,
            "path": self.path,
            "path_history": self.path_history[:],
        }

class SearchDialog(wx.Dialog):
    def __init__(self, parent, details=None):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Search", style=style)

        combo_style = wx.TE_PROCESS_ENTER if wx.Platform == "__WXMAC__" else 0
        self.combo_find = wx.ComboBox(self, size=(300, -1), style=combo_style)
        self.combo_file_patterns = wx.ComboBox(
            self, size=(300, -1), value="*", choices=file_pattern_choices, style=combo_style)
        self.dir_picker = DirPicker(self, size=(300, -1), combo=True)
        self.check_case = wx.CheckBox(self, wx.ID_ANY, "&Case sensitive")
        self.check_regexp = wx.CheckBox(self, label="Regular e&xpression")
        self.check_hidden = wx.CheckBox(self, label="Search &hidden files and folders")

        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Find Text"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.combo_find, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="File Patterns"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.combo_file_patterns, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Directory"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.dir_picker, 0, wx.EXPAND)
        grid.AddSpacer(0)
        chksizer = wx.BoxSizer(wx.VERTICAL)
        chksizer.Add(self.check_case, 0, wx.ALL, 2)
        chksizer.Add(self.check_regexp, 0, wx.ALL, 2)
        chksizer.Add(self.check_hidden, 0, wx.ALL, 2)
        grid.Add(chksizer)

        btn_search = wx.Button(self, wx.ID_OK, label="&Search")
        btn_search.SetDefault()
        btn_cancel = wx.Button(self, wx.ID_CANCEL)

        btnsizer = wx.StdDialogButtonSizer()
        btnsizer.AddButton(btn_search)
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
            self.combo_file_patterns.SetValue(details.file_patterns)
            self.dir_picker.SetHistory(details.path_history)
            self.dir_picker.SetValue(details.path)
            self.check_case.SetValue(details.case)
            self.check_regexp.SetValue(details.regexp)
            self.check_hidden.SetValue(details.hidden)

        self.combo_find.SetFocus()
        self.combo_find.SetMark(0, len(self.combo_find.GetValue()))

        self.combo_find.Bind(wx.EVT_KEY_DOWN, self.OnComboKeyDown)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnFind)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, btn_search)

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
            case = self.check_case.GetValue(),
            regexp = self.check_regexp.GetValue(),
            hidden = self.check_hidden.GetValue(),
            find = self.find,
            find_history = get_combo_history(self.combo_find),
            file_patterns = self.combo_file_patterns.GetValue(),
            path = self.path,
            path_history = self.dir_picker.GetHistory())

    def OnComboKeyDown(self, evt):
        if evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.OnFind(None)
        else:
            evt.Skip()

    def OnFind(self, evt):
        self.EndModal(wx.ID_OK)

    def OnUpdateFind(self, evt):
        find = self.find
        path = self.path
        evt.Enable(bool(find and path and os.path.isdir(path)))

if __name__ == "__main__":
    app = wx.App()
    dlg = SearchDialog(None)
    dlg.ShowModal()
    print dlg.GetDetails()
