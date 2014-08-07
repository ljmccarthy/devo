import os
import wx

class Dialogs(object):
    def __init__(self, prefix=""):
        self._prefix = prefix
        self._paths = {}

    def save_state(self):
        return {"paths" : self._paths}

    def load_state(self, state):
        self._paths = state.get("paths", {}).copy()

    def _make_caption(self, caption):
        return (self._prefix + " - " + caption) if caption else self._prefix

    def message_dialog(self, parent, message, caption, style):
        dlg = wx.MessageDialog(parent, message, self._make_caption(caption), style)
        try:
            return dlg.ShowModal()
        finally:
            dlg.Destroy()

    def error(self, parent, message, caption="Error"):
        self.message_dialog(parent, message, caption, wx.OK | wx.ICON_ERROR)

    def info(self, parent, message, caption=""):
        self.message_dialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)

    def yes_no(self, parent, message, caption="", icon_style=wx.ICON_QUESTION):
        return self.message_dialog(parent, message, caption,
            wx.YES_NO | wx.NO_DEFAULT | icon_style) == wx.ID_YES

    def _get_file_dialog(self, parent, message, path, wildcard, context, style):
        if wx.Platform == "__WXMAC__":
            message = ""
        else:
            message = self._make_caption(message)

        if not path and context:
            path = self._paths.get(context, path)

        dlg = wx.FileDialog(parent, wildcard=wildcard, message=message, defaultDir=path, style=style)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                selected_path = dlg.GetPath()
                if context:
                    self._paths[context] = os.path.dirname(selected_path)
                return selected_path
        finally:
            dlg.Destroy()

    def get_file_to_open(self, parent, message="Open File", path="", wildcard="All Files|*", context=""):
        return self._get_file_dialog(parent, message, path, wildcard, context, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

    def get_file_to_save(self, parent, message="Save File", path="", wildcard="All Files|*", context=""):
        return self._get_file_dialog(
            parent, message, path, wildcard, context, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

    def get_directory(self, parent, message="Select Folder", path=""):
        from dirdialog import DirDialog
        dlg = DirDialog(parent, message=message, select_path=path)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        finally:
            dlg.Destroy()

    def ask_save_changes(self, parent, path=""):
        from save_changes_dialog import SaveChangesDialog
        path = os.path.basename(path)
        if path:
            message = "File '%s' has been modified. Save changes?" % path
        else:
            message = "Save unsaved changes?"
        dlg = SaveChangesDialog(parent, message, self._make_caption("Unsaved Changes"))
        try:
            return dlg.ShowModal()
        finally:
            dlg.Destroy()

    def ask_overwrite(self, parent, path):
        return self.yes_no(parent, 
            "A file named '%s' already exists. Overwrite?" % path,
            "Confirm Overwrite")

    def ask_reload(self, parent, path):
        return self.yes_no(parent,
            "The file '%s' has been modified by another program. Do you want to reload?" % path,
            "Modified File")

    def ask_unload(self, parent, path):
        return not self.yes_no(parent,
            "The file '%s' has been deleted by another program. Do you want to keep the file open?" % path,
            "Deleted File")

    def ask_open_binary(self, parent, path):
        return self.yes_no(parent,
            "The file '%s' is not a text file. Open anyway?" % path,
            "Open Binary File")

    def get_text_input(self, *args, **kwargs):
        from text_input_dialog import TextInputDialog
        dlg = TextInputDialog(*args, **kwargs)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
        finally:
            dlg.Destroy()

dialogs = Dialogs("Devo")
