import os.path
from contextlib import contextmanager
import wx, wx.stc

from find_replace_dialog import FindReplaceDetails, FindReplaceDialog
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu

MARKER_FIND = 0
MARKER_ERROR = 1

class StyledTextCtrl(wx.stc.StyledTextCtrl):
    name = ""

    def __init__(self, parent, env):
        wx.stc.StyledTextCtrl.__init__(self, parent, pos=(-1, -1), size=(1, 1), style=wx.BORDER_NONE)
        self.env = env
        self._highlighted_lines = [None, None]
        self.UsePopUp(False)
        self.DefineMarkers()

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def OnContextMenu(self, evt):
        self.PopupMenu(edit_menu.Create())

    def DefineMarkers(self):
        self.MarkerDefine(MARKER_FIND, wx.stc.STC_MARK_BACKGROUND, background="#CCCCFF")
        self.MarkerDefine(MARKER_ERROR, wx.stc.STC_MARK_BACKGROUND, background="#FFCCCC")

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
        start, end = self.GetSelection()
        return start != end

    def CanFindNext(self):
        return bool(self.env.find_details and self.env.find_details.find)

    CanFindPrev = CanFindNext

    def IsEmpty(self):
        return self.GetTextLength() == 0

    def CentreLine(self, line):
        self.ScrollToLine(line - (self.LinesOnScreen() // 2))

    def SetCurrentLine(self, line):
        pos = self.PositionFromLine(line)
        self.SetSelection(pos, pos)
        self.CentreLine(line)

    def Unindent(self):
        start, end = self.GetSelection()
        self.BeginUndoAction()
        for line in xrange(self.LineFromPosition(start), self.LineFromPosition(end - 1) + 1):
            indent = self.GetLineIndentation(line)
            self.SetLineIndentation(line, indent - self.GetIndent())
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

        dlg = FindReplaceDialog(wx.GetApp().GetTopWindow(), self, self.name, find_details)
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
        dlg = GoToLineDialog(wx.GetApp().GetTopWindow(), self.name)
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