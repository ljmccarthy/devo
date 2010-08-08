import os
import wx

from dirdialog import DirDialog
from save_changes_dialog import SaveChangesDialog
from text_input_dialog import TextInputDialog

def message_dialog(parent, message, caption, style):
    if not caption:
        caption = wx.GetApp().GetAppName()
    dlg = wx.MessageDialog(parent, message, caption, style)
    try:
        return dlg.ShowModal()
    finally:
        dlg.Destroy()

def error(parent, message, caption="Error"):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_ERROR)

def info(parent, message, caption=""):
    message_dialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)

_saved_paths = {}

def _get_file_dialog(parent, message, path, wildcard, context, style):
    if context and not path:
        path = _saved_paths.get(context, "")
    dlg = wx.FileDialog(parent, wildcard=wildcard, message=message, defaultDir=path, style=style)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            selected_path = dlg.GetPath()
            if context:
                _saved_paths[context] = os.path.dirname(selected_path)
            return selected_path
    finally:
        dlg.Destroy()

def get_file_to_open(parent, message="Open File", path="", wildcard="All Files|*", context=""):
    return _get_file_dialog(parent, message, path, wildcard, context, 0)

def get_file_to_save(parent, message="Save File", path="", wildcard="All Files|*", context=""):
    return _get_file_dialog(
        parent, message, path, wildcard, context, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

def get_directory(parent, message="Select Folder", path=""):
    dlg = DirDialog(parent, message=message, select_path=path)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetPath()
    finally:
        dlg.Destroy()

def ask_save_changes(parent, path=""):
    path = os.path.basename(path)
    if path:
        message = "File '%s' has been modified. Save changes?" % path
    else:
        message = "Save unsaved changes?"
    dlg = SaveChangesDialog(parent, message)
    try:
        return dlg.ShowModal()
    finally:
        dlg.Destroy()

def ask_overwrite(parent, path):
    return message_dialog(parent, 
        "A file named '%s' already exists. Overwrite?" % path,
        "Confirm Overwrite",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

def ask_delete(parent, path):
    return message_dialog(parent,
        "Are you sure you want to delete '%s'?" % path,
        "Confirm Delete",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) == wx.ID_YES

def get_text_input(*args, **kwargs):
    dlg = TextInputDialog(*args, **kwargs)
    try:
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.textctrl.GetValue()
    finally:
        dlg.Destroy()
