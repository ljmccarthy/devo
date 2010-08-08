import wx
from dialogs import dialogs
from dialog_util import bind_escape_key

class GoToLineDialog(wx.Dialog):
    def __init__(self, parent, filename="", details=None):
        title = "Go To Line"
        if filename:
            title += " [%s]" % filename

        wx.Dialog.__init__(self, parent, title=title)

        self.text = wx.TextCtrl(self, size=(100, -1))
        self.text.SetFocus()

        flags = wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_CENTRE_VERTICAL

        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        sizer.Add(self.text, 0, flags | wx.LEFT, 5)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        sizer.Add(btn_ok, 0, flags, 5)
        self.SetSizer(sizer)
        self.Fit()

        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateOK, id=wx.ID_OK)
        self.text.Bind(wx.EVT_CHAR, self.OnTextChar)
        bind_escape_key(self)

    def OnOK(self, evt):
        if self.GetLineNumber() is not None:
            evt.Skip()

    def OnUpdateOK(self, evt):
        evt.Enable(self.GetLineNumber() is not None)

    def OnTextChar(self, evt):
        key = evt.GetKeyCode()
        if ord('0') <= key <= ord('9') or key < ord(' ') or key >= 0x7F:
            evt.Skip()

    def GetLineNumber(self):
        try:
            linenum = int(self.text.GetValue())
            if linenum > 0:
                return linenum - 1
        except ValueError:
            pass
