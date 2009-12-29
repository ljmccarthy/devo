import os
import stat
import wx
from async_wx import async_call, coroutine
import dialogs

def LoadBitmap(filename):
    bmp = wx.Bitmap(filename)
    if not bmp.Ok():
        raise IOError("Failed to load bitmap: %r" % filename)
    return bmp

class FSNode(object):
    __slots__ = ("path", "type", "populated")

    def __init__(self, path, type):
        self.path = path
        self.type = type
        self.populated = False

IM_FOLDER = 0
IM_FOLDER_DENIED = 1
IM_FILE = 2

def IterTreeChildren(tree, item):
    item = tree.GetFirstChild(item)[0]
    while item.IsOk():
        yield item
        item = tree.GetNextSibling(item)

class ProjectTree(wx.TreeCtrl):
    def __init__(self, parent, env, rootdir):
        style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT
        wx.TreeCtrl.__init__(self, parent, style=style)
        self.env = env
        self.rootdir = rootdir
        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(LoadBitmap("icons/folder.png"))
        self.imglist.Add(LoadBitmap("icons/folder_denied.png"))
        self.imglist.Add(LoadBitmap("icons/file.png"))
        self.SetImageList(self.imglist)
        self.InitializeTree()
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)

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
            self.PopulateNode(item, node)

    @coroutine
    def PopulateNode(self, rootitem, rootnode):
        rootnode.populated = True
        for item in IterTreeChildren(self, rootitem):
            node = self.GetPyData(item)
            if node.type == 'd':
                try:
                    yield self.PopulateDirTree(item, node.path)
                except OSError:
                    self.SetItemImage(item, IM_FOLDER_DENIED)

    @coroutine
    def PopulateDirTree(self, rootitem, rootpath):
        files = []
        for filename in sorted((yield async_call(os.listdir, rootpath)), key=lambda x: x.lower()):
            path = os.path.join(rootpath, filename)
            try:
                st = (yield async_call(os.stat, path))
            except OSError:
                pass
            else:
                if stat.S_ISREG(st.st_mode):
                    files.append((filename, path))
                elif stat.S_ISDIR(st.st_mode):
                    item = self.AppendItem(rootitem, filename, IM_FOLDER)
                    self.SetPyData(item, FSNode(path, 'd'))
        for filename, path in files:
            item = self.AppendItem(rootitem, filename, IM_FILE)
            self.SetPyData(item, FSNode(path, 'f'))

    @coroutine
    def InitializeTree(self):
        self.DeleteAllItems()
        rootitem = self.AddRoot("")
        rootnode = FSNode(self.rootdir, 'd')
        self.SetPyData(rootitem, rootnode)
        self.Expand(rootitem)
        try:
            yield self.PopulateDirTree(rootitem, self.rootdir)
            yield self.PopulateNode(rootitem, rootnode)
        except OSError, exn:
            dialogs.error(self, "Error: %s" % exn)
