import sys, os, stat, threading, time
import wx
import fsmonitor

import dialogs, fileutil
from async import Task
from async_wx import async_call, coroutine, queued_coroutine, managed, CoroutineQueue, CoroutineManager
from menu import Menu, MenuItem, MenuSeparator
from util import iter_tree_children, frozen_window
from resources import load_bitmap

ID_EDIT = wx.NewId()
ID_OPEN = wx.NewId()
ID_RENAME = wx.NewId()
ID_DELETE = wx.NewId()
ID_NEW_FOLDER = wx.NewId()

file_context_menu = Menu("", [
    MenuItem(ID_OPEN, "&Open"),
    MenuItem(ID_EDIT, "&Edit with Devo"),
    MenuSeparator,
    MenuItem(ID_RENAME, "&Rename"),
    MenuItem(ID_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_NEW_FOLDER, "&New Folder"),
])

dir_context_menu = Menu("", [
    MenuItem(ID_OPEN, "&Open"),
    MenuSeparator,
    MenuItem(ID_RENAME, "&Rename"),
    MenuItem(ID_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_NEW_FOLDER, "&New Folder"),
])

IM_FOLDER = 0
IM_FOLDER_DENIED = 1
IM_FILE = 2

def dirtree_insert(tree, parent_item, text, image):
    i = 0
    text_lower = text.lower()
    for i, item in enumerate(iter_tree_children(tree, parent_item)):
        item_text = tree.GetItemText(item)
        if item_text == text:
            return item
        if image != IM_FILE and tree.GetItemImage(item) == IM_FILE:
            return tree.InsertItemBefore(parent_item, i, text, image)
        if item_text.lower() > text_lower:
            if not (image == IM_FILE and tree.GetItemImage(item) != IM_FILE):
                return tree.InsertItemBefore(parent_item, i, text, image)
    return tree.AppendItem(parent_item, text, image)

def dirtree_delete(tree, parent_item, text):
    for item in iter_tree_children(tree, parent_item):
        if text == tree.GetItemText(item):
            sel_item = tree.GetNextSibling(item)
            if not sel_item.IsOk():
                sel_item = tree.GetPrevSibling(item)
            if sel_item.IsOk():
                tree.SelectItem(sel_item)
            tree.Delete(item)
            break

def get_file_type_and_image(path):
    try:
        st = os.stat(path)
        if stat.S_ISREG(st.st_mode):
            return 'f', IM_FILE
        elif stat.S_ISDIR(st.st_mode):
            return 'd', IM_FOLDER
    except OSError:
        pass
    return None, None

class SimpleNode(object):
    type = None
    context_menu = None

    def __init__(self, label, children):
        self.label = label
        self.children = children
        self.populated = False

    def expand(self, tree, rootitem, monitor):
        tree.SetItemImage(rootitem, IM_FOLDER)
        for node in self.children:
            item = tree.AppendItem(rootitem, node.label, IM_FOLDER)
            tree.SetItemNode(item, node)
            tree.SetItemHasChildren(item, True)

class FSNode(object):
    __slots__ = ("populated", "path", "type", "item", "watch", "label")

    def __init__(self, path="", type="", label=""):
        self.populated = False
        self.path = path
        self.type = type
        self.item = None
        self.watch = None
        self.label = label or os.path.basename(path) or path

    @coroutine
    def expand(self, tree, monitor):
        if not self.populated:
            self.populated = True
            files = []
            self.watch = monitor.add_watch(self.path, self)
            expanded = tree.IsExpanded(self.item)
            for filename in sorted((yield async_call(os.listdir, self.path)),
                                   key=lambda x: x.lower()):
                path = os.path.join(self.path, filename)
                try:
                    st = (yield async_call(os.stat, path))
                except OSError:
                    pass
                else:
                    if stat.S_ISREG(st.st_mode):
                        files.append((filename, path))
                    elif stat.S_ISDIR(st.st_mode):
                        try:
                            listable = (yield async_call(os.access, path, os.X_OK))
                        except OSError, e:
                            listable = False
                        image = IM_FOLDER if listable else IM_FOLDER_DENIED
                        item = tree.AppendItem(self.item, filename, image)
                        tree.SetItemNode(item, FSNode(path, 'd'))
                        tree.SetItemHasChildren(item, listable)
                        if not expanded:
                            tree.Expand(self.item)
                            expanded = True
            for filename, path in files:
                item = tree.AppendItem(self.item, filename, IM_FILE)
                tree.SetItemNode(item, FSNode(path, 'f'))
            if not expanded:
                tree.Expand(self.item)
                expanded = True
            tree.SetItemImage(self.item, IM_FOLDER)

    def collapse(self, tree, monitor):
        pass
        #monitor.remove_watch(self.watch)
        #self.populated = False

    @coroutine
    def add(self, name, tree, monitor):
        if self.populated:
            path = os.path.join(self.path, name)
            type, image = (yield async_call(get_file_type_and_image, path))
            if type:
                item = dirtree_insert(tree, self.item, name, image)
                node = FSNode(path, type)
                tree.SetItemNode(item, node)
                if type == 'd':
                    tree.SetItemHasChildren(item, True)
                yield item

    def remove(self, name, tree, monitor):
        if self.populated:
            dirtree_delete(tree, self.item, name)

    @property
    def context_menu(self):
        if self.type == 'f':
            return file_context_menu
        elif self.type == 'd':
            return dir_context_menu

def MakeTopLevel():
    if sys.platform == "win32":
        import win32api
        from win32com.shell import shell, shellcon
        mycomputer = SimpleNode("My Computer",
                        [FSNode(drive, 'd') for drive in
                         win32api.GetLogicalDriveStrings().strip("\0").split("\0")])
        mydocs = shell.SHGetFolderPath(None, shellcon.CSIDL_PERSONAL, None, 0)
        return [mycomputer, FSNode(mydocs, 'd')]
    else:
        return [FSNode("/", 'd')]

class DirTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, env, toplevel=None):
        style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.BORDER_NONE
        wx.TreeCtrl.__init__(self, parent, style=style)
        self.env = env
        self.toplevel = toplevel or MakeTopLevel()
        self.cq_populate = CoroutineQueue()
        self.cm = CoroutineManager()
        self.monitor = fsmonitor.FSMonitorThread(self._OnFileSystemChanged)
        self.fsevts = []
        self.fsevts_lock = threading.Lock()
        self.select_later_parent = None
        self.select_later_name = None
        self.select_later_time = 0
        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(load_bitmap("icons/folder.png"))
        self.imglist.Add(load_bitmap("icons/folder_denied.png"))
        self.imglist.Add(load_bitmap("icons/file.png"))
        self.SetImageList(self.imglist)
        self.InitializeTree()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnItemRightClicked)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnItemEndLabelEdit)
        self.Bind(wx.EVT_MENU, self.OnItemEdit, id=ID_EDIT)
        self.Bind(wx.EVT_MENU, self.OnItemOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnItemRename, id=ID_RENAME)
        self.Bind(wx.EVT_MENU, self.OnItemDelete, id=ID_DELETE)
        self.Bind(wx.EVT_MENU, self.OnNewFolder, id=ID_NEW_FOLDER)

    def OnClose(self, evt):
        self.cm.cancel()

    def _OnFileSystemChanged(self, evt):
        with self.fsevts_lock:
            called = bool(self.fsevts)
            self.fsevts.append(evt)
            if not called:
                wx.CallAfter(lambda: wx.CallLater(100, self.OnFileSystemChanged))

    def SelectLater(self, parent, name, timeout=1):
        self.select_later_parent = parent
        self.select_later_name = name
        self.select_later_time = time.time() + timeout

    @managed("cm")
    @queued_coroutine("cq_populate")
    def OnFileSystemChanged(self):
        with self.fsevts_lock:
            evts = self.fsevts
            self.fsevts = []
        with frozen_window(self):
            for evt in evts:
                if evt.action in (fsmonitor.FSEVT_CREATE, fsmonitor.FSEVT_MOVE_TO):
                    item = (yield evt.userobj.add(evt.name, self, self.monitor))
                    if item:
                        if evt.name == self.select_later_name \
                        and self.GetItemParent(item) == self.select_later_parent:
                            if time.time() < self.select_later_time:
                                self.SelectItem(item)
                            self.select_later_name = None
                            self.select_later_parent = None
                            self.select_later_time = 0
                elif evt.action in (fsmonitor.FSEVT_DELETE, fsmonitor.FSEVT_MOVE_FROM):
                    evt.userobj.remove(evt.name, self, self.monitor)

    def OnItemActivated(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'f':
            self.env.OpenFile(node.path)
        elif node.type == 'd':
            self.Toggle(node.item)

    def OnItemExpanding(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd' and not node.populated:
            self.ExpandNode(node)

    def OnItemCollapsed(self, evt):
        node = self.GetEventNode(evt)
        if node.type == 'd' and node.populated:
            self.CollapseNode(node)

    def OnItemRightClicked(self, evt):
        self.SelectItem(evt.GetItem())
        node = self.GetEventNode(evt)
        menu = node.context_menu
        if menu:
            self.PopupMenu(menu.Create())

    def OnItemEndLabelEdit(self, evt):
        if not evt.IsEditCancelled():
            evt.Veto()
            node = self.GetEventNode(evt)
            self.RenameNode(node, evt.GetLabel())

    def OnItemEdit(self, evt):
        node = self.GetSelectedNode()
        if node.type == 'f':
            self.env.OpenFile(node.path)

    def OnItemOpen(self, evt):
        node = self.GetSelectedNode()
        if node.type in 'fd':
            self._shell_open(node.path)

    def OnItemRename(self, evt):
        node = self.GetSelectedNode()
        if node.type in 'fd':
            self.EditLabel(node.item)

    def OnItemDelete(self, evt):
        node = self.GetSelectedNode()
        next_item = self.GetNextSibling(node.item)
        if dialogs.ask_delete(self, node.path):
            self._remove(node.path)

    def OnNewFolder(self, evt):
        node = self.GetSelectedNode()
        if node.type != 'd':
            node = self.GetPyData(self.GetItemParent(node.item))
        name = dialogs.get_text_input(self,
            "New Folder",
            "Please enter new folder name:")
        if name:
            self.NewFolder(node, name)

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

    @managed("cm")
    @queued_coroutine("cq_populate")
    def ExpandNode(self, node):
        yield node.expand(self, self.monitor)
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
    def _remove(self, path):
        try:
            yield async_call(fileutil.remove, path)
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
            return async_call(fileutil.shell_open, path)
        except OSError, e:
            dialogs.error(self, str(e))

    @managed("cm")
    @coroutine
    def InitializeTree(self):
        self.DeleteAllItems()
        rootitem = self.AddRoot("")
        if len(self.toplevel) == 1:
            self.SetItemNode(rootitem, self.toplevel[0])
            toplevel_items = [rootitem]
        else:
            self.SetItemNode(rootitem, FSNode())
            toplevel_items = []
            for node in self.toplevel:
                item = self.AppendItem(rootitem, node.label, IM_FOLDER)
                self.SetItemNode(item, node)
                self.SetItemHasChildren(item, True)
                toplevel_items.append(item)
        for item in toplevel_items:
            try:
                node = self.GetPyData(item)
                yield self.ExpandNode(node)
            except OSError:
                self.SetItemImage(item, IM_FOLDER_DENIED)
