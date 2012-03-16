import wx

if wx.Platform == "__WXMSW__":
    font_face = "Consolas"
    font_size = 10
elif wx.Platform == "__WXMAC__":
    font_face = "Menlo Regular"
    font_size = 12
else:
    font_face = "Monospace"
    font_size = 10
