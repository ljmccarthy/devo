import wx

def load_bitmap(filename):
    bmp = wx.Bitmap(filename)
    if not bmp.Ok():
        raise IOError("Failed to load bitmap: %r" % filename)
    return bmp
