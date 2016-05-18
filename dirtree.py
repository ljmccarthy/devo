import os, os.path
import sys
import time
import threading
import wx
from fsmonitor import FSMonitor, FSEvent

import fileutil
from async import async_call, coroutine, queued_coroutine, managed, Future, CoroutineQueue, CoroutineManager
from dialogs import dialogs
from dirtree_constants import *
from dirtree_filter import DirTreeFilter
from dirtree_node import SimpleNode, FSNode, DirNode
from menu import Menu, MenuItem, MenuSeparator
from signal_wx import Signal
from util import iter_tree_children, iter_tree_breadth_first, frozen_window, is_dead_object
from resources import load_bitmap

context_menu = Menu("", [
    MenuItem(ID_DIRTREE_OPEN, "&Open"),
    MenuItem(ID_DIRTREE_RENAME, "&Rename"),
    MenuItem(ID_DIRTREE_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_DIRTREE_NEW_FOLDER, "&New Folder..."),
    MenuSeparator,
    MenuItem(ID_DIRTREE_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID_DIRTREE_COLLAPSE_ALL, "&Collapse All"),
])

def split_path(path, relative_to=""):
    path = os.path.normpath(path)
    if relative_to:
        try:
            path = os.path.relpath(path, relative_to)
        except ValueError:
            pass
    return path.strip(os.path.sep).split(os.path.sep)

def make_top_level():
    if sys.platform == "win32":
        import win32api, pywintypes
        from win32com.shell import shell, shellcon

        def get_volume_label(drive):
            try:
                label = win32api.GetVolumeInformation(drive)[0]
            except pywintypes.error:
                label = ""
            return "%s (%s)" % (label, drive[:2]) if label else drive

        drives = [FSNode(drive, 'd', get_volume_label(drive))
                  for drive in win32api.GetLogicalDriveStrings().strip("\0").split("\0")]

        mydocs = shell.SHGetFolderPath(None, shellcon.CSIDL_PERSONAL, None, 0)
        desktop = shell.SHGetFolderPath(None, shellcon.CSIDL_DESKTOP, None, 0)

        return drives + [FSNode(mydocs, 'd'), FSNode(desktop, 'd')]
    else:
        return [FSNode("/", 'd')]

class DirTreeMonitor(object):
    def __init__(self, tree, monitor):
        self.tree = tree
        self.monitor = monitor
        self.__lock = threading.Lock()
        self.__events = []
        self.__thread = threading.Thread(target=self.__monitor_update_thread)
        self.__thread.daemon = True
        self.__thread.start()

    def __monitor_update_thread(self):
        while not is_dead_object(self.tree):
            events = self.monitor.read_events(timeout=1)
            if events:
                with self.__lock:
                    self.__events.extend(events)
                if not is_dead_object(self.tree):
                    self.tree.sig_update_tree.signal()
        self.monitor.close()
        with self.__lock:
            self.__events = []

    def get_events(self):
        with self.__lock:
            events, self.__events = self.__events, []
            return events

    def clear(self):
        self.monitor.remove_all_watches()
        with self.__lock:
            self.__events = []

add_events = (FSEvent.Attrib, FSEvent.Modify, FSEvent.Create, FSEvent.MoveTo)
remove_events = (FSEvent.Delete, FSEvent.MoveFrom)

