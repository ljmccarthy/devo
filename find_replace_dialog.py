import wx
import re
from dialogs import dialogs
from dialog_util import bind_escape_key
from util import get_combo_history

class FindReplaceDetails(object):
    def __init__(self, find="", replace="", case=False, reverse=False, regexp=False,
                 find_history=(), replace_history=()):
        self.case = case
        self.reverse = reverse
        self.regexp = regexp
        self.__find = None
        self.find = find
        self.replace = replace
        self.find_history = find_history
        self.replace_history = replace_history

    @property
    def find(self):
        return self.__find

    @find.setter
    def find(self, ptn):
        self.rx_find = re.compile(
            ptn.encode("utf-8") if self.regexp else re.escape(ptn.encode("utf-8")),
            0 if self.case else re.IGNORECASE)
        self.__find = ptn

    def _IterFindLines(self, editor, wrap=True):
        init_pos = editor.GetSelection()[1]
        init_line = editor.LineFromPosition(init_pos)
        last_line = editor.LineFromPosition(editor.GetTextLength())

        line_start = editor.PositionFromLine(init_line)
        line_end = editor.GetLineEndPosition(init_line)

        yield init_pos, editor.GetTextRangeRaw(init_pos, line_end)

        for line in xrange(init_line + 1, last_line + 1):
            yield editor.PositionFromLine(line), editor.GetLineRaw(line)

        if wrap:
            for line in xrange(0, init_line):
                yield editor.PositionFromLine(line), editor.GetLineRaw(line)

            yield line_start, editor.GetTextRangeRaw(line_start, init_pos)

    def _IterFindLinesReversed(self, editor, wrap=True):
        init_pos = editor.GetSelection()[0]
        init_line = editor.LineFromPosition(init_pos)
        last_line = editor.LineFromPosition(editor.GetTextLength())

        line_start = editor.PositionFromLine(init_line)
        line_end = editor.GetLineEndPosition(init_line)

        yield line_start, editor.GetTextRangeRaw(line_start, init_pos)

        for line in xrange(init_line - 1, -1, -1):
            yield editor.PositionFromLine(line), editor.GetLineRaw(line)

        if wrap:
            for line in xrange(last_line, init_line, -1):
                yield editor.PositionFromLine(line), editor.GetLineRaw(line)

            yield init_pos, editor.GetTextRangeRaw(init_pos, line_end)

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

    def Find(self, editor, wrap=True, reverse=False):
        reverse = reverse ^ self.reverse
        iterator = self._IterFindLines if not reverse else self._IterFindLinesReversed
        for pos, line in iterator(editor, wrap):
            m = self.rx_find.search(line)
            if m and reverse:
                while True:
                    start = m.end()
                    m2 = self.rx_find.search(line, start)
                    if not m2:
                        break
                    m = m2
            if m and m.start() != m.end():
                editor.CentreLine(editor.LineFromPosition(pos))
                editor.SetSelection(pos + m.start(), pos + m.end())
                return True
        return False

    def Replace(self, editor):
        if self.rx_find.match(editor.GetSelectedText()):
            self._ReplaceSelected(editor)
        return self.Find(editor)

    def ReplaceAll(self, editor):
        count = 0
        editor.BeginUndoAction()
        try:
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
        finally:
            editor.EndUndoAction()

class FindReplaceDialog(wx.Dialog):
    def __init__(self, editor, filename="", details=None):
        title = "Find and Replace"
        if filename:
            title += " [%s]" % filename

        wx.Dialog.__init__(self, editor, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.editor = editor

        self.combo_find = wx.ComboBox(self, size=(300, -1))
        self.combo_replace = wx.ComboBox(self, size=(300, -1))
        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Find"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.combo_find, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Replace"), 0, wx.ALIGN_CENTRE_VERTICAL)
        grid.Add(self.combo_replace, 0, wx.EXPAND)
        grid.AddSpacer(0)
        self.check_case = wx.CheckBox(self, wx.ID_ANY, "&Case sensitive")
        self.check_regexp = wx.CheckBox(self, wx.ID_ANY, "Regular e&xpression")
        self.check_reverse = wx.CheckBox(self, wx.ID_ANY, "Re&verse")
        chksizer = wx.BoxSizer(wx.VERTICAL)
        chksizer.Add(self.check_case, 0, wx.ALL, 2)
        chksizer.Add(self.check_regexp, 0, wx.ALL, 2)
        chksizer.Add(self.check_reverse, 0, wx.ALL, 2)
        grid.Add(chksizer)

        spacer = 10 if wx.Platform == "__WXMAC__" else 5
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_goto_start = wx.Button(self, label="&Go to Start")
        btnsizer.Add(btn_goto_start)
        btnsizer.AddSpacer(spacer)
        btnsizer.AddStretchSpacer()
        btn_find = wx.Button(self, wx.ID_FIND, "&Find")
        btn_find.SetDefault()
        btnsizer.Add(btn_find)
        btnsizer.AddSpacer(spacer)
        btnsizer.Add(wx.Button(self, wx.ID_REPLACE, "&Replace"))
        btnsizer.AddSpacer(spacer)
        btnsizer.Add(wx.Button(self, wx.ID_REPLACE_ALL, "Replace &All"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALL, spacer)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.Size)
        self.SetMaxSize((-1, self.Size.height))

        # Position in bottom-right corner
        pos = editor.Parent.ClientToScreen(editor.Position)
        self.SetPosition((
            pos.x + (editor.Size.width - self.Size.width) - 20,
            pos.y + (editor.Size.height - self.Size.height) - 20))

        if details is not None:
            self.combo_find.SetItems(details.find_history)
            self.combo_find.SetValue(details.find)
            self.combo_replace.SetItems(details.replace_history)
            self.combo_replace.SetValue(details.replace)
            self.check_case.SetValue(details.case)
            self.check_regexp.SetValue(details.regexp)
            self.check_reverse.SetValue(details.reverse)

        self.combo_find.SetFocus()
        self.combo_find.SetMark(0, len(self.combo_find.GetValue()))

        self.combo_find.Bind(wx.EVT_KEY_DOWN, self.OnComboKeyDown)
        self.combo_replace.Bind(wx.EVT_KEY_DOWN, self.OnComboKeyDown)
        self.Bind(wx.EVT_BUTTON, self.OnGoToStart, btn_goto_start)
        self.Bind(wx.EVT_BUTTON, self.OnFind, id=wx.ID_FIND)
        self.Bind(wx.EVT_BUTTON, self.OnReplace, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_BUTTON, self.OnReplaceAll, id=wx.ID_REPLACE_ALL)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, id=wx.ID_FIND)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateFind, id=wx.ID_REPLACE_ALL)
        bind_escape_key(self)

    def OnGoToStart(self, evt):
        self.editor.SetSelection(0, 0)

    def OnComboKeyDown(self, evt):
        if evt.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.OnFind(None)
        else:
            evt.Skip()

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

    def OnUpdateFind(self, evt):
        evt.Enable(bool(self.combo_find.GetValue()))

    def GetFindDetails(self, show_error=False):
        try:
            return FindReplaceDetails(
                find = self.combo_find.GetValue(),
                find_history = get_combo_history(self.combo_find),
                replace = self.combo_replace.GetValue(),
                replace_history = get_combo_history(self.combo_replace),
                case = self.check_case.GetValue(),
                reverse = self.check_reverse.GetValue(),
                regexp = self.check_regexp.GetValue())
        except re.error, e:
            if show_error:
                dialogs.error(self.editor,
                    "Invalid regular expression:\n\n" + str(e).capitalize())
