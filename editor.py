import os
import shutil
import wx
import wx.aui
import wx.stc
from async_wx import async_call, coroutine
from signal_wx import Signal
from syntax import filename_syntax_re, syntax_dict
import dialogs

if "wxMSW" in wx.PlatformInfo:
    font_face = "Consolas"
else:
    font_face = "Monospace"

class Editor(wx.stc.StyledTextCtrl):
    font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                   faceName=font_face)

    def __init__(self, parent, env):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        self.env = env
        self.path = ""
        self.loading = ""

        self.SetNullSyntax()
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)
        self.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
        self.SetWhitespaceForeground(True, "#dddddd")

        self.sig_set_title = Signal(self)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTLEFT, self.OnSavePointLeft)
        self.Bind(wx.stc.EVT_STC_SAVEPOINTREACHED, self.OnSavePointReached)

    def SetNullSyntax(self):
        self.SetLexer(wx.stc.STC_LEX_NULL)
        self.SetKeyWords(0, "")
        self.StyleClearAll()
        self.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, self.font)
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
        self.SetIndent(4)
        self.SetTabWidth(8)
        self.SetUseTabs(False)

    def SetSyntaxFromFilename(self, path):
        m = filename_syntax_re.match(os.path.basename(path))
        if m:
            syntax = syntax_dict[m.lastgroup]
            self.SetLexer(syntax.lexer)
            self.SetKeyWords(0, syntax.keywords)
            self.StyleClearAll()
            for style_num, spec in syntax.stylespecs:
                self.StyleSetFont(style_num, self.font)
                self.StyleSetSpec(style_num, spec)
            self.SetIndent(syntax.indent)
            self.SetTabWidth(syntax.indent if syntax.use_tabs else 8)
            self.SetUseTabs(syntax.use_tabs)
        else:
            self.SetNullSyntax()

    @coroutine
    def LoadFile(self, path):
        self.SetReadOnly(True)
        try:
            self.loading = path
            self.sig_set_title.signal(self)
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
            self.loading = ""
            self.SetReadOnly(False)
            self.sig_set_title.signal(self)

    @coroutine
    def SaveFile(self, path):
        text = self.GetText().encode("utf-8")
        temp = os.path.join(os.path.dirname(path), ".tmpsave." + os.path.basename(path))
        try:
            with (yield async_call(open, temp, "wb")) as out:
                yield async_call(shutil.copystat, path, temp)
                yield async_call(out.write, text)
        except IOError:
            yield async_call(os.remove, temp)
            raise
        else:
            yield async_call(os.rename, temp, path)
            self.SetSavePoint()

    def SaveAs(self):
        path = dialogs.get_file_to_open(self)
        if path:
            try:
                self.SaveFile(path)
            except Exception, exn:
                dialogs.error(self, "Error saving file '%s'\n\n%s" % (path, exn))
            else:
                self.path = path
                self.sig_set_title.signal(self)

    def Save(self):
        if self.path:
            try:
                self.SaveFile(self.path)
            except Exception, exn:
                dialogs.error(self, str(exn))
        else:
            self.SaveAs()

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
        elif mod == wx.MOD_CONTROL:
            if key == ord('X'):
                self.Cut()
            elif key == ord('C'):
                self.Copy()
            elif key == ord('V'):
                self.Paste()
            elif key == ord('S'):
                self.Save()
            else:
                evt.Skip()
        else:
            evt.Skip()

    def GetTitle(self):
        path = os.path.basename(self.path) or "Untitled"
        if self.loading:
            return "Loading %s..." % path
        elif (not self.GetReadOnly()) and self.GetModify():
            return path + " *"
        else:
            return path

    def OnSavePointLeft(self, evt):
        self.sig_set_title.signal(self)

    def OnSavePointReached(self, evt):
        self.sig_set_title.signal(self)
