import os, os.path
import sys
import time
import wx
from fsmonitor import FSMonitorThread, FSEvent

import fileutil
from async import async_call, coroutine, queued_coroutine, managed, Future, CoroutineQueue, CoroutineManager
from dialogs import dialogs
from dirtree_constants import *
from dirtree_filter import DirTreeFilter
from dirtree_node import SimpleNode, FSNode, DirNode, NODE_UNPOPULATED, NODE_POPULATING
from util import iter_tree_children, iter_tree_breadth_first, frozen_window
from resources import load_bitmap

def make_top_level():
    if sys.platform == "win32":
        import win32api
        from win32com.shell import shell, shellcon
        mycomputer = SimpleNode("My Computer",
                        [FSNode(drive, 'd') for drive in
                         win32api.GetLogicalDriveStrings().strip("\0").split("\0")])
        mydocs = shell.SHGetFolderPath(None, shellcon.CSIDL_PERSONAL, None, 0)
        desktop = shell.SHGetFolderPath(None, shellcon.CSIDL_DESKTOP, None, 0)
        return [mycomputer, FSNode(mydocs, 'd'), FSNode(desktop, 'd')]
    else:
        return [FSNode("/", 'd')]

class DirTreeCtrl(wx.TreeCtrl, wx.FileDropTarget):
    def __init__(self, parent, env, filter=None, show_root=False):
        style = wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.BORDER_NONE
        if not show_root:
            style |= wx.TR_HIDE_ROOT

        wx.TreeCtrl.__init__(self, parent, style=style)
        wx.FileDropTarget.__init__(self)

        self.SetDropTarget(self)
        self.SetDoubleBuffered(True)
        self.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        self.env = env
        self.filter = filter or DirTreeFilter()
        self.cq = CoroutineQueue()
        self.cm = CoroutineManager()
        self.select_later_parent = None
        self.select_later_name = None
        self.select_later_time = 0
        self.expanding_all = False
        self.drop_item = None

        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(load_bitmap("icons/folder.png"))
        self.imglist.Add(load_bitmap("icons/folder_denied.png"))
        self.imglist.Add(load_bitmap("icons/file.png"))
        self.SetImageList(self.imglist)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnItemRightClicked)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnItemBeginLabelEdit)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnItemEndLabelEdit)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.Bind(wx.EVT_MENU, self.OnItemEdit, id=ID_EDIT)
        self.Bind(wx.EVT_MENU, self.OnItemOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnItemOpenFolder, id=ID_OPEN_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnItemRename, id=ID_RENAME)
        self.Bind(wx.EVT_MENU, self.OnItemDelete, id=ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnNewFolder, id=ID_NEW_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnExpandAll, id=ID_EXPAND_ALL)
        self.Bind(wx.EVT_MENU, self.OnCollapseAll, id=ID_COLLAPSE_ALL)

        self.monitor = FSMonitorThread()
        self.monitor_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnMonitorTimer, self.monitor_timer)
        self.monitor_timer.Start(100)

    def Destroy(self):
        self.monitor_timer.Stop()
        self.monitor.remove_all_watches()
        self.monitor.read_events()
        self.cm.cancel()
        wx.TreeCtrl.Destroy(self)

    def OnMonitorTimer(self, evt):
        events = self.monitor.read_events()
        if events:
            self.OnFileSystemChanged(events)

    def SelectLater(self, parent, name, timeout=1):
        self.select_later_parent = parent
        self.select_later_name = name
        self.select_later_time = time.time() + timeout

    @managed("cm")
    @queued_coroutine("cq")
    def OnFileSystemChanged(self, events):
        for evt in events:
            if evt.action in (FSEvent.Create, FSEvent.MoveTo):
                item = (yield evt.user.add(evt.name, self, self.monitor, self.filter))
                if item:
                    if evt.name == self.select_later_name \
                    and self.GetItemParent(item) == self.select_later_parent:
                        if time.time() < self.select_later_time:
                            self.SelectItem(item)
                        self.select_later_name = None
                        self.select_later_parent = None
                        self.select_later_time = 0
            elif evt.action in (FSEvent.Delete, FSEvent.MoveFrom):
                evt.user.remove(evt.name, self, self.monitor)

    def OnItemActivated(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'f':
            self.env.open_file(node.path)
        elif node.type == 'd':
            self.Toggle(node.item)

    def OnItemExpanding(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd' and node.state == NODE_UNPOPULATED:
            self.ExpandNode(node)

    def OnItemCollapsed(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd':
            self.CollapseNode(node)

    def OnItemRightClicked(self, evt):
        self.SelectItem(evt.GetItem())
        node = self.GetEventNode(evt)
        menu = node.context_menu
        if menu:
            self.PopupMenu(menu.Create())

    def OnItemBeginLabelEdit(self, evt):
        node = self.GetEventNode(evt)
        if not (node and node.path):
            evt.Veto()

    def OnItemEndLabelEdit(self, evt):
        if not evt.IsEditCancelled():
            evt.Veto()
            node = self.GetEventNode(evt)
            self.RenameNode(node, evt.GetLabel())

    def OnBeginDrag(self, evt):
        node = self.GetEventNode(evt)
        if node:
            data = wx.FileDataObject()
            data.AddFile(node.path)
            dropsrc = wx.DropSource(self)
            dropsrc.SetData(data)
            dropsrc.DoDragDrop()

    def OnDragOver(self, x, y, default):
        self.OnLeave()
        item, flags = self.HitTest((x, y))
        if item and (flags & wx.TREE_HITTEST_ONITEMLABEL):
            self.drop_item = item
            self.SetItemDropHighlight(item, True)
            return wx.DragCopy
        return wx.DragNone

    def OnLeave(self):
        if self.drop_item:
            self.SetItemDropHighlight(self.drop_item, False)
            self.drop_item = None

    def OnDropFiles(self, x, y, filenames):
        self.OnLeave()
        item, flags = self.HitTest((x, y))
        if item and (flags & wx.TREE_HITTEST_ONITEMLABEL):            
            while item:
                node = self.GetPyData(item)
                if node.type == 'd':
                    for filename in filenames:
                        fileutil.shell_move_or_copy(filename, node.path)
                    break
                item = self.GetItemParent(item)

    def OnItemEdit(self, evt):
        node = self.GetSelectedNode()
        if node and node.type == 'f':
            self.env.open_file(node.path)

    def OnItemOpen(self, evt):
        path = self.GetSelectedPath()
        if path:
            self._shell_open(path)

    def OnItemOpenFolder(self, evt):
        path = self.GetSelectedPath()
        if path:
            self._shell_open(os.path.dirname(path))

    def OnItemRename(self, evt):
        node = self.GetSelectedNode()
        if node and node.path:
            self.EditLabel(node.item)

    def OnItemDelete(self, evt):
        node = self.GetSelectedNode()
        if node:
            next_item = self.GetNextSibling(node.item)
            fileutil.shell_remove(node.path)

    def OnNewFolder(self, evt):
        node = self.GetSelectedNode()
        if node:
            if node.type != 'd':
                node = self.GetPyData(self.GetItemParent(node.item))
            name = dialogs.get_text_input(self,
                "New Folder",
                "Please enter new folder name:")
            if name:
                self.NewFolder(node, name)

    @coroutine
    def OnExpandAll(self, evt):
        del evt
        if self.expanding_all:
            return
        self.expanding_all = True
        try:
            for item in iter_tree_breadth_first(self, self.GetRootItem()):
                if not self.expanding_all:
                    return
                node = self.GetPyData(item)
                if node.type == 'd':
                    if node.state == NODE_UNPOPULATED:
                        try:
                            yield self.ExpandNode(node)
                        except Exception:
                            pass
                    else:
                        self.Expand(item)
        finally:
            self.expanding_all = False

    def OnCollapseAll(self, evt):
        self.expanding_all = False
        self.CollapseAll()

    def SetItemNode(self, item, node):
        self.SetPyData(item, node)
        node.item = item
        return node

    def GetEventNode(self, evt):
        item = evt.GetItem()
        if item.IsOk():
            return self.GetPyData(item)

    def GetSelectedNode(self):
        item = self.GetSelection()
        if item.IsOk():
            return self.GetPyData(item)

    def GetSelectedPath(self):
        node = self.GetSelectedNode()
        return node.path if node else ""

    # Workaround for Windows sillyness
    if wx.Platform == "__WXMSW__":
        def IsExpanded(self, item):
            return self.GetRootItem() == item or wx.TreeCtrl.IsExpanded(self, item)
        def Expand(self, item):
            if self.GetRootItem() != item:
                wx.TreeCtrl.Expand(self, item)

    @managed("cm")
    @queued_coroutine("cq")
    def PopulateNode(self, node):
        if node.state == NODE_UNPOPULATED:
            f = node.expand(self, self.monitor, self.filter)
            if isinstance(f, Future):
                yield f

    @managed("cm")
    @coroutine
    def ExpandNode(self, node):
        if node.state == NODE_UNPOPULATED:
            yield self.PopulateNode(node)
        if node.state != NODE_POPULATING:
            self.Expand(node.item)

    def CollapseNode(self, node):
        node.collapse(self, self.monitor)

    @managed("cm")
    @coroutine
    def RenameNode(self, node, name):
        newpath = os.path.join(os.path.dirname(node.path), name)
        if newpath != node.path:
            try:
                if (yield async_call(os.path.exists, newpath)):
                    if not dialogs.ask_overwrite(self, newpath):
                        return
                yield async_call(fileutil.rename, node.path, newpath)
                self.SelectLater(self.GetItemParent(node.item), name)
            except OSError, e:
                dialogs.error(self, str(e))

    @managed("cm")
    @coroutine
    def NewFolder(self, node, name):
        path = os.path.join(node.path, name)
        try:
            yield async_call(os.mkdir, path)
            if self.IsExpanded(node.item):
                self.SelectLater(node.item, name)
        except OSError, e:
            dialogs.error(self, str(e))

    @managed("cm")
    def _shell_open(self, path):
        try:
            return async_call(fileutil.shell_open, path, workdir=os.path.dirname(path))
        except OSError, e:
            dialogs.error(self, str(e))

    @managed("cm")
    @coroutine
    def _InitialExpand(self, rootnode, toplevel):
        yield self.ExpandNode(rootnode)
        if isinstance(toplevel[0], SimpleNode):
            yield self.ExpandNode(toplevel[0])

    def SetTopLevel(self, toplevel=None):
        self.monitor.remove_all_watches()
        self.monitor.read_events()
        self.cm.cancel()
        self.cq.cancel()
        self.DeleteAllItems()
        toplevel = toplevel or make_top_level()
        if len(toplevel) == 1:
            rootitem = self.AddRoot(toplevel[0].label)
            rootnode = toplevel[0]
        else:
            rootitem = self.AddRoot("")
            rootnode = SimpleNode("", toplevel)
        self.SetItemNode(rootitem, rootnode)
        return self._InitialExpand(rootnode, toplevel)

    def _FindExpandedPaths(self, item, path, expanded):
        if self.IsExpanded(item):
            node = self.GetPyData(item)
            if node.type == 'd':
                subpath = (path and path + "/") + self.GetItemText(item)
                len_expanded = len(expanded)
                for child_item in iter_tree_children(self, item):
                    self._FindExpandedPaths(child_item, subpath, expanded)
                if len(expanded) == len_expanded:
                    expanded.append(subpath)
        return expanded

    def FindExpandedPaths(self):
        expanded = []
        for item in iter_tree_children(self, self.GetRootItem()):
            self._FindExpandedPaths(item, "", expanded)
        return expanded

    @managed("cm")
    @coroutine
    def _ExpandPaths(self, item, paths):
        expanded = [path[0] for path in paths if path]
        sub_paths = [path[1:] for path in paths if len(path) > 1]
        yield self.ExpandNode(self.GetPyData(item))
        for child_item in iter_tree_children(self, item):
            if self.GetItemText(child_item) in expanded:
                yield self._ExpandPaths(child_item, sub_paths)

    def ExpandPaths(self, paths):
        paths = [path.strip("/").split("/") for path in paths]
        return self._ExpandPaths(self.GetRootItem(), paths)

    def ExpandPath(self, path):
        return self._ExpandPaths(self.GetRootItem(), [path])

    def _SelectPath(self, item, path):
        node = self.GetPyData(item)
        if node.path == path:
            self.SelectItem(node.item)
        elif node.type == 'd':
            for child_item in iter_tree_children(self, item):
                self._SelectPath(child_item, path)

    @managed("cm")
    @coroutine
    def SelectPath(self, path):
        yield self.ExpandPath(path)
        self._SelectPath(self.GetRootItem(), path)

    def SavePerspective(self):
        p = {}
        expanded = self.FindExpandedPaths()
        if expanded:
            p["expanded"] = expanded
        selected = self.GetSelectedPath()
        if selected:
            p["selected"] = selected
        return p

    @managed("cm")
    @coroutine
    def LoadPerspective(self, p):
        expanded = p.get("expanded", ())
        if expanded:
            yield self.ExpandPaths(expanded)
        if "selected" in p:
            yield self.SelectPath(p["selected"])
