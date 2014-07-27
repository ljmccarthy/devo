import wx, wx.html

class HtmlFrame(wx.Frame):
    def __init__(self, parent, page="", title="", pos=wx.DefaultPosition, size=wx.DefaultSize):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        if size == wx.DefaultSize:
            size = (500, 300)
        wx.Frame.__init__(self, parent, title=title, pos=pos, size=size, style=style)
        self.html = wx.html.HtmlWindow(self)
        self.html.SetPage(page)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetMinSize((100, 100))

if __name__ == "__main__":
    app = wx.App()
    dlg = HtmlFrame(None, "<h1>Hello, <i>World</i></h1>", title="Hello")
    dlg.Show()
    app.MainLoop()
