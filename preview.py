import wx
from async import coroutine
from signal_wx import Signal

class Preview(wx.Panel):
    def __init__(self, parent, env):
        wx.Panel.__init__(self, parent)

        self.env = env
        self.current = ""
        self.sig_title_changed = Signal()
        self.sig_status_changed = Signal()

        import wx.html2 as webview
        self.wv = webview.WebView.New(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(self, -1, "<--", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnPrevPageButton, btn)
        btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckCanGoBack, btn)

        btn = wx.Button(self, -1, "-->", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnNextPageButton, btn)
        btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckCanGoForward, btn)

        btn = wx.Button(self, -1, "Stop", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnStopButton, btn)
        btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

        btn = wx.Button(self, -1, "Refresh", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.OnRefreshPageButton, btn)
        btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

        self.location = wx.ComboBox(
            self, -1, "", style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_COMBOBOX, self.OnLocationSelect, self.location)
        self.location.Bind(wx.EVT_TEXT_ENTER, self.OnLocationEnter)
        btnSizer.Add(self.location, 1, wx.EXPAND|wx.ALL, 2)

        sizer.Add(btnSizer, 0, wx.EXPAND)
        sizer.Add(self.wv, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(webview.EVT_WEBVIEW_NAVIGATING, self.OnWebViewNavigating, self.wv)
        self.Bind(webview.EVT_WEBVIEW_LOADED, self.OnWebViewLoaded, self.wv)
        self.Bind(webview.EVT_WEBVIEW_TITLE_CHANGED, self.OnWebViewTitleChanged, self.wv)

    @property
    def path(self):
        return self.current and self.current[len('file://'):]

    @property
    def modified(self):
        return False

    @property
    def title(self):
        return self.wv.GetCurrentTitle() or self.wv.GetCurrentURL()

    @property
    def status_text(self):
        return self.title

    @property
    def status_text_path(self):
        return self.title

    @path.setter
    def path(self, p):
        oldpath = self.path
        if oldpath:
            self.env.remove_monitor_path(oldpath)
        self.env.add_monitor_path(p)
        self.wv.LoadURL('file://' + p)

    @coroutine
    def TryClose(self):
        yield True

    def SavePerspective(self):
        return dict(
            view_type = "preview",
            path = self.path,
        )

    @coroutine
    def LoadPerspective(self, p):
        path = p.get("path", "")
        os.stat(path)  # check it exists
        self.path = path
        yield

    @coroutine
    def OnModifiedExternally(self):
        self.wv.Reload()
        yield

    @coroutine
    def OnUnloadedExternally(self):
        yield

    def OnWebViewNavigating(self, evt):
        pass # to stop it navigating:   evt.Veto()

    def OnWebViewTitleChanged(self, evt):
        self.sig_title_changed.signal(self)

    def OnWebViewLoaded(self, evt):
        self.current = evt.GetURL()
        self.location.SetValue(self.current)
        self.sig_title_changed.signal(self)

    def OnLocationSelect(self, evt):
        url = self.location.GetStringSelection()
        self.log.write('OnLocationSelect: %s\n' % url)
        self.wv.LoadURL(url)

    def OnLocationEnter(self, evt):
        url = self.location.GetValue()
        self.location.Append(url)
        self.wv.LoadURL(url)

    def OnOpenButton(self, event):
        url = dialogs.get_text_input(self, "Open Location", "Enter a full URL or local path", self.current)
        if url:
            self.current = url
            self.wv.LoadURL(self.current)

    def OnPrevPageButton(self, event):
        self.wv.GoBack()

    def OnNextPageButton(self, event):
        self.wv.GoForward()

    def OnCheckCanGoBack(self, event):
        event.Enable(self.wv.CanGoBack())

    def OnCheckCanGoForward(self, event):
        event.Enable(self.wv.CanGoForward())

    def OnStopButton(self, evt):
        self.wv.Stop()

    def OnRefreshPageButton(self, evt):
        self.wv.Reload()

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.FRAME_EX_METAL)
    wnd = Preview(frame, None)
    frame.Show()
    app.MainLoop()
