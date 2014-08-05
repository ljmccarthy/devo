import collections
import os, os.path
import stat
import traceback
import wx

import fileutil
from async import async_call, coroutine
from dirtree_constants import *
from util import iter_tree_children, natural_order_key

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

def list_dir_file_info_sorted(dirpath):
    result = []
    for filename in os.listdir(dirpath):
        try:
            result.append(get_file_info(dirpath, filename))
        except OSError:
            pass
    result.sort(key=lambda info: natural_order_key(info.filename))
    return result

def dirtree_insert_node(tree, parent_item, node, image):
    # Optimise common case when expanding directory for the first time
    item = tree.GetLastChild(parent_item)
    if item.IsOk() and tree.GetPyData(item) < node:
        item = tree.AppendItem(parent_item, node.label, image)
        tree.SetItemNode(item, node)
        return item, node

    # Search for the position to insert
    for index, existing_item in enumerate(iter_tree_children(tree, parent_item)):
        existing_node = tree.GetPyData(existing_item)
        if node == existing_node:
            return existing_item, existing_node
        elif node < existing_node:
            item = tree.InsertItemBefore(parent_item, index, node.label, image)
            tree.SetItemNode(item, node)
            return item, node

    item = tree.AppendItem(parent_item, node.label, image)
    tree.SetItemNode(item, node)
    return item, node

def dirtree_create_node(tree, parent_item, file_info):
    node = FSNode(file_info.path, file_info.node_type)
    image = IM_FILE if node.type == 'f' else IM_FOLDER if file_info.listable else IM_FOLDER_DENIED
    item, node = dirtree_insert_node(tree, parent_item, node, image)
    tree.SetItemHasChildren(item, node.type == 'd')
    tree.SetItemHasChildren(parent_item, True)
    return item

def dirtree_delete(tree, parent_item, text):
    for item in iter_tree_children(tree, parent_item):
        if text == tree.GetItemText(item):
            select_item = tree.GetNextSibling(item)
            if not select_item.IsOk():
                select_item = tree.GetPrevSibling(item)
                if not select_item.IsOk():
                    select_item = tree.GetNextSibling(item)
            if select_item.IsOk():
                tree.SelectItem(select_item)
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

    def __lt__(self, other):
        if not isinstance(other, FSNode):
            raise TypeError()
        if self.type != other.type:
            return self.type == 'd' and other.type == 'f'
        return natural_order_key(self.label) < natural_order_key(other.label)

    def __gt__(self, other):
        if not isinstance(other, FSNode):
            raise TypeError()
        if self.type != other.type:
            return self.type == 'f' and other.type == 'd'
        return natural_order_key(self.label) > natural_order_key(other.label)

    def __eq__(self, other):
        if not isinstance(other, FSNode):
            raise TypeError()
        return self.type == other.type and self.label == other.label

    def __ne__(self, other):
        return not (self == other)

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    @coroutine
    def expand(self, tree, monitor, filter):
        if self.type == 'd' and not self.populated:
            try:
                if not self.watch:
                    self.watch = monitor.add_dir_watch(self.path, user=self)
                for file_info in (yield async_call(list_dir_file_info_sorted, self.path)):
                    if file_info.node_type and filter(file_info):
                        dirtree_create_node(tree, self.item, file_info)
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
                yield dirtree_create_node(tree, self.item, file_info)
        except OSError as e:
            pass

    def remove(self, name, tree, monitor):
        dirtree_delete(tree, self.item, name)
        child_item = tree.GetFirstChild(self.item)[0]
        tree.SetItemHasChildren(self.item, child_item.IsOk())

def DirNode(path):
    return FSNode(path, 'd')
