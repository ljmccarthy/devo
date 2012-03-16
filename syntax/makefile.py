import wx.stc

ident = "makefile"
name = "Makefile"
extensions = ["*Makefile", "*makefile", "*.mk"]
lexer = wx.stc.STC_LEX_MAKEFILE
indent = 8
use_tabs = True
comment_token = "#"

stylespecs = (
    (wx.stc.STC_STYLE_DEFAULT, ""),
)

keywords = ""
