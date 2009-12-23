import os
import wx

class ProjectTree(wx.TreeCtrl):
    IM_FOLDER = 0
    IM_FILE = 1

    def __init__(self, parent, env, rootdir):
        wx.TreeCtrl.__init__(self, parent, style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        self.env = env
        self.rootdir = rootdir
        bmp_folder = wx.ArtProvider.GetBitmap(wx.ART_FOLDER)
        self.imglist = wx.ImageList(bmp_folder.GetWidth(), bmp_folder.GetHeight())
        self.imglist.Add(bmp_folder)
        self.imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE))
        self.SetImageList(self.imglist)
        self.UpdateTree()
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)

    def OnItemActivated(self, evt):
        item = evt.GetItem()
        path = self.GetPyData(item)
        if path:
            self.env.OpenFile(path)
        else:
            self.Toggle(item)

    def UpdateTree(self):
        self.DeleteAllItems()
        item = self.AddRoot("")
        self.Expand(item)
        treedict = {self.rootdir : item}
        for path in sorted(os.listdir(self.rootdir)):
            path = os.path.join(self.rootdir, path)
            if os.path.isdir(path):
                for path, dirnames, filenames in os.walk(path):
                    dirnames.sort()
                    filenames.sort()
                    item = self.AppendItem(
                        treedict[os.path.dirname(path)], os.path.basename(path), self.IM_FOLDER)
                    treedict[path] = item
                    for filename in filenames:
                        fileitem = self.AppendItem(item, filename, self.IM_FILE)
                        self.SetPyData(fileitem, os.path.join(path, filename))
