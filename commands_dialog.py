import wx, collections
from accelerator import parse_accelerator, unparse_accelerator
from dialogs import dialogs

command_help = """\
Commands may use the following environment variables:

$CURRENT_FILE - Current file
$CURRENT_DIR - Directory of current file
$CURRENT_BASENAME - Base filename of current file
$PROJECT_ROOT - Project root directory
"""

Command = collections.namedtuple("Command", "name accel cmdline")

class EditCommandDialog(wx.Dialog):
    def __init__(self, parent, name="", accel="", cmdline=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Edit Command", style=style)

        self.text_name = wx.TextCtrl(self, value=name)
        self.text_accel = wx.TextCtrl(self, value=accel)
        self.text_cmdline = wx.TextCtrl(self, value=cmdline)

        grid = wx.FlexGridSizer(2, 2, 5, 5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Name in Menu"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.text_name, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Accelerator"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.text_accel, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Shell Command"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.text_cmdline, 0, wx.EXPAND)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticText(self, label=command_help), 0, wx.ALL, 5)
        main_sizer.Add(grid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btn_sizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_sizer, 1, wx.EXPAND)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.Size)
        self.text_name.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)

    def OnOK(self, evt):
        command = []
        for field in ("text_name", "text_accel", "text_cmdline"):
            ctrl = getattr(self, field)
            value = ctrl.Value.strip()
            if not value:
                ctrl.SetFocus()
                dialogs.error(self, "Field is required")
                return
            if ctrl is self.text_accel:
                try:
                    value = parse_accelerator(value)
                except Exception, e:
                    ctrl.SetFocus()
                    dialogs.error(self, "Error: %s" % e)
                    return
            command.append(value)
        self.command = Command(*command)
        evt.Skip()

class CommandsDialog(wx.Dialog):
    def __init__(self, parent):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Configure Commands", style=style)
        
        self.cmdlist = wx.ListBox(self)
        self.cmdlist.SetMinSize((300, 200))
        btn_add = wx.Button(self, label="&Add")
        btn_edit = wx.Button(self, label="&Edit")
        btn_remove = wx.Button(self, label="&Remove")

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(btn_add, 0, wx.EXPAND)
        right_sizer.AddSpacer(5)
        right_sizer.Add(btn_edit, 0, wx.EXPAND)
        right_sizer.AddSpacer(5)
        right_sizer.Add(btn_remove, 0, wx.EXPAND)
        right_sizer.AddStretchSpacer()
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.cmdlist, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(right_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, 5)
        
        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btn_sizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_sizer, 1, wx.EXPAND)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize(self.Size)
        self.cmdlist.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnAdd, btn_add)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, btn_edit)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, btn_remove)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_edit)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_remove)

    def OnAdd(self, evt):
        dlg = EditCommandDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                print dlg.command
                self.cmdlist.Append(dlg.command.name, dlg.command)
        finally:
            dlg.Destroy()

    def OnEdit(self, evt):
        selection = self.cmdlist.GetSelection()
        if selection != wx.NOT_FOUND:
            command = self.cmdlist.GetClientData(selection)
            dlg = EditCommandDialog(self,
                name    = command.name,
                accel   = unparse_accelerator(*command.accel),
                cmdline = command.cmdline)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    print dlg.command
            finally:
                dlg.Destroy()        

    def OnRemove(self, evt):
        selection = self.cmdlist.GetSelection()
        if selection != wx.NOT_FOUND:
            self.cmdlist.Delete(selection)

    def OnUpdateHasSelection(self, ui):
        ui.Enable(self.cmdlist.GetSelection() != wx.NOT_FOUND)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = CommandsDialog(None)
    dlg.ShowModal()
