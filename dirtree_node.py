import collections
import os, os.path
import stat
import traceback
import wx

import fileutil
from async import async_call, coroutine
from dirtree_constants import *
from util import iter_tree_children

class FileInfo(collections.namedtuple("FileInfo", "filename dirpath stat_result listable hidden")):
    @property
    def path(self):
        return os.path.join(self.dirpath, self.filename)
    @property
    def is_file(self):
        return stat.S_ISREG(self.stat_result.st_mode)
    @property
    def is_dir(self):
        return stat.S_ISDIR(self.stat_result.st_mode)
    @property
    def node_type(self):
        if stat.S_ISREG(self.stat_result.st_mode):
            return 'f'
        if stat.S_ISDIR(self.stat_result.st_mode):
            return 'd'
        return ''

def get_file_info(dirpath, filename):
    path = os.path.join(dirpath, filename)
    stat_result = os.stat(path)
    hidden = fileutil.is_hidden_file(path)
    if stat.S_ISDIR(stat_result.st_mode):
        try:
            listable = os.access(path, os.X_OK)
        except OSError:
            listable = False
    else:
        listable = False
    return FileInfo(filename, dirpath, stat_result, listable, hidden)

def listdir(dirpath):
    result = []
    for filename in os.listdir(dirpath):
        try:
            result.append(get_file_info(dirpath, filename))
        except OSError:
            pass
    result.sort(key=lambda info: info.filename.lower())
    return result

def dirtree_insert(tree, parent_item, text, image):
    text_lower = text.lower()

    # Optimise common case when expanding directory for the first time
    item = tree.GetLastChild(parent_item)
    if item.IsOk() and tree.GetItemText(item) < text_lower and (
            image == IM_FILE or tree.GetItemImage(item) != IM_FILE):
        return tree.AppendItem(parent_item, text, image)

    # Search for the position to insert
    for pos, item in enumerate(iter_tree_children(tree, parent_item)):
        item_text = tree.GetItemText(item)
        if item_text == text:
            return item
        if image != IM_FILE and tree.GetItemImage(item) == IM_FILE:
            return tree.InsertItemBefore(parent_item, pos, text, image)
        if item_text.lower() > text_lower:
            if not (image == IM_FILE and tree.GetItemImage(item) != IM_FILE):
                return tree.InsertItemBefore(parent_item, pos, text, image)

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

class SimpleNode(object):
    type = 'd'
    path = ""

    def __init__(self, label, children):
        self.label = label
        self.children = children
        self.populated = False
        self.item = None

    def expand(self, tree, monitor, filter):
        if not self.populated:
            self.populated = True
            tree.SetItemImage(self.item, IM_FOLDER)
            for node in self.children:
                item = tree.AppendItem(self.item, node.label, IM_FOLDER)
                tree.SetItemNode(item, node)
                tree.SetItemHasChildren(item, True)

    def collapse(self, tree, monitor):
        pass

class FSNode(object):
    __slots__ = ("populated", "path", "type", "item", "watch", "label")

    def __init__(self, path, type, label=""):
        self.populated = False
        self.path = path
        self.type = type
        self.item = None
        self.watch = None
        self.label = label or os.path.basename(path) or path

    def insert(self, tree, file_info):
        node = FSNode(file_info.path, file_info.node_type)
        image = IM_FILE if node.type == 'f' else IM_FOLDER if file_info.listable else IM_FOLDER_DENIED
        item = dirtree_insert(tree, self.item, node.label, image)
        tree.SetItemNode(item, node)
        tree.SetItemHasChildren(item, node.type == 'd')
        tree.SetItemHasChildren(self.item, True)
        return item

    @coroutine
    def expand(self, tree, monitor, filter):
        if self.type == 'd' and not self.populated:
            try:
                if not self.watch:
                    self.watch = monitor.add_dir_watch(self.path, user=self)
                for file_info in (yield async_call(listdir, self.path)):
                    if filter(file_info):
                        self.insert(tree, file_info)
                tree.SetItemImage(self.item, IM_FOLDER)
                tree.SetItemHasChildren(self.item, tree.GetFirstChild(self.item)[0].IsOk())
            except Exception:
                self.populated = False
                print traceback.format_exc()
            else:
                self.populated = True

    def collapse(self, tree, monitor):
        pass
        #monitor.remove_watch(self.watch)
        #self.populated = False

    @coroutine
    def add(self, name, tree, monitor, filter):
        try:
            file_info = (yield async_call(get_file_info, self.path, name))
            if file_info.node_type and filter(file_info):
                yield self.insert(tree, file_info)
        except OSError as e:
            pass

    def remove(self, name, tree, monitor):
        dirtree_delete(tree, self.item, name)
        child_item = tree.GetFirstChild(self.item)[0]
        tree.SetItemHasChildren(self.item, child_item.IsOk())

def DirNode(path):
    return FSNode(path, 'd')
