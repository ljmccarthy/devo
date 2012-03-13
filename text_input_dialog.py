import wx

class TextInputDialog(wx.Dialog):
    def __init__(self, parent, title="", message="", value="", width=300):
        wx.Dialog.__init__(self, parent, title=title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        if message:
            label = wx.StaticText(self, label=message)
            sizer.Add(label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.textctrl = wx.TextCtrl(self, size=(width, -1), value=value)
        sizer.Add(self.textctrl, 0, wx.ALL | wx.EXPAND, 5)
        btnsizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.textctrl.SetFocus()

    def GetValue():
        return self.textctrl.GetValue()
