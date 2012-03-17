import os.path
from contextlib import contextmanager
import wx, wx.stc

from editor_fonts import font_face, font_size
from find_replace_dialog import FindReplaceDetails, FindReplaceDialog
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu
from syntax import filename_syntax_re, syntax_dict, plain

MARKER_FIND = 0
MARKER_ERROR = 1

class StyledTextCtrl(wx.stc.StyledTextCtrl):
    name = ""

    def __init__(self, parent, env):
        wx.stc.StyledTextCtrl.__init__(self, parent, pos=(-1, -1), size=(1, 1), style=wx.BORDER_NONE)
        self.env = env
        self._highlighted_lines = [None, None]
        self.UsePopUp(False)
        self.SetSyntax(plain)
        self.SetScrollWidth(1)

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.stc.EVT_STC_CHANGE, self.OnChange)

    def OnContextMenu(self, evt):
        self.SetFocus()
        self.PopupMenu(edit_menu.Create())

    def OnChange(self, evt):
        # Assumes that all styles use the same fixed-width font.
        max_len = max(self.LineLength(line) for line in xrange(self.GetLineCount()))
        self.SetScrollWidth((max_len + 1) * self.TextWidth(wx.stc.STC_STYLE_DEFAULT, "_"))

    def SetSyntax(self, syntax):
        self.syntax = syntax
        self.ClearDocumentStyle()
        self.SetLexer(syntax.lexer)
        self.SetKeyWords(0, syntax.keywords)
        self.StyleResetDefault()
        self.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, font_size, font_face, False, False, False)
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
        self.StyleClearAll()
        self.MarkerDefine(MARKER_FIND, wx.stc.STC_MARK_BACKGROUND, background="#CCCCFF")
        self.MarkerDefine(MARKER_ERROR, wx.stc.STC_MARK_BACKGROUND, background="#FFCCCC")
        for style_num, spec in syntax.stylespecs:
            self.StyleSetSpec(style_num, spec)
        self.SetIndent(syntax.indent)
        self.SetTabWidth(syntax.indent if syntax.use_tabs else 8)
        self.SetUseTabs(syntax.use_tabs)
        self.Colourise(0, -1)

    def SetSyntaxFromFilename(self, path):
        m = filename_syntax_re.match(os.path.basename(path))
        if m:
            self.SetSyntax(syntax_dict[m.lastgroup])
        else:
            self.SetSyntax(plain)

    def ClearHighlight(self, marker_type):
        line = self._highlighted_lines[marker_type]
        if line is not None:
            self.MarkerDelete(line, marker_type)
            self._highlighted_lines[marker_type] = None

    def SetHighlightedLine(self, line, marker_type):
        self.ClearHighlight(marker_type)
        self.MarkerAdd(line, marker_type)
        self._highlighted_lines[marker_type] = line

    def ClearAll(self):
        self.ClearHighlight(MARKER_FIND)
        self.ClearHighlight(MARKER_ERROR)
        wx.stc.StyledTextCtrl.ClearAll(self)

    def CanCut(self):
        return not self.GetReadOnly() and self.CanCopy()

    def CanCopy(self):
        return self.HasSelection()

    def CanFindNext(self):
        return bool(self.env.find_details and self.env.find_details.find)

    CanFindPrev = CanFindNext

    def IsEmpty(self):
        return self.GetTextLength() == 0

    def GetLastVisibleLine(self):
        return self.GetFirstVisibleLine() + self.LinesOnScreen() - 1

    def CentreLine(self, line):
        if not (self.GetFirstVisibleLine() <= line <= self.GetLastVisibleLine()):
            self.ScrollToLine(line - (self.LinesOnScreen() // 2))

    def SetCurrentLine(self, line):
        self.CentreLine(line)
        pos = self.PositionFromLine(line)
        self.SetSelection(pos, pos)

    def SetRangeText(self, start, end, text):
        self.SetTargetStart(start)
        self.SetTargetEnd(end)
        self.ReplaceTarget(text)

    def HasSelection(self):
        start, end = self.GetSelection()
        return start != end

    def GetLineSelection(self):
        start, end = self.GetSelection()
        return (self.LineFromPosition(start), self.LineFromPosition(end - 1))

    def GetLineSelectionRange(self):
        start_line, end_line = self.GetLineSelection()
        return xrange(start_line, end_line + 1)

    def SetLineSelection(self, start_line, end_line):
        self.SetSelection(self.PositionFromLine(start_line), self.GetLineEndPosition(end_line) - 1)

    def Indent(self):
        self.BeginUndoAction()
        for line in self.GetLineSelectionRange():
            indent = self.GetLineIndentation(line)
            self.SetLineIndentation(line, indent + self.GetIndent())
        self.EndUndoAction()

    def Unindent(self):
        self.BeginUndoAction()
        for line in self.GetLineSelectionRange():
            indent = self.GetLineIndentation(line)
            self.SetLineIndentation(line, indent - self.GetIndent())
        self.EndUndoAction()

    def GetSelectionIndent(self):
        indent = None
        for line in self.GetLineSelectionRange():
            if self.GetLine(line).strip():
                if indent is None:
                    indent = self.GetLineIndentation(line)
                else:
                    indent = min(indent, self.GetLineIndentation(line))
        return indent or 0

    def Comment(self):
        indent = self.GetSelectionIndent()
        self.BeginUndoAction()
        for line in self.GetLineSelectionRange():
            if not self.GetLine(line).strip():
                self.SetLineIndentation(line, indent)
            pos = self.PositionFromLine(line) + indent
            self.SetRangeText(pos, pos, self.syntax.comment_token)
        self.EndUndoAction()

    def Uncomment(self):
        self.BeginUndoAction()
        for line in self.GetLineSelectionRange():
            s = self.GetLineRaw(line)
            if s:
                offset = len(s) - len(s.strip()) - 1
                if s[offset : offset + len(self.syntax.comment_token)] == self.syntax.comment_token:
                    pos = self.PositionFromLine(line) + offset
                    self.SetRangeText(pos, pos + len(self.syntax.comment_token), "")
        self.EndUndoAction()

    def Find(self):
        selected = self.GetSelectedText().strip().split("\n", 1)[0]
        find_details = self.env.find_details or FindReplaceDetails(find=selected)
        if selected:
            find_details.find = selected
            find_details.replace = ""
            find_details.case = False
            find_details.regexp = False
            find_details.reverse = False

        dlg = FindReplaceDialog(self, self.name, find_details)
        try:
            dlg.ShowModal()
            self.env.find_details = dlg.GetFindDetails()
        finally:
            dlg.Destroy()

    def FindNext(self):
        if self.CanFindNext():
            self.env.find_details.Find(self)

    def FindPrev(self):
        if self.CanFindPrev():
            self.env.find_details.Find(self, reverse=True)

    def GoToLine(self):
        dlg = GoToLineDialog(self, self.name)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.GotoLine(dlg.GetLineNumber())
        finally:
            dlg.Destroy()

    @contextmanager
    def ModifyReadOnly(self):
        was_read_only = self.GetReadOnly()
        self.SetReadOnly(False)
        try:
            yield
        finally:
            self.SetReadOnly(was_read_only)
