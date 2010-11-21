import collections
import os, os.path
import stat
import wx

import fileutil
from async import async_call, coroutine
from dirtree_constants import *
from menu import Menu, MenuItem, MenuSeparator
from util import iter_tree_children

file_context_menu = Menu("", [
    MenuItem(ID_NEW_FOLDER, "&New Folder"),
    MenuSeparator,
    MenuItem(ID_OPEN, "&Open"),
    MenuItem(ID_EDIT, "&Edit with Devo"),
    MenuItem(ID_RENAME, "&Rename"),
    MenuItem(ID_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID_COLLAPSE_ALL, "&Collapse All"),
])

dir_context_menu = Menu("", [
    MenuItem(ID_NEW_FOLDER, "&New Folder"),
    MenuSeparator,
    MenuItem(ID_OPEN, "&Open"),
    MenuItem(ID_RENAME, "&Rename"),
    MenuItem(ID_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID_COLLAPSE_ALL, "&Collapse All"),    
])

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

class SimpleNode(object):
    type = 'd'
    path = ""
    context_menu = None

    def __init__(self, label, children):
        self.label = label
        self.children = children
        self.state = NODE_UNPOPULATED
        self.item = None

    def expand(self, tree, monitor, filter):
        if self.state == NODE_UNPOPULATED:
            tree.SetItemImage(self.item, IM_FOLDER)
            for node in self.children:
                item = tree.AppendItem(self.item, node.label, IM_FOLDER)
                tree.SetItemNode(item, node)
                tree.SetItemHasChildren(item, True)
            self.state = NODE_POPULATED

    def collapse(self, tree, monitor):
        pass

class FSNode(object):
    __slots__ = ("state", "path", "type", "item", "watch", "label")

    def __init__(self, path, type, label=""):
        self.state = NODE_UNPOPULATED
        self.path = path
        self.type = type
        self.item = None
        self.watch = None
        self.label = label or os.path.basename(path) or path

    @coroutine
    def _do_expand(self, tree, monitor, filter):
        self.watch = monitor.add_dir_watch(self.path, user=self)
        dirs = []
        files = []            
        for info in (yield async_call(listdir, self.path)):
            if not filter(info):
                continue
            path = os.path.join(self.path, info.filename)
            if info.is_file:
                files.append(FSNode(path, 'f'))
            elif info.is_dir:
                dirs.append((FSNode(path, 'd'), info.listable))
        for node, listable in dirs:
            image = IM_FOLDER if listable else IM_FOLDER_DENIED
            item = tree.AppendItem(self.item, node.label, image)
            tree.SetItemNode(item, node)
            tree.SetItemHasChildren(item, listable)
        for node in files:
            item = tree.AppendItem(self.item, node.label, IM_FILE)
            tree.SetItemNode(item, node)
        tree.SetItemImage(self.item, IM_FOLDER)
        tree.SetItemHasChildren(self.item, tree.GetFirstChild(self.item)[0].IsOk())

    @coroutine
    def expand(self, tree, monitor, filter):
        if self.state == NODE_UNPOPULATED:
            self.state = NODE_POPULATING
            yield self._do_expand(tree, monitor, filter)
            self.state = NODE_POPULATED

    def collapse(self, tree, monitor):
        pass
        #monitor.remove_watch(self.watch)
        #self.populated = False

    @coroutine
    def add(self, name, tree, monitor, filter):
        if self.state == NODE_POPULATED:
            try:
                info = (yield async_call(get_file_info, self.path, name))
            except OSError, e:
                return
            if not filter(info):
                return
            if info.is_file:
                type = 'f'
                image = IM_FILE
            elif info.is_dir:
                type = 'd'
                image = IM_FOLDER
            item = dirtree_insert(tree, self.item, name, image)
            node = FSNode(info.path, type)
            tree.SetItemNode(item, node)
            if type == 'd':
                tree.SetItemHasChildren(item, True)
            tree.SetItemHasChildren(self.item, True)
            yield item

    def remove(self, name, tree, monitor):
        if self.state == NODE_POPULATED:
            dirtree_delete(tree, self.item, name)

    @property
    def context_menu(self):
        if self.type == 'f':
            return file_context_menu
        elif self.type == 'd':
            return dir_context_menu

def DirNode(path):
    return FSNode(path, 'd')