class DirTreeCtrl(wx.TreeCtrl, wx.FileDropTarget):
    def __init__(self, parent, filter=None, show_root=False):
        style = wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.BORDER_NONE
        if not show_root:
            style |= wx.TR_HIDE_ROOT

        wx.TreeCtrl.__init__(self, parent, style=style)
        wx.FileDropTarget.__init__(self)

        self.SetDropTarget(self)
        self.SetDoubleBuffered(True)

        old_font = self.GetFont()
        self.font = wx.Font(old_font.PointSize, old_font.Family, old_font.Style, old_font.Weight, faceName=old_font.FaceName)
        self.SetFont(self.font)

        self.filter = filter or DirTreeFilter()
        self.cq = CoroutineQueue()
        self.cm = CoroutineManager()
        self.select_later_parent = None
        self.select_later_name = None
        self.select_later_time = 0
        self.expanding_all = False
        self.drop_item = None
        self.sig_update_tree = Signal(self)
        self.sig_update_tree.bind(self.UpdateFromFSMonitor)
        self.monitor = FSMonitor()
        self.monitor_thread = DirTreeMonitor(self, self.monitor)

        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(load_bitmap("icons/folder.png"))
        self.imglist.Add(load_bitmap("icons/folder_denied.png"))
        self.imglist.Add(load_bitmap("icons/file.png"))
        self.SetImageList(self.imglist)

        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnItemRightClicked)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnItemBeginLabelEdit)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnItemEndLabelEdit)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnBeginDrag)
        self.Bind(wx.EVT_MENU, self.OnItemRename, id=ID_DIRTREE_RENAME)
        self.Bind(wx.EVT_MENU, self.OnItemDelete, id=ID_DIRTREE_DELETE)
        self.Bind(wx.EVT_MENU, self.OnNewFolder, id=ID_DIRTREE_NEW_FOLDER)
        self.Bind(wx.EVT_MENU, self.OnExpandAll, id=ID_DIRTREE_EXPAND_ALL)
        self.Bind(wx.EVT_MENU, self.OnCollapseAll, id=ID_DIRTREE_COLLAPSE_ALL)

    def Destroy(self):
        self.cm.cancel()
        self.monitor.close()
        wx.TreeCtrl.Destroy(self)

    def SelectLater(self, parent, name, timeout=1):
        self.select_later_parent = parent
        self.select_later_name = name
        self.select_later_time = time.time() + timeout

    def TrySelectLater(self, item, name):
        if name == self.select_later_name \
        and self.GetItemParent(item) == self.select_later_parent:
            if time.time() < self.select_later_time:
                self.SelectItem(item)
            self.select_later_name = None
            self.select_later_parent = None
            self.select_later_time = 0

    @managed("cm")
    @coroutine
    def UpdateFromFSMonitor(self):
        for evt in self.monitor_thread.get_events():
            if evt.action in add_events:
                item = (yield evt.user.add(evt.name, self, self.monitor, self.filter))
                if item:
                    self.TrySelectLater(item, evt.name)
            elif evt.action in remove_events:
                evt.user.remove(evt.name, self, self.monitor)

    def OnItemExpanding(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd' and not node.populated:
            self.ExpandNode(node)

    def OnItemCollapsed(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd':
            self.CollapseNode(node)

    def GetNodeMenu(self, node):
        return context_menu

    def OnItemRightClicked(self, evt):
        self.SelectItem(evt.GetItem())
        node = self.GetEventNode(evt)
        menu = self.GetNodeMenu(node)
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
                        filename = os.path.realpath(filename)
                        if filename != node.path:
                            fileutil.shell_move_or_copy(filename, node.path, parent=self)
                    break
                item = self.GetItemParent(item)

    def OnItemRename(self, evt):
        node = self.GetSelectedNode()
        if node and node.path:
            self.EditLabel(node.item)

    def OnItemDelete(self, evt):
        node = self.GetSelectedNode()
        if node:
            next_item = self.GetNextSibling(node.item)
            fileutil.shell_remove(node.path, parent=self)

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

    @managed("cm")
    @coroutine
    def OnExpandAll(self, evt):
        del evt
        if self.expanding_all:
            return
        if not dialogs.yes_no(self,
                "Expanding all folders may take a long time. Continue?",
                icon_style=wx.ICON_WARNING):
            return
        self.expanding_all = True
        try:
            for item in iter_tree_breadth_first(self, self.GetRootItem()):
                if not self.expanding_all:
                    return
                node = self.GetPyData(item)
                if node.type == 'd':
                    if not node.populated:
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

    def IsExpanded(self, item):
        return self.GetRootItem() == item or wx.TreeCtrl.IsExpanded(self, item)

    def Expand(self, item):
        if self.GetRootItem() != item:
            wx.TreeCtrl.Expand(self, item)

    @managed("cm")
    @coroutine
    def PopulateNode(self, node):
        if not node.populated:
            f = node.expand(self, self.monitor, self.filter)
            if isinstance(f, Future):
                yield f

    @managed("cm")
    @coroutine
    def ExpandNode(self, node):
        if not node.populated:
            try:
                yield self.PopulateNode(node)
            except OSError:
                return
        if node.populated:
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
            except OSError as e:
                dialogs.error(self, str(e))

    @managed("cm")
    @coroutine
    def NewFolder(self, node, name):
        path = os.path.join(node.path, name)
        try:
            yield async_call(os.mkdir, path)
            if self.IsExpanded(node.item):
                self.SelectLater(node.item, name)
        except OSError as e:
            dialogs.error(self, str(e))

    @managed("cm")
    @queued_coroutine("cq")
    def _InitialExpand(self, rootnode, toplevel):
        yield self.ExpandNode(rootnode)
        if isinstance(toplevel[0], SimpleNode):
            yield self.ExpandNode(toplevel[0])

    def SetTopLevel(self, toplevel=None):
        self.cm.cancel()
        self.cq.cancel()
        self.monitor_thread.clear()
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
                subpath = os.path.join(path, os.path.basename(node.path)) if path else node.path
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
            node = self.GetPyData(child_item)
            name = os.path.basename(node.path) or node.path.strip(os.path.sep)
            if name in expanded:
                yield self._ExpandPaths(child_item, sub_paths)

    def ExpandPaths(self, paths):
        rootpath = self.GetPyData(self.GetRootItem()).path
        paths = [split_path(path, rootpath) for path in paths]
        return self._ExpandPaths(self.GetRootItem(), paths)

    def ExpandPath(self, path):
        return self.ExpandPaths([path])

    def _SelectExpandedPath(self, item, path):
        node = self.GetPyData(item)
        if node.path == path:
            self.SelectItem(node.item)
        elif node.type == 'd':
            for child_item in iter_tree_children(self, item):
                self._SelectExpandedPath(child_item, path)

    @managed("cm")
    @coroutine
    def _SelectPath(self, path):
        yield self.ExpandPath(os.path.dirname(path))
        self._SelectExpandedPath(self.GetRootItem(), path)

    @managed("cm")
    @coroutine
    def _SelectExpandPath(self, path):
        yield self.ExpandPath(path)
        self._SelectExpandedPath(self.GetRootItem(), path)

    @managed("cm")
    @queued_coroutine("cq")
    def SelectPath(self, path):
        yield self._SelectPath(os.path.normpath(path))

    @managed("cm")
    @queued_coroutine("cq")
    def SelectExpandPath(self, path):
        yield self._SelectExpandPath(os.path.normpath(path))

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
    @queued_coroutine("cq")
    def LoadPerspective(self, p):
        expanded = p.get("expanded", ())
        if expanded:
            yield self.ExpandPaths(expanded)
        if "selected" in p:
            yield self._SelectPath(p["selected"])
