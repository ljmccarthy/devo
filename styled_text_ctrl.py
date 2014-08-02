import os.path
import string
import random
import wx
import wx.stc
from contextlib import contextmanager

from find_replace_dialog import FindReplaceDetails, FindReplaceDialog
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu
from syntax import syntax_from_filename, syntax_plain
from themes import default_theme
from util import clean_text, clean_strip_text, unique

MARKER_FIND = 0
MARKER_ERROR = 1

default_styles = [
    (wx.stc.STC_STYLE_DEFAULT,    ""),
    (wx.stc.STC_STYLE_LINENUMBER, "back:#C0C0C0"),
    (wx.stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold"),
    (wx.stc.STC_STYLE_BRACEBAD,   "fore:#000000,back:#FF0000,bold"),
]

class StyledTextCtrl(wx.stc.StyledTextCtrl):
    name = ""

    def __init__(self, parent, env):
        wx.stc.StyledTextCtrl.__init__(self, parent, pos=(-1, -1), size=(1, 1), style=wx.BORDER_NONE)
        self.env = env
        self.UsePopUp(False)
        self.SetSyntax(syntax_plain)
        self.SetScrollWidth(1)
        #self.SetScrollWidthTracking(True)

        self.Bind(wx.EVT_KEY_DOWN, self.__OnKeyDown)
        self.Bind(wx.EVT_CONTEXT_MENU, self.__OnContextMenu)
        self.Bind(wx.stc.EVT_STC_CHANGE, self.__OnChange)

    def ShouldFilterKeyEvent(self, evt):
        key = evt.GetKeyCode()
        mod = evt.GetModifiers()
        return ((mod & wx.MOD_RAW_CONTROL) and unichr(key) in string.ascii_letters) \
            or (wx.WXK_F1 <= key <= wx.WXK_F24)

    def __OnKeyDown(self, evt):
        evt.Skip(not self.ShouldFilterKeyEvent(evt))

    def GetDyanmicEditMenuItems(self):
        return []

    def __OnContextMenu(self, evt):
        self.SetFocus()
        self.PopupMenu(edit_menu.Create(hooks={"edit": self.GetDyanmicEditMenuItems()}))

    def __OnChange(self, evt):
        # Assumes that all styles use the same fixed-width font.
        max_len = max(self.LineLength(line) for line in xrange(self.GetLineCount()))
        self.SetScrollWidth((max_len + 1) * self.TextWidth(wx.stc.STC_STYLE_DEFAULT, "_"))

    def RefreshStyle(self):
        font = self.env.editor_font
        font_info = (font.PointSize, font.FaceName,
            font.Weight == wx.FONTWEIGHT_BOLD,
            font.Style in (wx.FONTSTYLE_ITALIC, wx.FONTSTYLE_SLANT), False)

        self.ClearDocumentStyle()
        self.SetLexer(self.syntax.lexer)
        self.SetKeyWords(0, self.syntax.keywords)
        self.StyleResetDefault()
        self.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, *font_info)
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
        self.StyleClearAll()

        self.MarkerDefine(MARKER_FIND, wx.stc.STC_MARK_BACKGROUND, background="#CCCCFF")
        self.MarkerDefine(MARKER_ERROR, wx.stc.STC_MARK_BACKGROUND, background="#FFCCCC")

        for token_type, style_spec in default_styles:
            self.StyleSetSpec(token_type, style_spec)

        for token_type, style_spec in self.syntax.get_style_specs(default_theme):
            self.StyleSetSpec(token_type, style_spec)

        self.SetIndent(self.syntax.indent_width)
        self.SetTabWidth(self.syntax.tab_width)
        self.SetUseTabs(self.syntax.use_tabs)
        self.Colourise(0, -1)

    def SetSyntax(self, syntax):
        self.syntax = syntax
        self.RefreshStyle()

    def SetSyntaxFromFilename(self, path):
        self.SetSyntax(syntax_from_filename(path))

    def ClearHighlight(self, marker_type):
        self.MarkerDeleteAll(marker_type)

    def SetHighlightedLine(self, line, marker_type):
        self.ClearHighlight(marker_type)
        self.MarkerAdd(line, marker_type)

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

    def Paste(self):
        wx.TheClipboard.Open()
        try:
            text_data = wx.TextDataObject()
            if wx.TheClipboard.GetData(text_data):
                text = clean_strip_text(text_data.GetText())
                self.ReplaceSelection(text)
        finally:
            wx.TheClipboard.Close()

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
        if start == end:
            end += 1
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
            s = self.GetLineRaw(line)[:-1]
            pos = self.PositionFromLine(line) + indent
            self.SetRangeText(pos, pos, self.syntax.comment_token)
        self.EndUndoAction()

    def Uncomment(self):
        self.BeginUndoAction()
        for line in self.GetLineSelectionRange():
            s = self.GetLineRaw(line)[:-1]
            if s:
                offset = len(s) - len(s.lstrip())
                if s[offset : offset + len(self.syntax.comment_token)] == self.syntax.comment_token:
                    pos = self.PositionFromLine(line) + offset
                    self.SetRangeText(pos, pos + len(self.syntax.comment_token), "")
        self.EndUndoAction()

    def ReplaceSelectionAndSelect(self, replace):
        start = self.GetSelectionStart()
        self.ReplaceSelection(replace)
        self.SetSelection(start, start + len(replace))

    def JoinLines(self):
        start = self.GetSelectionStart()
        lines = self.GetSelectedText().split("\n")
        replace = " ".join(line.strip() for line in lines[1:])
        replace = lines[0] + " " + replace if replace else lines[0]
        self.ReplaceSelectionAndSelect(replace)

    def GetLineIndentText(self, line_num):
        line = self.GetLine(line_num)
        return line[:len(line) - len(line.lstrip())]

    def GetFirstSelectedLineIndent(self):
        start = self.GetSelectionStart()
        return self.GetLineIndentText(self.LineFromPosition(start))

    def SplitLines(self):
        indent = self.GetFirstSelectedLineIndent()
        lines = self.GetSelectedText().split("\n", 1)
        first = lines[0]
        rest = lines[1] if len(lines) == 2 else ""
        first_parts = first.split()
        replace_lines = [first.rsplit(None, len(first_parts) - 1)[0]]
        replace_lines.extend(indent + x for x in first_parts[1:])
        replace_lines.extend(indent + x for x in rest.split())
        replace = "\n".join(replace_lines)
        self.ReplaceSelectionAndSelect(replace)

    def SelectLines(self):
        start, end = self.GetSelection()
        start = self.PositionFromLine(self.LineFromPosition(start))
        end_line = self.LineFromPosition(end)
        end = self.PositionFromLine(end_line) + self.GetLineLength(end_line)
        self.SetSelection(start, end)

    def SortLines(self):
        self.SelectLines()
        lines = self.GetSelectedText().split("\n")
        lines.sort(key=lambda x: x.strip())
        self.ReplaceSelectionAndSelect("\n".join(lines))

    def SortLinesCaseInsensitive(self):
        self.SelectLines()
        lines = self.GetSelectedText().split("\n")
        lines.sort(key=lambda x: x.strip().lower())
        self.ReplaceSelectionAndSelect("\n".join(lines))

    def UniqueLines(self):
        self.SelectLines()
        lines = self.GetSelectedText().split("\n")
        lines = unique(lines)
        self.ReplaceSelectionAndSelect("\n".join(lines))

    def ReverseLines(self):
        self.SelectLines()
        lines = self.GetSelectedText().split("\n")
        lines.reverse()
        self.ReplaceSelectionAndSelect("\n".join(lines))

    def ShuffleLines(self):
        self.SelectLines()
        lines = self.GetSelectedText().split("\n")
        random.shuffle(lines)
        self.ReplaceSelectionAndSelect("\n".join(lines))

    def RemoveExtraSpace(self):
        replace_lines = []
        for line in self.GetSelectedText().split("\n"):
            indent = line[:len(line) - len(line.lstrip())]
            replace_lines.append(indent + " ".join(line.split()))
        self.ReplaceSelectionAndSelect("\n".join(replace_lines))

    def TabsToSpaces(self):
        replace = self.GetSelectedText().expandtabs(self.GetTabWidth())
        self.ReplaceSelectionAndSelect(replace)

    def LowerCase(self):
        self.ReplaceSelectionAndSelect(self.GetSelectedText().lower())

    def UpperCase(self):
        self.ReplaceSelectionAndSelect(self.GetSelectedText().upper())

    def TitleCase(self):
        self.ReplaceSelectionAndSelect(self.GetSelectedText().title())

    def SwapCase(self):
        self.ReplaceSelectionAndSelect(self.GetSelectedText().swapcase())

    def GetSelectedFirstLine(self):
        return self.GetSelectedText().strip().split("\n", 1)[0]

    def Find(self):
        selected = self.GetSelectedFirstLine()
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
            self.SetFocus()

    def FindNext(self):
        if self.CanFindNext():
            self.env.find_details.Find(self)

    def FindPrev(self):
        if self.CanFindPrev():
            self.env.find_details.Find(self, reverse=True)

    def GoToLine(self):
        dlg = GoToLineDialog(self, self.name, self.GetCurrentLine() + 1)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.CentreLine(dlg.GetLineNumber())
                self.GotoLine(dlg.GetLineNumber())
        finally:
            dlg.Destroy()
            self.SetFocus()

    @contextmanager
    def ModifyReadOnly(self):
        was_read_only = self.GetReadOnly()
        self.SetReadOnly(False)
        try:
            yield
        finally:
            self.SetReadOnly(was_read_only)
