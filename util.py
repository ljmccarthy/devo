import mimetypes
import wx

class frozen_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Thaw()

def is_text_file(path):
    filetype, encoding = mimetypes.guess_type(path)
    return filetype is None or filetype.startswith("text/")

def iter_tree_children(tree, item):
    item = tree.GetFirstChild(item)[0]
    while item.IsOk():
        yield item
        item = tree.GetNextSibling(item)

def _TryCallLater(timer, func, args, kwargs):
    print "_TryCallLater", timer, func, args, kwargs
    try:
        wx.CallLater(timer, func, *args, **kwargs)
    except wx._core.PyDeadObjectError, e:
        pass

def CallLater(timer, func, *args, **kwargs):
    """Thread-safe CallLater with PyDeadObjectError handling."""
    if wx.Thread_IsMain():
        _TryCallLater(timer, func, args, kwargs)
    else:
        wx.CallAfter(_TryCallLater, timer, func, args, kwargs)
        
