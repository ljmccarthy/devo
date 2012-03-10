import wx
import os
from dialogs import dialogs

ID_BROWSE = wx.NewId()

class FilePicker(wx.Panel):
    def __init__(self, parent, browse_func, size=wx.Size(100, -1), value=""):
        wx.Panel.__init__(self, parent)
        size = wx.Size(*size)
        self.browse_func = browse_func
        self.text = wx.TextCtrl(self, ID_BROWSE,
            size=(size.width - 30, size.height), value=value)
        btn_browse = wx.Button(self, ID_BROWSE,
            size=(30, -1 if wx.Platform == "__WXMAC__" else self.text.Size.height),
            label="...")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.text, 1, wx.ALIGN_CENTRE_VERTICAL|wx.FIXED_MINSIZE|wx.ALL, 2)
        sizer.Add(btn_browse, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL, 2)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.__OnBrowse, id=ID_BROWSE)

    def __OnBrowse(self, evt):
        path = self.text.GetValue()
        while path and not os.path.isdir(path):
            path = os.path.dirname(path)
        path = self.browse_func(self, path=path)
        if path:
            self.text.SetValue(path)

    def GetValue(self):
        return self.text.GetValue()

def FileOpenPicker(parent, size=(100, -1), value=""):
    return FilePicker(parent, dialogs.get_file_to_open, size, value)

def FileSavePicker(parent, size=(100, -1), value=""):
    return FilePicker(parent, dialogs.get_file_to_save, size, value)

def DirPicker(parent, size=(100, -1), value=""):
    return FilePicker(parent, dialogs.get_directory, size, value)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    FileOpenPicker(frame)
    frame.Show()
    app.MainLoop()
