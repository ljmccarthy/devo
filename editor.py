import os
import wx, wx.stc
from async_wx import async_call, coroutine
from fileutil import atomic_write_file
from find_replace_dialog import FindReplaceDialog, FindReplaceDetails
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu
from signal_wx import Signal
from syntax import filename_syntax_re, syntax_dict
import dialogs

if wx.Platform == "__WXMSW__":
    fontface = "Courier New"
else:
    fontface = "Monospace"

class Editor(wx.stc.StyledTextCtrl):
    def __init__(self, parent, env, path=""):
        pre = wx.stc.PreStyledTextCtrl()
        pre.Hide()
        pre.Create(parent, size=wx.Size(1, 1), style=wx.BORDER_NONE)
        self.PostCreate(pre)
        self.SetDropTarget(None)

        self.env = env
        self.path = path
        self.find_details = FindReplaceDetails("", "")
        self.sig_title_changed = Signal(self)

        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
        self.SetWhitespaceForeground(True, "#dddddd")
        self.SetNullSyntax()

        self.default_scroll_width = self.TextWidth(wx.stc.STC_STYLE_DEFAULT, "W")
        self.SetScrollWidth(self.default_scroll_width)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTLEFT, self.OnSavePointLeft)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTREACHED, self.OnSavePointReached)

    @property
    def changed(self):
        return (not self.GetReadOnly()) and self.GetModify()

    @property
    def title(self):
        path = os.path.basename(self.path) or "Untitled"
        if self.changed:
            return path + " *"
        else:
            return path

    @coroutine
    def TryClose(self):
        if self.changed:
            result = dialogs.ask_save_changes(self, self.path)
            if result == wx.ID_YES:
                try:
                    yield (yield self.Save())
                except Exception:
                    yield False
            else:
                yield result == wx.ID_NO
        else:
            yield True

    def SetNullSyntax(self):
        self.ClearDocumentStyle()
        self.SetLexer(wx.stc.STC_LEX_NULL)
        self.SetKeyWords(0, "")
        self.StyleResetDefault()
        self.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, 10, fontface, False, False, False)
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
        self.StyleClearAll()
        self.SetIndent(4)
        self.SetTabWidth(8)
        self.SetUseTabs(False)

    def SetSyntaxFromFilename(self, path):
        m = filename_syntax_re.match(os.path.basename(path))
        if m:
            syntax = syntax_dict[m.lastgroup]
            self.ClearDocumentStyle()
            self.SetLexer(syntax.lexer)
            self.SetKeyWords(0, syntax.keywords)
            self.StyleResetDefault()
            self.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, 10, fontface, False, False, False)
            self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
            self.StyleClearAll()
            for style_num, spec in syntax.stylespecs:
                self.StyleSetSpec(style_num, spec)
            self.SetIndent(syntax.indent)
            self.SetTabWidth(syntax.indent if syntax.use_tabs else 8)
            self.SetUseTabs(syntax.use_tabs)
            self.Colourise(0, -1)
        else:
            self.SetNullSyntax()

    @coroutine
    def LoadFile(self, path):
        self.SetReadOnly(True)
        self.Disable()
        old_path = self.path
        self.path = path
        self.sig_title_changed.signal(self)
        try:
            with (yield async_call(open, path)) as f:
                text = (yield async_call(f.read))
            try:
                text = text.decode("utf-8")
            except UnicodeDecodeError:
                text = text.decode("iso-8859-1")
            self.SetReadOnly(False)
            self.SetSyntaxFromFilename(path)
            self.SetText(text)
            self.EmptyUndoBuffer()
            self.SetSavePoint()

            width = max(self.TextWidth(wx.stc.STC_STYLE_DEFAULT, line)
                             for line in text.split("\n"))
            self.SetScrollWidth(max(width, self.default_scroll_width))
        except:
            self.path = old_path
            self.sig_title_changed.signal(self)
            raise
        finally:
            self.Enable()
            self.SetReadOnly(False)

    @coroutine
    def TryLoadFile(self, path):
        try:
            yield self.LoadFile(path)
            yield True
        except Exception, e:
            dialogs.error(self, "Error opening file:\n\n%s" % e)
            yield False

    @coroutine
    def SaveFile(self, path):
        text = self.GetText().encode("utf-8")
        if not text.endswith("\n"):
            text += "\n"
        yield async_call(atomic_write_file, path, text)
        self.SetSavePoint()

    @coroutine
    def SaveAs(self):
        path = dialogs.get_file_to_save(self, context="save")
        if path:
            path = os.path.realpath(path)
            try:
                yield self.SaveFile(path)
            except Exception, exn:
                dialogs.error(self, "Error saving file '%s'\n\n%s" % (path, exn))
                raise
            else:
                self.SetSyntaxFromFilename(path)
                self.path = path
                self.sig_title_changed.signal(self)
                yield True
        yield False

    @coroutine
    def Save(self):
        if self.path:
            try:
                yield self.SaveFile(self.path)
                yield True
            except Exception, exn:
                dialogs.error(self, "Error saving file '%s'\n\n%s" % (self.path, exn))
                raise
        else:
            yield (yield self.SaveAs())

    def OnReturnKeyDown(self, evt):
        start, end = self.GetSelection()
        if start == end:
            indent = self.GetLineIndentation(self.GetCurrentLine())
            pos = self.GetCurrentPos()
            if self.GetUseTabs():
                indent //= self.GetTabWidth()
                self.InsertText(pos, "\n" + "\t" * indent)
            else:
                self.InsertText(pos, "\n" + " " * indent)
            self.GotoPos(pos + indent + 1)
        else:
            evt.Skip()

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        mod = evt.GetModifiers()
        if mod == wx.MOD_NONE:
            if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
                self.OnReturnKeyDown(evt)
            else:
                evt.Skip()
        else:
            evt.Skip()

    def OnRightDown(self, evt):
        start, end = self.GetSelection()
        if start == end:
            pos = self.PositionFromPoint(evt.GetPosition())
            self.SetSelection(pos, pos)
            self.SetCurrentPos(pos)
        evt.Skip()

    def OnContextMenu(self, evt):
        self.PopupMenu(edit_menu.Create())

    def OnSavePointLeft(self, evt):
        self.sig_title_changed.signal(self)

    def OnSavePointReached(self, evt):
        self.sig_title_changed.signal(self)

    def DoFind(self):
        dlg = FindReplaceDialog(self, os.path.basename(self.path), self.find_details)
        try:
            dlg.ShowModal()
            self.find_details = dlg.GetFindDetails()
        finally:
            dlg.Destroy()

    def Find(self):
        selected = self.GetSelectedText().strip().split("\n")[0]
        if selected:
            self.find_details.find = selected
        self.DoFind()

    def FindNext(self):
        if self.CanFindNext():
            self.find_details.Find(self)

    def CanFindNext(self):
        return self.find_details is not None

    def GoToLine(self):
        dlg = GoToLineDialog(self, os.path.basename(self.path))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.GotoLine(dlg.GetLineNumber())
        finally:
            dlg.Destroy()

    def Unindent(self):
        start, end = self.GetSelection()
        self.BeginUndoAction()
        for line in xrange(self.LineFromPosition(start), self.LineFromPosition(end) + 1):
            indent = self.GetLineIndentation(line)
            self.SetLineIndentation(line, indent - self.GetIndent())
        self.EndUndoAction()

    def SavePerspective(self):
        p = {
            "line"      : self.GetFirstVisibleLine(),
            "selection" : self.GetSelection(),
        }
        if self.path:
            p["path"] = self.path
        elif self.changed:
            p["text"] = self.GetText()
        return p

    def LoadPerspective(self, p):
        future = None
        if "text" in p:
            self.SetSavePoint()
            self.EmptyUndoBuffer()
            self.SetText(p["text"])
        elif "path" in p:
            future = self.LoadFile(p["path"])
        self.ScrollToLine(p.get("line", 0))
        self.SetSelection(*p.get("selection", (0, 0)))
        return future
