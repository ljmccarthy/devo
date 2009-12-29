import os
import mimetypes
import wx
from async_wx import async_call, coroutine
from project_tree import ProjectTree
from editor import Editor
import dialogs

class frozen_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Thaw()

def is_text(path):
    filetype, encoding = mimetypes.guess_type(path)
    return filetype is None or filetype.startswith("text/")

class AppEnv(object):
    def __init__(self, mainframe):
        self.mainframe = mainframe

    @coroutine
    def OpenFile(self, path):
        if not (yield async_call(is_text, path)):
            dialogs.error(self.mainframe, "Selected file is not a text file:\n\n%s" % path)
        else:
            yield self.mainframe.OpenEditor(path)

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Editor", size=(1000, 1200))
        self.editors = {}
        self.env = AppEnv(self)

        self.manager = wx.aui.AuiManager(self)
        self.notebook = wx.aui.AuiNotebook(self)
        self.tree = ProjectTree(self, self.env, "/devel")

        self.manager.AddPane(self.tree,
            wx.aui.AuiPaneInfo().Left().BestSize(wx.Size(200, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook,
            wx.aui.AuiPaneInfo().CentrePane())
        self.manager.Update()

        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)

    def OnPageClose(self, evt):
        editor = self.notebook.GetPage(evt.GetSelection())
        del self.editors[editor.path]

    def AddPage(self, win, text):
        i = self.notebook.GetSelection() + 1
        self.notebook.InsertPage(i, win, text)
        self.notebook.SetSelection(i)

    def NewEditor(self, path):
        editor = Editor(self.notebook, self)
        self.AddPage(editor, "Untitled")

    @coroutine
    def OpenEditor(self, path):
        realpath = os.path.realpath(path)
        editor = self.editors.get(realpath)
        if editor is not None:
            i = self.notebook.GetPageIndex(editor)
            if i >= 0:
                self.notebook.SetSelection(i)
        else:
            with frozen_window(self.notebook):
                editor = Editor(self.notebook, self)
                editor.Show(False)
                self.editors[realpath] = editor
                try:
                    yield editor.LoadFile(realpath)
                except Exception, exn:
                    dialogs.error(self, "Error opening file:\n\n%s" % exn)
                    editor.Destroy()
                    del self.editors[realpath]
                else:
                    self.AddPage(editor, os.path.basename(path))
                    self.editors[realpath] = editor
