import os
import wx, wx.stc
from async import async_call, coroutine
from dialogs import dialogs
from fileutil import atomic_write_file, read_file, mkpath
from signal_wx import Signal
from styled_text_ctrl import StyledTextCtrl
from util import clean_text

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

class Editor(StyledTextCtrl, wx.FileDropTarget):
    def __init__(self, parent, env, path=""):
        StyledTextCtrl.__init__(self, parent, env)
        wx.FileDropTarget.__init__(self)
        self.SetDropTarget(None)

        self.path = path
        self.file_encoding = "utf-8"
        self.modified_externally = False
        self.static_title = None

        self.sig_title_changed = Signal(self)
        self.sig_status_changed = Signal(self)

        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
        self.SetWhitespaceForeground(True, "#dddddd")

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTLEFT, self.OnSavePointLeft)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTREACHED, self.OnSavePointReached)
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnStcUpdateUI)

    def GetModify(self):
        return (not self.GetReadOnly()) and (
                self.modified_externally or super(Editor, self).GetModify())

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def modified(self):
        return self.GetModify()

    @property
    def title(self):
        if self.static_title is not None:
            return self.static_title
        path = os.path.basename(self.path) or "Untitled"
        return path + " *" if self.modified else path

    @property
    def status_text(self):
        return "Line %d, Column %d" % (
            self.GetCurrentLine() + 1, self.GetColumn(self.GetCurrentPos()) + 1)
            
    @coroutine
    def OnModifiedExternally(self):
        if dialogs.ask_reload(self, os.path.basename(self.path)):
            yield self.Reload()
        else:
            self.SetModified()

    @coroutine
    def OnUnloadedExternally(self):
        if os.path.exists(self.path):
            if dialogs.ask_reload(self, os.path.basename(self.path)):
                yield self.Reload()                        
            else:
                self.SetModified()
        else:
            if dialogs.ask_unload(self, os.path.basename(self.path)):
                yield self.env.close_view(self)
            else:
                self.SetModified()

    @property
    def status_text_path(self):
        return self.static_title or self.path or "Untitled"

    def SetModified(self):
        self.modified_externally = True
        self.sig_title_changed.signal(self)

    @coroutine
    def TryClose(self):
        if self.modified:
            result = dialogs.ask_save_changes(wx.GetApp().GetTopWindow(), self.path)
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

    def SetStatic(self, title, text):
        self.static_title = title
        self.path = ""
        self.SetText(text)
        self.SetSavePoint()
        self.EmptyUndoBuffer()
        self.SetReadOnly(True)
        self.sig_title_changed.signal(self)
        self.sig_status_changed.signal(self)

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
            text = clean_text(text)

            self.modified_externally = False
            self.SetReadOnly(False)
            self.SetSyntaxFromFilename(path)
            self.SetText(text)
            self.SetSavePoint()

            if old_path:
                self.env.remove_monitor_path(old_path)
            self.env.add_monitor_path(path)
        except:
            self.path = old_path
            self.sig_title_changed.signal(self)
            self.sig_status_changed.signal(self)
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
        text = clean_text(text)
        if not text.endswith("\n"):
            text += "\n"
        yield async_call(mkpath, os.path.dirname(path))
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
                self.static_title = None
                self.env.add_monitor_path(path)
                self.env.add_recent_file(path)
                self.sig_title_changed.signal(self)
                self.sig_status_changed.signal(self)
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

    def OnSavePointLeft(self, evt):
        self.sig_title_changed.signal(self)

    def OnSavePointReached(self, evt):
        self.sig_title_changed.signal(self)

    def OnStcUpdateUI(self, evt):
        self.sig_status_changed.signal(self)

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            self.env.open_file(filename)
        return True

    def SavePerspective(self):
        p = {
            "line"      : self.GetFirstVisibleLine(),
            "selection" : self.GetSelection(),
            "view_type" : "editor",
        }
        if self.path:
            p["path"] = self.path
        else:
            p["text"] = self.GetText()
            if self.static_title is not None:
                p["static_title"] = self.static_title
        return p

    @coroutine
    def LoadPerspective(self, p):
        if "text" in p:
            self.modified_externally = False
            static_title = p.get("static_title")
            if static_title is None:
                self.SetSavePoint()
                self.SetText(p["text"])
            else:
                self.SetStatic(static_title, p["text"])

        elif "path" in p:
            yield self.LoadFile(p["path"])
            self.EmptyUndoBuffer()

        self.ScrollToLine(p.get("line", 0))
        self.SetSelection(*p.get("selection", (0, 0)))
