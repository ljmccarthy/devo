import os
import wx, wx.stc
from async import async_call, coroutine
from dialogs import dialogs
from fileutil import atomic_write_file, read_file
from find_replace_dialog import FindReplaceDialog
from go_to_line_dialog import GoToLineDialog
from menu_defs import edit_menu
from signal_wx import Signal
from syntax import filename_syntax_re, syntax_dict

if wx.Platform == "__WXMSW__":
    fontface = "Consolas"
else:
    fontface = "Monospace"

def decode_text(text):
    try:
        return text.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return text.decode("iso-8859-1"), "iso-8859-1"

def encode_text(text, encoding):
    try:
        return text.encode(encoding), encoding
    except UnicodeEncodeError:
        return text.encode("utf-8"), "utf-8"

class Editor(wx.stc.StyledTextCtrl):
    def __init__(self, parent, env, path=""):
        pre = wx.stc.PreStyledTextCtrl()
        pre.Hide()
        pre.Create(parent, size=wx.Size(1, 1), style=wx.BORDER_NONE)
        self.PostCreate(pre)
        self.UsePopUp(False)
        self.SetDropTarget(None)

        self.env = env
        self.path = path
        self.file_encoding = "utf-8"
        self.modified_externally = False
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

    def GetModify(self):
        return (not self.GetReadOnly()) and (
                self.modified_externally or super(Editor, self).GetModify())

    @property
    def modified(self):
        return self.GetModify()

    @property
    def title(self):
        path = os.path.basename(self.path) or "Untitled"
        return path + " *" if self.modified else path

    def CanCut(self):
        return not self.GetReadOnly() and self.CanCopy()

    def CanCopy(self):
        start, end = self.GetSelection()
        return start != end

    def SetModified(self):
        self.modified_externally = True
        self.sig_title_changed.signal(self)

    @coroutine
    def TryClose(self):
        if self.modified:
            result = dialogs.ask_save_changes(self, self.path)
            if result == wx.ID_YES:
                try:
                    save_result = (yield self.Save())
                    if save_result:
                        self.env.remove_monitor_path(self.path)
                    yield save_result
                except Exception:
                    yield False
            else:
                yield result == wx.ID_NO
        else:
            if self.path:
                self.env.remove_monitor_path(self.path)
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
            text = (yield async_call(read_file, path, "r"))
            text, self.file_encoding = decode_text(text)

            self.modified_externally = False
            self.SetReadOnly(False)
            self.SetSyntaxFromFilename(path)
            self.SetText(text)
            self.SetSavePoint()

            width = max(self.TextWidth(wx.stc.STC_STYLE_DEFAULT, line)
                             for line in text.split("\n"))
            self.SetScrollWidth(max(width, self.default_scroll_width))

            if old_path:
                self.env.remove_monitor_path(old_path)
            self.env.add_monitor_path(path)
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
            self.EmptyUndoBuffer()
            yield True
        except Exception, e:
            dialogs.error(self, "Error opening file:\n\n%s" % e)
            yield False

    @coroutine
    def Reload(self):
        line_num = self.GetFirstVisibleLine()
        yield self.LoadFile(self.path)
        self.ScrollToLine(line_num)

    @coroutine
    def SaveFile(self, path):
        text, self.file_encoding = encode_text(self.GetText(), self.file_encoding)
        if not text.endswith("\n"):
            text += "\n"
        yield async_call(atomic_write_file, path, text)
        self.modified_externally = False
        self.SetSavePoint()

    @coroutine
    def SaveAs(self):
        path = self.env.get_file_to_save()
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
                self.env.add_monitor_path(path)
                self.env.add_recent_file(path)
                self.sig_title_changed.signal(self)
                yield True
        yield False

    @coroutine
    def Save(self):
        if self.path:
            try:
                with self.env.updating_path(self.path):
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
        dlg = FindReplaceDialog(self, os.path.basename(self.path), self.env.find_details)
        try:
            dlg.ShowModal()
            self.env.find_details = dlg.GetFindDetails()
        finally:
            dlg.Destroy()

    def Find(self):
        selected = self.GetSelectedText().strip().split("\n")[0]
        if selected:
            self.env.find_details.find = selected
        self.DoFind()

    def FindNext(self):
        if self.CanFindNext():
            self.env.find_details.Find(self)

    def FindPrev(self):
        if self.CanFindPrev():
            self.env.find_details.Find(self, reverse=True)

    def CanFindNext(self):
        return self.env.find_details is not None

    CanFindPrev = CanFindNext

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
        for line in xrange(self.LineFromPosition(start), self.LineFromPosition(end - 1) + 1):
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
        elif self.modified:
            p["text"] = self.GetText()
        return p

    @coroutine
    def LoadPerspective(self, p):
        future = None
        if "text" in p:
            self.modified_externally = False
            self.SetSavePoint()
            self.SetText(p["text"])
        elif "path" in p:
            yield self.LoadFile(p["path"])
            self.EmptyUndoBuffer()
        self.ScrollToLine(p.get("line", 0))
        self.SetSelection(*p.get("selection", (0, 0)))
