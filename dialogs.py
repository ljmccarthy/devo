import wx

def error(parent, message, caption="Error"):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def get_file_to_open(parent, wildcard="All Files|*.*", message="Open File", dirname=""):
    dlg = wx.FileDialog(parent, wildcard=wildcard, message=message, defaultDir=dirname)
    path = ""
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path
