import wx
import wx.html2 as webview
from async import coroutine
from signal_wx import Signal

class Preview(wx.Panel):
    def __init__(self, parent, env):
        wx.Panel.__init__(self, parent, -1)
        self.env = env

        self.current = ""
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.wv = webview.WebView.New(self)
        self.Bind(webview.EVT_WEB_VIEW_NAVIGATING, self.OnWebViewNavigating, self.wv)
        self.Bind(webview.EVT_WEB_VIEW_LOADED, self.OnWebViewLoaded, self.wv)
        self.Bind(webview.EVT_WEB_VIEW_TITLE_CHANGED, self.OnWebViewTitleChanged, self.wv)
        
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
        
        self.sig_title_changed = Signal()
        self.sig_status_changed = Signal()
        
    @coroutine
    def TryClose(self):
        yield True

    def SavePerspective(self):
        return dict(
            view_type="preview",
            path = self.path,
        )
        
    @coroutine
    def LoadPerspective(self, p):
        path = p.get("path", "")
        os.stat(path)  # check it exists
        self.path = path
        yield        
        
    @property
    def path(self):
        return self.current and self.current[len('file://'):]
        
    @property 
    def modified(self):
        return False
    
    @path.setter
    def path(self, p):
        oldpath = self.path
        if oldpath:
            self.env.remove_monitor_path(oldpath)
        self.env.add_monitor_path(p)
        self.wv.LoadURL('file://' + p)
        
    @coroutine
    def OnModifiedExternally(self):
        self.wv.Reload()
        yield
        
    @coroutine
    def OnUnloadedExternally(self):
        yield
        
    @property
    def title(self):
        return self.wv.GetCurrentTitle()

    @property
    def status_text(self):
        return self.title
        
    @property
    def status_text_path(self):
        return self.title

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
        dlg = wx.TextEntryDialog(self, "Open Location",
                                "Enter a full URL or local path",
                                self.current, wx.OK|wx.CANCEL)
        dlg.CentreOnParent()

        if dlg.ShowModal() == wx.ID_OK:
            self.current = dlg.GetValue()
            self.wv.LoadURL(self.current)

        dlg.Destroy()

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
