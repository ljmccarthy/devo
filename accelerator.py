import string
import wx

key_codes = {
    "Backspace" : wx.WXK_BACK,
    "Del"       : wx.WXK_DELETE,
    "Delete"    : wx.WXK_DELETE,
    "Down"      : wx.WXK_DOWN,
    "End"       : wx.WXK_END,
    "Enter"     : wx.WXK_NUMPAD_ENTER,
    "F1"        : wx.WXK_F1,
    "F2"        : wx.WXK_F2,
    "F3"        : wx.WXK_F3,
    "F4"        : wx.WXK_F4,
    "F5"        : wx.WXK_F5,
    "F6"        : wx.WXK_F6,
    "F7"        : wx.WXK_F7,
    "F8"        : wx.WXK_F8,
    "F9"        : wx.WXK_F9,
    "F10"       : wx.WXK_F10,
    "F11"       : wx.WXK_F11,
    "F12"       : wx.WXK_F12,
    "Home"      : wx.WXK_HOME,
    "Insert"    : wx.WXK_INSERT,
    "Left"      : wx.WXK_LEFT,
    "Page Down" : wx.WXK_PAGEDOWN,
    "Page Up"   : wx.WXK_PAGEUP,
    "Pause"     : wx.WXK_PAUSE,
    "Return"    : wx.WXK_RETURN,
    "Right"     : wx.WXK_RIGHT,
    "Space"     : wx.WXK_SPACE,
    "Tab"       : wx.WXK_TAB,
    "Up"        : wx.WXK_UP,
}

modifier_bits = {
    "Alt"   : wx.MOD_ALT,
    "Ctrl"  : wx.MOD_CONTROL,
    "Shift" : wx.MOD_SHIFT,
}

key_names = dict((code, name) for (name, code) in key_codes.iteritems())
modifier_names = dict((bits, mod) for (mod, bits) in modifier_bits.iteritems())

def is_alpha(c):
    return (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z')

def is_digit(c):
    return c >= '0' and c <= '9'

def is_accelerator_key(c):
    return is_alpha(c) or is_digit(c)

def parse_accelerator(s):
    parts = [string.capwords(part.strip()) for part in s.split("+")]
    try:
        mod = 0
        for modname in parts[:-1]:
            mod |= modifier_bits[modname]
    except KeyError, e:
        raise ValueError("Invalid modifier name: %s" % e.args[0])
    keyname = parts[-1]
    key = None
    if len(keyname) == 1:
        if is_accelerator_key(keyname):
            key = ord(keyname)
    else:
        key = key_codes.get(keyname)
    if key is None:
        raise ValueError("Invalid key name: %s" % keyname)
    return key, mod

def unparse_accelerator(key, mod):
    keyname = key_names.get(key)
    if keyname is None:
        if is_accelerator_key(chr(key)):
            keyname = chr(key)
        else:
            raise ValueError("Invalid key code: %d" % key)
    parts = []
    for i in xrange(32):
        bit = 1 << i
        if mod & bit:
            modname = modifier_names.get(bit)
            if modname is None:
                raise ValueError("Invalid modifier: %x" % mod)
            parts.append(modname)
    parts.append(keyname)
    return "+".join(parts)

if __name__ == "__main__":
    print unparse_accelerator(*parse_accelerator("ctrl+alt+del"))
