# coding=UTF8

import wx

programmer = "Programmed by Luke McCarthy <luke@iogopro.co.uk>"
url = "https://github.com/shaurz/devo"

license = u"""\
Copyright © 2010 Luke McCarthy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\
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
