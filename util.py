import wx

class frozen_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Thaw()

class hidden_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Hide()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Show()

if wx.Platform == "__WXMSW__":
    frozen_or_hidden_window = frozen_window
else:
    frozen_or_hidden_window = hidden_window

non_printable_chars = "\x00\x01\x02\x03\x04\x05\x06\x07\x0E\x0F" + \
    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F\x7F"

def count_non_printable(s):
    count = 0
    for c in s:
        if c in non_printable_chars:
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

def iter_tree_breadth_first(tree, item):
    for subitem in iter_tree_children(tree, item):
        yield subitem
    for subitem in iter_tree_children(tree, item):
        for subsubitem in iter_tree_breadth_first(tree, subitem):
            yield subsubitem

def get_combo_history(combo, size=10):
    value = combo.GetValue()
    history = combo.GetStrings()
    if value.strip():
        if value in history:
            history.remove(value)
        history.insert(0, value)
    return history[:size]

def get_text_extent(font, text):
    dc = wx.MemoryDC()
    dc.SetFont(font)
    return dc.GetTextExtent(text)

def is_focused(win):
    focus = wx.Window.FindFocus()
    while focus:
        if win is focus:
            return True
        focus = focus.Parent
    return False

def new_id_range(n):
    first = wx.NewId()
    last = first + n
    wx.RegisterId(last)
    return first, last

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
