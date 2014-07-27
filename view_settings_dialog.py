import wx

view_modes = [
    ("Remember previous size and position", "previous"),
    ("Start on left side of screen", "left"),
    ("Start on right side of screen", "right"),
]

view_mode_indices = {x[1]: i for i, x in enumerate(view_modes)}

def font_style_string(font):
    font_style = []
    if font.Weight == wx.FONTWEIGHT_BOLD:
        font_style.append("Bold")
    if font.Style in (wx.FONTSTYLE_ITALIC, wx.FONTSTYLE_SLANT):
        font_style.append("Italic")
    return " ".join(font_style)

def font_style_string_to_style(font_style):
    return wx.FONTSTYLE_ITALIC if "Italic" in font_style else wx.FONTSTYLE_NORMAL

def font_style_string_to_weight(font_style):
    return wx.FONTWEIGHT_BOLD if "Bold" in font_style else wx.FONTWEIGHT_NORMAL

platform_font_defaults = {
    "__WXMSW__": ("Consolas", 10),
    "__WXMAC__": ("Menlo Regular", 12),
}

def get_font_from_settings(settings):
    font_face, font_size = platform_font_defaults.get(wx.Platform, ("Monospace", 10))
    try:
        font_size = int(settings.get("font_size", font_size))
    except ValueError:
        pass
    return wx.Font(font_size, wx.FONTFAMILY_TELETYPE,
        font_style_string_to_style(settings.get("font_style", "")),
        font_style_string_to_weight(settings.get("font_style", "")),
        faceName = settings.get("font_face", font_face))

class ViewSettingsDialog(wx.Dialog):
    def __init__(self, parent, settings={}):
        wx.Dialog.__init__(self, parent, title="View Settings")

        self.label_font = wx.StaticText(self, label="Font")
        self.btn_font = wx.Button(self, label="Change Font...")
        self.SetSelectedFont(get_font_from_settings(settings))

        self.choice_start_mode = wx.Choice(self, choices=list(x[0] for x in view_modes))
        self.choice_start_mode.Select(view_mode_indices.get(settings.get("window_start_mode", "previous"), 0))

        display_rect = wx.Display(wx.Display.GetFromWindow(parent)).GetClientArea()
        self.spin_width = wx.SpinCtrl(self, min=100, max=display_rect.width, value=str(settings.get("window_start_width", 1200)))
        self.check_remember_width = wx.CheckBox(self, label="Remember last width")
        self.check_remember_width.SetValue("window_start_width" not in settings)
        self.OnUpdateControls(None)

        width_sizer = wx.BoxSizer(wx.HORIZONTAL)
        width_sizer.Add(self.spin_width, 0, wx.ALIGN_CENTER_VERTICAL)
        width_sizer.AddSpacer(5)
        width_sizer.Add(self.check_remember_width, 1, wx.ALIGN_CENTER_VERTICAL)

        sb_font = wx.StaticBoxSizer(wx.StaticBox(self, label="Font"), wx.HORIZONTAL)
        sb_font.Add(self.label_font, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sb_font.Add(self.btn_font, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

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
        sizer.Add(sb_font, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(sb_window, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.OnSelectFont, self.btn_font)
        self.Bind(wx.EVT_CHOICE, self.OnUpdateControls, self.choice_start_mode)
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateControls, self.check_remember_width)

    def SetSelectedFont(self, font):
        self.label_font.SetFont(font)
        self.font = self.label_font.GetFont()
        self.label_font.SetLabel("%s %d" % (self.font.FaceName, self.font.PointSize))
        self.Fit()
        self.Centre()

    def OnSelectFont(self, evt):
        fontdata = wx.FontData()
        fontdata.SetInitialFont(self.font)
        fontdata.SetAllowSymbols(False)
        dlg = wx.FontDialog(self, fontdata)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                fontdata = dlg.GetFontData()
                self.SetSelectedFont(fontdata.GetChosenFont())
        finally:
            dlg.Destroy()

    def OnUpdateControls(self, evt):
        enable_width = self.choice_start_mode.Selection != 0
        self.spin_width.Enable(enable_width and not self.check_remember_width.Value)
        self.check_remember_width.Enable(enable_width)

    def UpdateSettings(self, settings):
        settings["font_face"] = self.font.FaceName
        settings["font_size"] = self.font.PointSize
        settings["font_style"] = font_style_string(self.font)

        settings["window_start_mode"] = view_modes[self.choice_start_mode.Selection][1]
        if self.choice_start_mode.Selection != 0 and not self.check_remember_width.Value:
            settings["window_start_width"] = self.spin_width.GetValue()
        elif "window_start_width" in settings:
            del settings["window_start_width"]

if __name__ == "__main__":
    app = wx.App()
    dlg = ViewSettingsDialog(None)
    if dlg.ShowModal() == wx.ID_OK:
        settings = {}
        dlg.UpdateSettings(settings)
        print settings
