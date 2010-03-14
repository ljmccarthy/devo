import wx
import os
import dialogs

ID_BROWSE = wx.NewId()

class FilePicker(wx.Panel):
    def __init__(self, parent, browse_func, size=(100, -1), value=""):
        wx.Panel.__init__(self, parent)
        self.browse_func = browse_func
        self.text = wx.TextCtrl(self, ID_BROWSE, size=size, value=value)
        btn_browse = wx.Button(self, ID_BROWSE, size=(25, self.text.Size.height), label="...")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.text, 1, wx.FIXED_MINSIZE)
        sizer.AddSpacer(2)
        sizer.Add(btn_browse, 0, wx.FIXED_MINSIZE)
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
