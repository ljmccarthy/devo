import os.path

import fileutil
from async import async_call
from dirtree import DirTreeCtrl
from dirtree_constants import *
from menu import Menu, MenuItem, MenuSeparator

ID_DIRTREE_EDIT = wx.NewId()
ID_DIRTREE_OPEN_FOLDER = wx.NewId()
ID_DIRTREE_SEARCH = wx.NewId()
ID_DIRTREE_SEARCH_FOLDER = wx.NewId()

context_menu_file = Menu("", [
    MenuItem(ID_DIRTREE_OPEN, "&Open"),
    MenuItem(ID_DIRTREE_EDIT, "&Edit with Devo"),
    MenuItem(ID_DIRTREE_PREVIEW, "&Preview"),
    MenuItem(ID_DIRTREE_RENAME, "&Rename"),
    MenuItem(ID_DIRTREE_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_DIRTREE_NEW_FOLDER, "&New Folder..."),
    MenuItem(ID_DIRTREE_OPEN_FOLDER, "Open Containing &Folder"),
    MenuSeparator,
    MenuItem(ID_DIRTREE_SEARCH, "Searc&h..."),
    MenuItem(ID_DIRTREE_SEARCH_FOLDER, "Search Containing Folder..."),
    MenuSeparator,
    MenuItem(ID_DIRTREE_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID_DIRTREE_COLLAPSE_ALL, "&Collapse All"),
])

context_menu_dir = Menu("", [
    MenuItem(ID_DIRTREE_OPEN, "&Open"),
    MenuItem(ID_DIRTREE_RENAME, "&Rename"),
    MenuItem(ID_DIRTREE_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_DIRTREE_NEW_FOLDER, "&New Folder..."),
    MenuItem(ID_DIRTREE_OPEN_FOLDER, "Open Containing &Folder"),
    MenuSeparator,
    MenuItem(ID_DIRTREE_SEARCH, "Searc&h..."),
    MenuSeparator,
    MenuItem(ID_DIRTREE_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID_DIRTREE_COLLAPSE_ALL, "&Collapse All"),
])

class EditorDirTreeCtrl(DirTreeCtrl):
    def __init__(self, parent, env, filter=None, show_root=False):
        DirTreeCtrl.__init__(self, parent, filter=filter, show_root=show_root)
        self.env = env

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_MENU, self.OnItemOpen, id=ID_DIRTREE_OPEN)
        self.Bind(wx.EVT_MENU, self.OnItemPreview, id=ID_DIRTREE_PREVIEW)
        self.Bind(wx.EVT_MENU, self.OnItemEdit, id=ID_DIRTREE_EDIT)
        self.Bind(wx.EVT_MENU, self.OnItemOpenFolder, id=ID_DIRTREE_OPEN_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnSearch, id=ID_DIRTREE_SEARCH)
        self.Bind(wx.EVT_MENU, self.OnSearchFolder, id=ID_DIRTREE_SEARCH_FOLDER)

    def GetNodeMenu(self, node):
        if node.type == 'd':
            return context_menu_dir
        if node.type == 'f':
            return context_menu_file

    def OnItemActivated(self, evt):
        node = self.GetEventNode(evt)
        if node:
            if node.type == 'f':
                self.env.open_file(node.path)
            elif node.type == 'd':
                self.Toggle(node.item)

    def OnItemOpen(self, evt):
        path = self.GetSelectedPath()
        if path:
            self._shell_open(path)

    def OnItemEdit(self, evt):
        node = self.GetSelectedNode()
        if node and node.type == 'f':
            self.env.open_file(node.path)
            
    def OnItemPreview(self, evt):
        node = self.GetSelectedNode()
        if node and node.type == 'f':
            self.env.open_preview(node.path)

    def _shell_open(self, path):
        try:
            self.cm.add(async_call(fileutil.shell_open, path, workdir=os.path.dirname(path)))
        except OSError, e:
            dialogs.error(self, str(e))

    def OnItemOpenFolder(self, evt):
        path = self.GetSelectedPath()
        if path:
            self._shell_open(os.path.dirname(path))

    def OnSearch(self, evt):
        path = self.GetSelectedPath()
        if path:
            self.env.search(path=path)

    def OnSearchFolder(self, evt):
        path = self.GetSelectedPath()
        if path:
            self.env.search(path=os.path.dirname(path))
