import os
import wx
import wx.aui
import wx.stc
from async_wx import coroutine_method, WxScheduled
from syntax import filename_syntax_re, syntax_dict

class Editor(wx.stc.StyledTextCtrl, WxScheduled):
    font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                   faceName="Monospace")
                   #faceName="Fixedsys Excelsior 3.01")

    def __init__(self, parent, env):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        self.env = env
        self.path = ""

        self.SetNullSyntax()
        self.SetTabIndents(True)
        self.SetBackSpaceUnIndents(True)

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
        self.SetTabWidth(4)
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
            self.SetTabWidth(syntax.indent)
            self.SetUseTabs(syntax.use_tabs)
        else:
            self.SetNullSyntax()

    @coroutine_method
    def LoadFile(self, path):
        self.SetReadOnly(True)
        try:
            with (yield self.async_call(open, path)) as f:
                text = (yield self.async_call(f.read))
        except IOError, exn:
            self.SetReadOnly(False)
            print exn
        else:
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

    def OnKeyDown(self, evt):
        key = evt.GetKeyCode()
        mod = evt.GetModifiers()
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and mod == wx.MOD_NONE:
            indent = self.GetLineIndentation(self.GetCurrentLine())
            pos = self.GetCurrentPos()
            self.InsertText(pos, "\n" + " " * indent)
            self.GotoPos(pos + indent + 1)
        else:
            evt.Skip()

    def OnSavePointLeft(self, evt):
        pass

    def OnSavePointReached(self, evt):
        pass
