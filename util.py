import os.path, re
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

def get_top_level_focus():
    focus = wx.Window.FindFocus()
    while focus:
        if isinstance(focus, wx.TopLevelWindow):
            return focus
        focus = wx.GetTopLevelParent(focus)

def new_id_range(n):
    first = wx.NewId()
    last = first + n
    wx.RegisterId(last)
    return first, last

def _TryCallLater(timer, func, args, kwargs):
    try:
        wx.CallLater(timer, func, *args, **kwargs)
    except wx._core.PyDeadObjectError as e:
        pass

def CallLater(timer, func, *args, **kwargs):
    """Thread-safe CallLater with PyDeadObjectError handling."""
    if wx.Thread_IsMain():
        _TryCallLater(timer, func, args, kwargs)
    else:
        wx.CallAfter(_TryCallLater, timer, func, args, kwargs)

non_printable_re = re.compile(r"[\0-\x07\x0E-\x1F\x7F]")
line_end_re = re.compile(r"\r\n|\r|\n")

def count_non_printable(s):
    count = 0
    for c in s:
        if non_printable_re.match(c):
            count += 1
    return count

# Heuristic idea from Subversion:
# http://subversion.apache.org/faq.html#binary-files
def is_text_file(path):
    with open(path, "rb") as f:
        data = f.read(1024)
    return not ("\0" in data or count_non_printable(data) > len(data) // 6)

def clear_text_lines(text):
    text = non_printable_re.sub("", text)
    return line_end_re.split(text)

def clean_text(text):
    return "\n".join(clear_text_lines(text))

def clean_strip_text(text):
    lines = clear_text_lines(text)
    if lines:
        lines = [line.rstrip() for line in lines[:-1]] + [lines[-1]]
    return "\n".join(lines)

def shorten_text(text, max_length):
    return text[:max_length - 2] + "..." if len(text) > max_length else text

def shorten_path(path):
    parts = path.split(os.path.sep)
    if len(parts) > 6:
        return os.path.sep.join(parts[:3] + ["..."] + parts[-2:])
    else:
        return path
