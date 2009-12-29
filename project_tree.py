import os
import wx
from async_wx import coroutine_method, WxScheduled

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
IM_FILE = 1

def IterTreeChildren(tree, item):
    item = tree.GetFirstChild(item)[0]
    while item.IsOk():
        yield item
        item = tree.GetNextSibling(item)

class ProjectTree(wx.TreeCtrl, WxScheduled):
    def __init__(self, parent, env, rootdir):
        style = wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT
        wx.TreeCtrl.__init__(self, parent, style=style)
        self.env = env
        self.rootdir = rootdir
        self.imglist = wx.ImageList(16, 16)
        self.imglist.Add(LoadBitmap("icons/folder.png"))
        self.imglist.Add(LoadBitmap("icons/file.png"))
        self.SetImageList(self.imglist)
        self.UpdateTree()
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

    @coroutine_method
    def PopulateNode(self, rootitem, rootnode):
        for item in IterTreeChildren(self, rootitem):
            node = self.GetPyData(item)
            if node.type == 'd':
                yield self.PopulateDirTree(item, node.path)
        rootnode.populated = True

    @coroutine_method
    def PopulateDirTree(self, rootitem, rootpath):
        files = []
        for filename in sorted((yield self.async_call(os.listdir, rootpath))):
            path = os.path.join(rootpath, filename)
            if (yield self.async_call(os.path.isfile, path)):
                files.append((filename, path))
            elif (yield self.async_call(os.path.isdir, path)):
                item = self.AppendItem(rootitem, filename, IM_FOLDER)
                self.SetPyData(item, FSNode(path, 'd'))
        for filename, path in files:
            item = self.AppendItem(rootitem, filename, IM_FILE)
            self.SetPyData(item, FSNode(path, 'f'))

    @coroutine_method
    def UpdateTree(self):
        self.DeleteAllItems()
        rootitem = self.AddRoot("")
        self.Expand(rootitem)
        yield self.PopulateDirTree(rootitem, self.rootdir)
        for item in IterTreeChildren(self, rootitem):
            node = self.GetPyData(item)
            if node.type == 'd':
                yield self.PopulateDirTree(item, node.path)
