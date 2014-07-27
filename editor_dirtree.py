import wx
import os.path

import fileutil
import ID
from async import async_call
from dialogs import dialogs
from dirtree import DirTreeCtrl
from menu_defs import file_context_menu, dir_context_menu

class EditorDirTreeCtrl(DirTreeCtrl):
    def __init__(self, parent, env, filter=None, show_root=False):
        DirTreeCtrl.__init__(self, parent, filter=filter, show_root=show_root)
        self.env = env

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_MENU, self.OnItemOpen, id=ID.DIRTREE_OPEN)
        self.Bind(wx.EVT_MENU, self.OnItemEdit, id=ID.DIRTREE_EDIT)
        self.Bind(wx.EVT_MENU, self.OnItemPreview, id=ID.DIRTREE_PREVIEW)
        self.Bind(wx.EVT_MENU, self.OnItemOpenFolder, id=ID.DIRTREE_OPEN_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnSearch, id=ID.DIRTREE_SEARCH)
        self.Bind(wx.EVT_MENU, self.OnSearchFolder, id=ID.DIRTREE_SEARCH_FOLDER)

    def GetNodeMenu(self, node):
        if node.type == 'd':
            return dir_context_menu
        if node.type == 'f':
            return file_context_menu

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
        except OSError as e:
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
