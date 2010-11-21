import wx

programmer = "Programmed by Luke McCarthy <luke@iogopro.co.uk>"
url = "https://github.com/shaurz/devo"

license = """\
Copyright (c) 2010 Luke McCarthy
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\
"""

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="About Devo")

        label_devo = wx.StaticText(self, label="Devo")
        label_devo.SetForegroundColour(wx.RED)
        label_devo.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        label_devolved = wx.StaticText(self, label="      Text Editing Devolved")
        label_devolved.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))

        label_programmer = wx.StaticText(self, label=programmer)
        link_website = wx.HyperlinkCtrl(self, wx.ID_ANY, label=url, url=url)
        text_license = wx.TextCtrl(self, value=license, size=(600, 200), style=wx.TE_READONLY | wx.TE_MULTILINE)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_devo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        sizer.Add(label_devolved, 0, wx.LEFT | wx.RIGHT, 5)
        sizer.AddSpacer(15)
        sizer.Add(label_programmer, 0, wx.LEFT | wx.RIGHT, 5)
        sizer.Add(link_website, 0, wx.LEFT | wx.RIGHT, 5)
        sizer.AddSpacer(5)
        sizer.Add(text_license, 0, wx.ALL | wx.FIXED_MINSIZE, 5)
        sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Fit()

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = AboutDialog(None)
    dlg.ShowModal()
