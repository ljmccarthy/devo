import webbrowser
import wx

class HyperLinkCtrl(wx.Panel):
    def __init__(self, parent, id, label, url, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="hyperlink"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.url = url
        self.normal_cursor = self.GetCursor()

        if wx.Platform == "__WXMSW__":
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        self.label = wx.StaticText(self, label=label)
        self.label.SetForegroundColour(wx.BLUE)
        font = self.GetFont()
        font.SetUnderlined(True)
        self.label.SetFont(font)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.EXPAND)
        self.SetSizer(sizer)

        if wx.Platform != "__WXMSW__":
            self.Bind(wx.EVT_ENTER_WINDOW, self.__OnEnterWindow)
            self.Bind(wx.EVT_LEAVE_WINDOW, self.__OnLeaveWindow)
        else:
            self.label.Bind(wx.EVT_ENTER_WINDOW, self.__OnEnterWindow)
            self.label.Bind(wx.EVT_LEAVE_WINDOW, self.__OnLeaveWindow)

        self.label.Bind(wx.EVT_LEFT_UP, self.__OnLeftUp)

    def __OnEnterWindow(self, evt):
        self.label.SetForegroundColour(wx.RED)
        self.Refresh()
        wx.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

    def __OnLeaveWindow(self, evt):
        self.label.SetForegroundColour(wx.BLUE)
        self.Refresh()
        wx.SetCursor(self.normal_cursor)

    def __OnLeftUp(self, evt):
        webbrowser.open_new_tab(self.url)
