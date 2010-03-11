import wx
import os

def message_dialog(parent, message, caption, style):
    if not caption:
        caption = wx.GetApp().GetAppName()
    dlg = wx.MessageDialog(parent, message, caption, style)
    rc = dlg.ShowModal()
    dlg.Destroy()
    return rc

def error(parent, message, caption="Error"):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_ERROR)

def info(parent, message, caption=""):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)

def get_file_to_open(parent, wildcard="All Files|*.*", message="Open File", dirname=""):
    dlg = wx.FileDialog(parent, wildcard=wildcard, message=message, defaultDir=dirname)
    path = ""
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path

def get_file_to_save(parent, wildcard="All Files|*.*", message="Save File", dirname=""):
    dlg = wx.FileDialog(parent,
        wildcard=wildcard, message=message, defaultDir=dirname,
        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    path = ""
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    dlg.Destroy()
    return path

class SaveChangesDialog(wx.Dialog):
    def __init__(self, parent, message, title="Unsaved Changes"):
        wx.Dialog.__init__(self, parent, title=title)
        btnsizer = wx.StdDialogButtonSizer()
        btn_save = wx.Button(self, wx.ID_YES, "&Save")
        btn_save.SetDefault()
        btnsizer.AddButton(btn_save)
        btnsizer.AddButton(wx.Button(self, wx.ID_NO, "&Don't Save"))
        btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL, "&Cancel"))
        btnsizer.Realize()
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.StaticBitmap(self, wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_WARNING))
        hsizer.Add(bmp, 0, wx.ALIGN_CENTRE | wx.RIGHT, 15)
        hsizer.Add(wx.StaticText(self, label=message), 1, wx.ALIGN_CENTRE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL, 15)
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        self.Fit()
        size = self.GetSize()
        self.SetMinSize(size)
        self.SetMaxSize(size)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(evt.GetId()))

def ask_save_changes(parent, path=""):
    path = os.path.basename(path)
    if path:
        message = "File '%s' has been modified. Save changes?" % path
    else:
        message = "Save unsaved changes?"
    dlg = SaveChangesDialog(parent, message)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result

def ask_overwrite(parent, path):
    return message_dialog(parent, 
        "A file named '%s' already exists. Overwrite?" % path,
        "Confirm Overwrite",
        wx.YES_NO | wx.ICON_QUESTION) == wx.ID_YES

def ask_delete(parent, path):
    return message_dialog(parent,
        "Are you sure you want to delete '%s'?" % path,
        "Confirm Delete",
        wx.YES_NO | wx.ICON_QUESTION) == wx.ID_YES
