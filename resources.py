import sys, os.path
import wx

class ResourceError(Exception):
    pass

if hasattr(sys, "frozen"):
    from res_compiled import resources
    from cStringIO import StringIO

    def load_bitmap(name):
        name = os.path.normpath(name)
        data = resources.get(name)
        if data is None:
            raise ResourceError("Resource not found: %r" % name)
        image = wx.ImageFromStream(StringIO(data))
        if image.Ok():
            bitmap = wx.BitmapFromImage(image)
            if bitmap.Ok():
                return bitmap
        raise ResourceError("Failed to load bitmap: %r" % name)

else:
    respath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")

    def load_bitmap(name):
        bitmap = wx.Bitmap(os.path.join(respath, name))
        if not bitmap.Ok():
            raise ResourceError("Failed to load bitmap: %r" % name)
        return bitmap
