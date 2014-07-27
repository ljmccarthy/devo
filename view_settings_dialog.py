import wx

view_modes = [
    ("Remember previous size and position", "previous"),
    ("Start on left side of screen", "left"),
    ("Start on right side of screen", "right"),
]

view_mode_indices = {x[1]: i for i, x in enumerate(view_modes)}

class ViewSettingsDialog(wx.Dialog):
    def __init__(self, parent, settings={}):
        wx.Dialog.__init__(self, parent, title="View Settings")

        self.choice_start_mode = wx.Choice(self, choices=list(x[0] for x in view_modes))
        self.choice_start_mode.Select(view_mode_indices.get(settings.get("window_start_mode", "previous"), 0))

        self.spin_width = wx.SpinCtrl(self, min=100, max=65535, value=str(settings.get("window_start_width", 1200)))
        self.check_remember_width = wx.CheckBox(self, label="Remember last width")
        self.check_remember_width.SetValue("window_start_width" not in settings)
        self.OnUpdateControls(None)

        width_sizer = wx.BoxSizer(wx.HORIZONTAL)
        width_sizer.Add(self.spin_width, 0, wx.ALIGN_CENTER_VERTICAL)
        width_sizer.AddSpacer(5)
        width_sizer.Add(self.check_remember_width, 0, wx.ALIGN_CENTER_VERTICAL)

        sb_window = wx.StaticBoxSizer(wx.StaticBox(self, label="Window"), wx.VERTICAL)
        sb_window.Add(self.choice_start_mode, 0, wx.EXPAND|wx.ALL, 5)
        sb_window.Add(width_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btn_sizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sb_window, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()

        self.Bind(wx.EVT_CHOICE, self.OnUpdateControls, self.choice_start_mode)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateControls, self.check_remember_width)

    def OnUpdateControls(self, evt):
        enable_width = self.choice_start_mode.Selection != 0
        self.spin_width.Enable(enable_width and not self.check_remember_width.Value)
        self.check_remember_width.Enable(enable_width)

    def UpdateSettings(self, settings):
        settings["window_start_mode"] = view_modes[self.choice_start_mode.Selection][1]
        if self.choice_start_mode.Selection != 0 and not self.check_remember_width.Value:
            settings["window_start_width"] = self.spin_width.GetValue()
        elif "window_start_width" in settings:
            del settings["window_start_width"]

if __name__ == "__main__":
    app = wx.App()
    dlg = ViewSettingsDialog(None)
    if dlg.ShowModal() == wx.ID_OK:
        print dlg.GetSettings()
