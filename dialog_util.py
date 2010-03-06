import wx

def on_escape_key_down(self, evt):
    mod = evt.GetModifiers()
    key = evt.GetKeyCode()
    if mod == wx.MOD_NONE and key == wx.WXK_ESCAPE:
        self.EndModal(wx.ID_CANCEL)
    else:
        evt.Skip()

def bind_escape_key(dlg):
    handler = lambda evt: on_escape_key_down(dlg, evt)
    dlg.Bind(wx.EVT_KEY_DOWN, handler)
    for control in dlg.GetChildren():
        control.Bind(wx.EVT_KEY_DOWN, handler)

