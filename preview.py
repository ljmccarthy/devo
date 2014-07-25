import wx
from async import coroutine
from signal_wx import Signal

def is_preview_available():
    try:
        import wx.html2
        return True
    except ImportError as e:
        return False

class Preview(wx.Panel):
    def __init__(self, parent, env, url="", show_browser_ui=True):
        wx.Panel.__init__(self, parent)

        self.env = env
        self.show_browser_ui = show_browser_ui
        self.sig_title_changed = Signal()
        self.sig_status_changed = Signal()

        import wx.html2 as webview
        self.wv = webview.WebView.New(self, url=url)

        sizer = wx.BoxSizer(wx.VERTICAL)

        if show_browser_ui:
            btnSizer = wx.BoxSizer(wx.HORIZONTAL)

            btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_GO_BACK))
            self.Bind(wx.EVT_BUTTON, self.OnBack, btn)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_Back, btn)
            btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

            btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD))
            self.Bind(wx.EVT_BUTTON, self.OnForward, btn)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_Forward, btn)
            btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

            if wx.Platform == "__WXGTK__":
                btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap("gtk-stop"))
            else:
                btn = wx.Button(self, label="Stop", style=wx.BU_EXACTFIT)
            self.Bind(wx.EVT_BUTTON, self.OnStop, btn)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_Stop, btn)
            btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

            if wx.Platform == "__WXGTK__":
                btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap("gtk-refresh"))
            else:
                btn = wx.Button(self, label="Refresh", style=wx.BU_EXACTFIT)
            self.Bind(wx.EVT_BUTTON, self.OnRefresh, btn)
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_Refresh, btn)
            btnSizer.Add(btn, 0, wx.EXPAND|wx.ALL, 2)

            self.location = wx.ComboBox(self, value=url, style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
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
    def url(self):
        return self.wv.GetCurrentURL()

    @url.setter
    def url(self, url):
        self.wv.LoadURL(url)

    @property
    def path(self):
        url = self.url
        return url[len("file://"):] if url.startswith("file://") else ""

    @path.setter
    def path(self, p):
        oldpath = self.path
        if oldpath:
            self.env.remove_monitor_path(oldpath)
        self.env.add_monitor_path(p)
        self.wv.LoadURL("file://" + p)

    @property
    def modified(self):
        return False

    @property
    def title(self):
        return (self.wv.GetCurrentTitle()
                or self.path
                or self.url
                or ("Loading..." if self.wv.IsBusy() else "..."))

    @property
    def status_text(self):
        return self.title

    @property
    def status_text_path(self):
        return self.title

    @coroutine
    def TryClose(self):
        yield True

    def SavePerspective(self):
        p = dict(view_type="preview")
        path = self.path
        if path:
            p["path"] = path
        else:
            p["url"] = self.url
        return p

    @coroutine
    def LoadPerspective(self, p):
        if "path" in p:
            self.path = p["path"]
        elif "url" in p:
            self.url = p["url"]
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
        if self.show_browser_ui:
            self.location.SetValue(self.current)
        self.sig_title_changed.signal(self)

    def OnLocationSelect(self, evt):
        url = self.location.GetStringSelection()
        self.log.write("OnLocationSelect: %s\n" % url)
        self.wv.LoadURL(url)

    def OnLocationEnter(self, evt):
        url = self.location.GetValue()
        self.location.Append(url)
        self.wv.LoadURL(url)

    def OnOpenButton(self, evt):
        url = dialogs.get_text_input(self, "Open Location", "Enter a full URL or local path", self.current)
        if url:
            self.current = url
            self.wv.LoadURL(self.current)

    def OnBack(self, evt):
        self.wv.GoBack()

    def OnForward(self, evt):
        self.wv.GoForward()

    def OnStop(self, evt):
        self.wv.Stop()

    def OnRefresh(self, evt):
        self.wv.Reload()

    def OnUpdateUI_Back(self, evt):
        evt.Enable(self.wv.CanGoBack())

    def OnUpdateUI_Forward(self, evt):
        evt.Enable(self.wv.CanGoForward())

    def OnUpdateUI_Stop(self, evt):
        evt.Enable(self.wv.IsBusy())

    def OnUpdateUI_Refresh(self, evt):
        evt.Enable(not self.wv.IsBusy())

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.FRAME_EX_METAL)
    wnd = Preview(frame, None)
    frame.Show()
    app.MainLoop()
