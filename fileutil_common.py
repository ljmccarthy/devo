import wx
import os.path
from dialogs import dialogs

def destination_is_same(srcpath, dstpath):
    return os.path.dirname(os.path.realpath(srcpath)) == os.path.realpath(dstpath)

def ask_delete_file(parent, path):
    return dialogs.message_dialog(parent,
        "Are you sure you want to delete '%s'?" % path,
        "Confirm Delete",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

def ask_move_file(parent, srcpath, dstpath):
    return dialogs.message_dialog(parent,
        "Are you sure you want to move:\n\t%s\n\nDestination:\n\t%s" % (srcpath, dstpath),
        "Confirm Move",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

def ask_copy_file(parent, srcpath, dstpath):
    return dialogs.message_dialog(parent,
        "Are you sure you want to copy:\n\t%s\n\nDestination:\n\t%s" % (srcpath, dstpath),
        "Confirm Copy",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

__all__ = (
    "destination_is_same",
    "ask_delete_file",
    "ask_move_file",
    "ask_copy_file",
)
