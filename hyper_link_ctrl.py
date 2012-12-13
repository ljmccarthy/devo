import webbrowser
import wx

class HyperLinkCtrl(wx.Panel):
    def __init__(self, parent, id, label, url, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name="hyperlink"):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.url = url
        self.normal_cursor = self.GetCursor()

        self.label = wx.StaticText(self, label=url)
        self.label.SetForegroundColour(wx.BLUE)
        fontsize = self.label.GetFont().PointSize
        self.label.SetFont(wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, underline=True))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_ENTER_WINDOW, self.__OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.__OnLeaveWindow)
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
