import wx, wx.html

class HtmlPopup(wx.PopupWindow):
    def __init__(self, parent, page="", pos=wx.DefaultPosition, size=wx.DefaultSize):
        if size == wx.DefaultSize:
            size = (500, 300)
        super(HtmlPopup, self).__init__(parent)
        self.SetPosition(pos)
        self.SetSize(size)
        self.SetMinSize((100, 100))

        self.html = wx.html.HtmlWindow(self)
        self.html.SetPage(page)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html, 1, wx.EXPAND|wx.ALL, 1)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        width, height = self.ClientSize
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        dc.Clear()
        dc.SetPen(wx.BLACK_PEN)
        dc.DrawRectangle(0, 0, width, height)
        dc.EndDrawing()

if __name__ == "__main__":
    app = wx.App()
    dlg = HtmlPopup(None, "<h1>Hello, <i>World</i></h1>")
    dlg.Show()
    app.MainLoop()
