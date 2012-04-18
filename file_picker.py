import wx
import os
from dialogs import dialogs
from util import get_combo_history

ID_BROWSE = wx.NewId()

class FilePicker(wx.Panel):
    def __init__(self, parent, browse_func, size=wx.Size(100, -1), value="", combo=False):
        wx.Panel.__init__(self, parent)
        size = wx.Size(*size)
        self.browse_func = browse_func

        if combo:
            self.path_ctrl = wx.ComboBox(self, ID_BROWSE,
                size=(size.width - 30, size.height), value=value)
        else:
            self.path_ctrl = wx.TextCtrl(self, ID_BROWSE,
                size=(size.width - 30, size.height), value=value)

        btn_browse = wx.Button(self, ID_BROWSE,
            size=(30, -1 if wx.Platform == "__WXMAC__" else self.path_ctrl.Size.height),
            label="...")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.path_ctrl, 1, wx.ALIGN_CENTRE_VERTICAL|wx.FIXED_MINSIZE|wx.ALL)
        sizer.AddSpacer(5)
        sizer.Add(btn_browse, 0, wx.ALIGN_CENTRE_VERTICAL|wx.ALL)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.__OnBrowse, id=ID_BROWSE)

    def __OnBrowse(self, evt):
        path = os.path.expanduser(self.path_ctrl.GetValue())
        while path and not os.path.isdir(path):
            path = os.path.dirname(path)
        path = self.browse_func(self, path=path)
        if path:
            self.path_ctrl.SetValue(path)

    def GetValue(self):
        return self.path_ctrl.GetValue()

    def SetValue(self, value):
        self.path_ctrl.SetValue(value)

    def GetHistory(self):
        return get_combo_history(self.path_ctrl)

    def SetHistory(self, history):
        self.path_ctrl.SetItems(history)

def FileOpenPicker(parent, size=(100, -1), value="", combo=False):
    return FilePicker(parent, dialogs.get_file_to_open, size, value, combo)

def FileSavePicker(parent, size=(100, -1), value="", combo=False):
    return FilePicker(parent, dialogs.get_file_to_save, size, value, combo)

def DirPicker(parent, size=(100, -1), value="", combo=False):
    return FilePicker(parent, dialogs.get_directory, size, value, combo)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(None)
    FileOpenPicker(frame)
    frame.Show()
    app.MainLoop()
