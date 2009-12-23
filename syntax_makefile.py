import wx.stc

ident = "makefile"
name = "Makefile"
extensions = ["Makefile", "*.mk"]
lexer = wx.stc.STC_LEX_MAKEFILE
indent = 8
use_tabs = True

stylespecs = (
    (wx.stc.STC_STYLE_DEFAULT,    ""),
)

keywords = ""
