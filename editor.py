import os
import shutil
import wx
import wx.aui
import wx.stc
from async_wx import async_call, coroutine
from find_replace_dialog import FindReplaceDialog
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu
from signal_wx import Signal
from syntax import filename_syntax_re, syntax_dict
import dialogs

if "wxMSW" in wx.PlatformInfo:
    fontface = "Courier New"
else:
    fontface = "Monospace"

class Editor(wx.stc.StyledTextCtrl):
    def __init__(self, parent, env, path=""):
        wx.stc.StyledTextCtrl.__init__(self, parent, style=wx.BORDER_NONE)
        self.env = env
        self.path = path
        self.find_details = None
        self.sig_title_changed = Signal(self)

        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
        self.SetWhitespaceForeground(True, "#dddddd")
        self.SetNullSyntax()

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
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
            self.path = path
        finally:
            self.Enable()
            self.SetReadOnly(False)
            self.sig_title_changed.signal(self)

    @coroutine
    def SaveFile(self, path):
        text = self.GetText().encode("utf-8")
        if not text.endswith("\n"):
            text += "\n"
        temp = os.path.join(os.path.dirname(path), ".tmpsave." + os.path.basename(path))
        try:
            with (yield async_call(open, temp, "wb")) as out:
                try:
                    yield async_call(shutil.copystat, path, temp)
                except OSError:
                    pass
                yield async_call(out.write, text)
        except IOError:
            try:
                yield async_call(os.remove, temp)
            except OSError:
                pass
            raise
        else:
            yield async_call(os.rename, temp, path)
            self.SetSavePoint()

    @coroutine
    def SaveAs(self):
        path = dialogs.get_file_to_save(self)
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

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        mod = evt.GetModifiers()
        if mod == wx.MOD_NONE:
            if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
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
        else:
            evt.Skip()

    def OnContextMenu(self, evt):
        self.PopupMenu(edit_menu.Create())

    def OnSavePointLeft(self, evt):
        self.sig_title_changed.signal(self)

    def OnSavePointReached(self, evt):
        self.sig_title_changed.signal(self)

    def Find(self):
        dlg = FindReplaceDialog(self, os.path.basename(self.path), self.find_details)
        try:
            dlg.ShowModal()
            self.find_details = dlg.GetFindDetails()
        finally:
            dlg.Destroy()

    def FindNext(self):
        if self.find_details is not None:
            self.find_details.Find(self)

    def GoToLine(self):
        dlg = GoToLineDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.GotoLine(dlg.GetLineNumber())
        finally:
            dlg.Destroy()
