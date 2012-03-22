import sys
import wx
import app_info

license = app_info.copyright + u"""

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

class AboutDialog(wx.Dialog):
    def __init__(self, parent, env):
        wx.Dialog.__init__(self, parent, title="About " + app_info.name)
        self.env = env

        logo_font_size = 25 if sys.platform == "__WXMAC__" else 20
        subtitle_font_size = 24 if sys.platform == "__WXMAC__" else 10

        fontsize = self.GetFont().PointSize
        label_devo = wx.StaticText(self, label=app_info.name)
        label_devo.SetForegroundColour(wx.RED)
        label_devo.SetFont(wx.Font(fontsize * 2, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        label_devolved = wx.StaticText(self, label="      Text Editing Devolved")
        label_devolved.SetFont(wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD))
        label_version = wx.StaticText(self, label="Version " + app_info.version_string)

        label_developer = wx.StaticText(self, label=app_info.developer)
        link_website = wx.HyperlinkCtrl(self, wx.ID_ANY, label=app_info.url, url=app_info.url)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_license = wx.Button(self, label="License")
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.Add(btn_license)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(btn_ok)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_devo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.Add(label_devolved, 0, wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer(15)
        sizer.Add(label_version, 0, wx.LEFT | wx.RIGHT, 20)
        sizer.AddSpacer(5)
        sizer.Add(label_developer, 0, wx.LEFT | wx.RIGHT, 20)
        sizer.AddSpacer(5)
        sizer.Add(link_website, 0, wx.LEFT | wx.RIGHT, 20)
        sizer.AddSpacer(5)
        sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(sizer)
        self.Fit()
        self.CentreOnScreen()

        self.Bind(wx.EVT_BUTTON, self.OnLicense, btn_license)

    def OnLicense(self, evt):
        self.EndModal(wx.ID_OK)
        self.env.open_static_text("Devo License", license)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = AboutDialog(None)
    dlg.ShowModal()
