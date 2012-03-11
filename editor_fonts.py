import wx, wx.stc

if wx.Platform == "__WXMSW__":
    font_face = "Consolas"
    font_size = 10
elif wx.Platform == "__WXMAC__":
    font_face = "Menlo Regular"
    font_size = 12
else:
    font_face = "Monospace"
    font_size = 10

def init_stc_style(ctrl, lexer=wx.stc.STC_LEX_NULL, keywords=""):
    ctrl.ClearDocumentStyle()
    ctrl.SetLexer(lexer)
    ctrl.SetKeyWords(0, keywords)
    ctrl.StyleResetDefault()
    ctrl.StyleSetFontAttr(wx.stc.STC_STYLE_DEFAULT, font_size, font_face, False, False, False)
    ctrl.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "")
    ctrl.StyleClearAll()
