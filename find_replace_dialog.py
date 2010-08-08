import wx
import re
from dialogs import dialogs
from dialog_util import bind_escape_key

class FindReplaceDetails(object):
    def __init__(self, find, replace, case=False, reverse=False, regexp=False):
        self.case = case
        self.reverse = reverse
        self.regexp = regexp
        self.__find = None
        self.find = find
        self.replace = replace

    @property
    def find(self):
        return self.__find

    @find.setter
    def find(self, ptn):
        self.rx_find = re.compile(
            ptn if self.regexp else re.escape(ptn),
            0 if self.case else re.IGNORECASE)
        self.__find = ptn

    def _IterFindLines(self, editor, wrap=True):
        init_pos = editor.GetSelection()[1]
        init_line = editor.LineFromPosition(init_pos)
        last_line = editor.LineFromPosition(editor.GetTextLength())

        line_end = editor.GetLineEndPosition(init_line)
        yield init_pos, editor.GetTextRange(init_pos, line_end)

        for line in xrange(init_line + 1, last_line + 1):
            yield editor.PositionFromLine(line), editor.GetLine(line)

        if wrap:
            for line in xrange(0, init_line):
                yield editor.PositionFromLine(line), editor.GetLine(line)

            line_start = editor.PositionFromLine(init_line)
            yield line_start, editor.GetTextRange(line_start, init_pos)

    def _ReplaceSelected(self, editor):
        text = editor.GetSelectedText()
        if text:
            if self.regexp:
                try:
                    repl = self.rx_find.sub(self.replace, editor.GetSelectedText(), 1)
                    editor.ReplaceSelection(repl)
                except re.error, e:
                    dialogs.error(editor, "Replace error:\n\n" + str(e).capitalize())
                    return False
            else:
                editor.ReplaceSelection(self.replace)

    def Find(self, editor, wrap=True):
        for pos, line in self._IterFindLines(editor, wrap):
            m = self.rx_find.search(line)
            if m and m.start() != m.end():
                editor.SetSelection(pos + m.start(), pos + m.end())
                return True
        return False

    def Replace(self, editor):
        if self.rx_find.match(editor.GetSelectedText()):
            self._ReplaceSelected(editor)
        return self.Find(editor)

    def ReplaceAll(self, editor):
        count = 0
        editor.SetSelection(0, 0)
        m = True
        while m:
            for pos, line in self._IterFindLines(editor, wrap=False):
                m = self.rx_find.search(line)
                if m and m.start() != m.end():
                    editor.SetSelection(pos + m.start(), pos + m.end())
                    self._ReplaceSelected(editor)
                    count += 1
                    break
        return count

ID_GO_TO_START = wx.NewId()

class FindReplaceDialog(wx.Dialog):
    def __init__(self, parent, filename="", details=None):
        title = "Find and Replace"
        if filename:
            title += " [%s]" % filename

        wx.Dialog.__init__(self, parent, title=title)
        self.editor = parent

        self.text_find = wx.TextCtrl(self, size=(300, -1))
        self.text_replace = wx.TextCtrl(self, size=(300, -1))
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Find"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.text_find, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Replace"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.text_replace, 0, wx.EXPAND)
        grid.AddSpacer(0)
        self.check_case = wx.CheckBox(self, wx.ID_ANY, "&Case sensitive")
        self.check_regexp = wx.CheckBox(self, wx.ID_ANY, "Regular &expression")
        self.check_reverse = wx.CheckBox(self, wx.ID_ANY, "Re&verse")
        chksizer = wx.BoxSizer(wx.VERTICAL)
        chksizer.Add(self.check_case)
        chksizer.AddSpacer(5)
        chksizer.Add(self.check_regexp)
        chksizer.AddSpacer(5)
        chksizer.Add(self.check_reverse)
        grid.Add(chksizer)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.AddStretchSpacer()
        btnsizer.Add(wx.Button(self, ID_GO_TO_START, "&Go to Start"))
        btnsizer.AddSpacer(5)
        btn_find = wx.Button(self, wx.ID_FIND, "&Find")
        btn_find.SetDefault()
        btnsizer.Add(btn_find)
        btnsizer.AddSpacer(5)
        btnsizer.Add(wx.Button(self, wx.ID_REPLACE, "&Replace"))
        btnsizer.AddSpacer(5)
        btnsizer.Add(wx.Button(self, wx.ID_REPLACE_ALL, "Replace &All"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()

        if details is not None:
            self.text_find.SetValue(details.find)
            self.text_replace.SetValue(details.replace)
            self.check_regexp.SetValue(details.regexp)
            self.check_reverse.SetValue(details.reverse)

        self.text_find.SetFocus()
        self.text_find.SetSelection(-1, -1)

        self.Bind(wx.EVT_BUTTON, self.OnGoToStart, id=ID_GO_TO_START)
        self.Bind(wx.EVT_BUTTON, self.OnFind, id=wx.ID_FIND)
        self.Bind(wx.EVT_BUTTON, self.OnReplace, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_BUTTON, self.OnReplaceAll, id=wx.ID_REPLACE_ALL)
        bind_escape_key(self)

    def OnGoToStart(self, evt):
        self.editor.SetSelection(0, 0)

    def OnFind(self, evt):
        details = self.GetFindDetails(True)
        if details and not details.Find(self.editor):
            dialogs.info(self, "Pattern not found: '%s'" % details.find, "Find")

    def OnReplace(self, evt):
        details = self.GetFindDetails(True)
        if details and not details.Replace(self.editor):
            dialogs.info(self, "Pattern not found: '%s'" % details.find, "Replace")

    def OnReplaceAll(self, evt):
        details = self.GetFindDetails(True)
        if not details:
            return
        count = details.ReplaceAll(self.editor)
        if count > 0:
            dialogs.info(self,
                "Replaced %d instances of '%s'" % (count, details.find),
                "Replace All")
        else:
            dialogs.info(self,
                "Pattern not found: '%s'" % details.find,
                "Replace All")

    def GetFindDetails(self, show_error=False):
        try:
            return FindReplaceDetails(
                find = self.text_find.GetValue(),
                replace = self.text_replace.GetValue(),
                case = self.check_case.GetValue(),
                reverse = self.check_reverse.GetValue(),
                regexp = self.check_regexp.GetValue())
        except re.error, e:
            if show_error:
                dialogs.error(self.editor,
                    "Invalid regular expression:\n\n" + str(e).capitalize())
