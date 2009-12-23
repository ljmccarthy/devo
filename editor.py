import wx
import wx.aui
import wx.stc
from async_wx import coroutine_method, WxScheduled

class Editor(wx.stc.StyledTextCtrl, WxScheduled):
    font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                   faceName="Monospace")
                   #faceName="Fixedsys Excelsior 3.01")

    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        self.StyleSetFont(0, self.font)
        self.path = ""
        self.LoadFile("test.txt")

    @coroutine_method
    def LoadFile(self, path):
        try:
            with (yield self.async_call(open, path)) as f:
                text = (yield self.async_call(f.read))
        except IOError, exn:
            print exn
        else:
            try:
                text = text.decode("utf-8")
            except UnicodeDecodeError:
                text = text.decode("iso-8859-1")
            self.SetText(text)
            self.path = path
