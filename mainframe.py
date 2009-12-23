import wx
from project_tree import ProjectTree
from editor import Editor

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Editor", size=(1000, 1200))
        self.manager = wx.aui.AuiManager(self)
        self.notebook = wx.aui.AuiNotebook(self)
        self.tree = ProjectTree(self)
        self.notebook.AddPage(Editor(self.notebook), "Untitled")
        self.manager.AddPane(self.tree,
            wx.aui.AuiPaneInfo().Left().BestSize(wx.Size(200, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook, wx.aui.AuiPaneInfo().CentrePane())
        self.manager.Update()
