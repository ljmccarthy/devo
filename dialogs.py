import os
import wx

from dirdialog import DirDialog

def message_dialog(parent, message, caption, style):
    if not caption:
        caption = wx.GetApp().GetAppName()
    dlg = wx.MessageDialog(parent, message, caption, style)
    try:
        return dlg.ShowModal()
    finally:
        dlg.Destroy()

def error(parent, message, caption="Error"):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_ERROR)

def info(parent, message, caption=""):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)

def get_file_to_open(parent, wildcard="All Files|*.*", message="Open File", path=""):
    dlg = wx.FileDialog(parent, wildcard=wildcard, message=message, defaultDir=path)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetPath()
    finally:
        dlg.Destroy()

def get_file_to_save(parent, wildcard="All Files|*.*", message="Save File", path=""):
    dlg = wx.FileDialog(parent,
        wildcard=wildcard, message=message, defaultDir=path,
        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetPath()
    finally:
        dlg.Destroy()

def get_directory(parent, message="Select Folder", path=""):
    dlg = DirDialog(parent, message=message, select_path=path)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetPath()
    finally:
        dlg.Destroy()

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
        warning_bitmap = wx.ArtProvider.GetBitmap(wx.ART_WARNING, wx.ART_MESSAGE_BOX)
        bmp = wx.StaticBitmap(self, wx.ID_ANY, warning_bitmap)
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
    try:
        return dlg.ShowModal()
    finally:
        dlg.Destroy()

def ask_overwrite(parent, path):
    return message_dialog(parent, 
        "A file named '%s' already exists. Overwrite?" % path,
        "Confirm Overwrite",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

def ask_delete(parent, path):
    return message_dialog(parent,
        "Are you sure you want to delete '%s'?" % path,
        "Confirm Delete",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

class TextInputDialog(wx.Dialog):
    def __init__(self, parent, title="", message="", value="", width=300):
        wx.Dialog.__init__(self, parent, title=title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        if message:
            label = wx.StaticText(self, label=message)
            sizer.Add(label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        self.textctrl = wx.TextCtrl(self, size=(width, -1), value=value)
        sizer.Add(self.textctrl, 0, wx.ALL | wx.EXPAND, 5)
        btnsizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.GetSize())
        self.textctrl.SetFocus()

def get_text_input(*args, **kwargs):
    dlg = TextInputDialog(*args, **kwargs)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.textctrl.GetValue()
    finally:
        dlg.Destroy()
