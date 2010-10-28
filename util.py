import wx

class frozen_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Thaw()

def count_non_printable(s):
    count = 0
    for c in s:
        if ord(c) < 0x20:
            count += 1
    return count

# Heuristic idea from Subversion:
# http://subversion.apache.org/faq.html#binary-files
def is_text_file(path):
    with open(path, "rb") as f:
        data = f.read(1024)
    return not ("\0" in data or count_non_printable(data) > len(data) // 6)

def iter_tree_children(tree, item):
    item = tree.GetFirstChild(item)[0]
    while item.IsOk():
        yield item
        item = tree.GetNextSibling(item)

def is_focused(win):
    focus = wx.Window.FindFocus()
    while focus:
        if win is focus:
            return True
        focus = focus.Parent
    return False

def _TryCallLater(timer, func, args, kwargs):
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
