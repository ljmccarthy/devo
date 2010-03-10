import sys, os, stat, threading
import wx
import fsmonitor

import dialogs
from async import Task
from async_wx import async_call, coroutine, queued_coroutine, managed, CoroutineQueue, CoroutineManager
from util import iter_tree_children
from resources import load_bitmap

IM_FOLDER = 0
IM_FOLDER_DENIED = 1
IM_FOLDER_WAITING = 2
IM_FILE = 3

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

    def __init__(self, label, children):
        self.label = label
        self.children = children
        self.populated = False

    def expand(self, tree, rootitem, monitor):
        tree.SetItemImage(rootitem, IM_FOLDER)
        for node in self.children:
            item = tree.AppendItem(rootitem, node.label, IM_FOLDER)
            tree.SetPyData(item, node)
            tree.SetItemHasChildren(item, True)

class FSNode(object):
    __slots__ = ("populated", "path", "type", "item", "label")

    def __init__(self, path="", type="", label=""):
        self.populated = False
        self.path = path
        self.type = type
        self.item = None
        self.label = label or os.path.basename(path) or path

    @coroutine
    def expand(self, tree, rootitem, monitor):
        if not self.populated:
            self.populated = True
            self.item = rootitem
            files = []
            monitor.add_watch(self.path, self)
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
                        item = tree.AppendItem(rootitem, filename, IM_FOLDER)
                        tree.SetPyData(item, FSNode(path, 'd'))
                        tree.SetItemHasChildren(item, True)
            for filename, path in files:
                item = tree.AppendItem(rootitem, filename, IM_FILE)
                tree.SetPyData(item, FSNode(path, 'f'))
            tree.SetItemImage(rootitem, IM_FOLDER)

    def collapse(self, tree, rootitem, monitor):
        pass
        #monitor.remove_watch(self.path)
        #self.populated = False
        #self.item = None

    @coroutine
    def add(self, name, tree, monitor):
        if self.populated:
            path = os.path.join(self.path, name)
            type, image = (yield async_call(get_file_type_and_image, path))
            if type:
                item = dirtree_insert(tree, self.item, name, image)
                node = FSNode(path, type)
                tree.SetPyData(item, node)
                if type == 'd':
                    tree.SetItemHasChildren(item, True)

    def remove(self, name, tree, monitor):
        if self.populated:
            dirtree_delete(tree, self.item, name)

if sys.platform == "win32":
    import win32api
    from win32com.shell import shell, shellcon
    mycomputer = SimpleNode("My Computer",
                    [FSNode(drive, 'd') for drive in
                     win32api.GetLogicalDriveStrings().strip("\0").split("\0")])
    mydocs = shell.SHGetFolderPath(None, shellcon.CSIDL_PERSONAL, None, 0)
    toplevel = [mycomputer, FSNode(mydocs, 'd')]
else:
    toplevel = [FSNode("/", 'd')]

class DirTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, env, toplevel=toplevel):
        style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.BORDER_NONE
        wx.TreeCtrl.__init__(self, parent, style=style)
        self.env = env
        self.toplevel = toplevel
        self.cq_populate = CoroutineQueue()
        self.cm = CoroutineManager()
        self.monitor = fsmonitor.FSMonitorThread(self._OnFileSystemChanged)
        self.fsevts = []
        self.fsevts_lock = threading.Lock()
        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(load_bitmap("icons/folder.png"))
        self.imglist.Add(load_bitmap("icons/folder_denied.png"))
        self.imglist.Add(load_bitmap("icons/folder_waiting.png"))
        self.imglist.Add(load_bitmap("icons/file.png"))
        self.SetImageList(self.imglist)
        self.InitializeTree()
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        self.cm.cancel()

    def _OnFileSystemChanged(self, evt):
        with self.fsevts_lock:
            called = bool(self.fsevts)
            self.fsevts.append(evt)
            if not called:
                wx.CallAfter(lambda: wx.CallLater(200, self.OnFileSystemChanged))

    @managed("cm")
    @queued_coroutine("cq_populate")
    def OnFileSystemChanged(self):
        with self.fsevts_lock:
            evts = self.fsevts
            self.fsevts = []
        for evt in evts:
            if evt.action in (fsmonitor.FSEVT_CREATE, fsmonitor.FSEVT_MOVE_TO):
                yield evt.userobj.add(evt.name, self, self.monitor)
            elif evt.action in (fsmonitor.FSEVT_DELETE, fsmonitor.FSEVT_MOVE_FROM):
                evt.userobj.remove(evt.name, self, self.monitor)

    def OnItemActivated(self, evt):
        item = evt.GetItem()
        node = self.GetPyData(item)
        if node.type == 'f':
            self.env.OpenFile(node.path)
        elif node.type == 'd':
            self.Toggle(item)

    def OnItemExpanding(self, evt):
        item = evt.GetItem()
        node = self.GetPyData(item)
        if node.type == 'd' and not node.populated:
            self.ExpandNode(item, node)

    def OnItemCollapsed(self, evt):
        item = evt.GetItem()
        node = self.GetPyData(item)
        if node.type == 'd' and node.populated:
            self.CollapseNode(item, node)

    @managed("cm")
    @queued_coroutine("cq_populate")
    def ExpandNode(self, item, node):
        yield node.expand(self, item, self.monitor)
        self.Expand(item)

    def CollapseNode(self, item, node):
        node.collapse(self, item, self.monitor)

    @managed("cm")
    @coroutine
    def InitializeTree(self):
        self.DeleteAllItems()
        rootitem = self.AddRoot("")
        if len(self.toplevel) == 1:
            self.SetPyData(rootitem, self.toplevel[0])
            toplevel_items = [rootitem]
        else:
            self.SetPyData(rootitem, FSNode())
            toplevel_items = []
            for node in self.toplevel:
                item = self.AppendItem(rootitem, node.label, IM_FOLDER)
                self.SetPyData(item, node)
                self.SetItemHasChildren(item, True)
                toplevel_items.append(item)
        for item in toplevel_items:
            try:
                node = self.GetPyData(item)
                yield self.ExpandNode(item, node)
            except OSError:
                self.SetItemImage(item, IM_FOLDER_DENIED)
