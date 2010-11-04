import string
import wx
from accelerator import parse_accelerator, unparse_accelerator
from dialogs import dialogs

command_help = """\
Accelerator keys may use modifers, for example:

    Alt+Shift+X
    Ctrl+F10

Commands may use the following environment variables:

    $CURRENT_FILE - Current file
    $CURRENT_DIR - Directory of current file
    $CURRENT_BASENAME - Base filename of current file
    $PROJECT_ROOT - Project root directory\
"""

def check_variables(s):
    try:
        string.Template(s).substitute(
            CURRENT_FILE="", CURRENT_DIR="", CURRENT_BASENAME="", PROJECT_ROOT="")
    except KeyError, e:
        raise Exception("Unknown variable name: %s" % e.args)
    except ValueError, e:
        raise Exception("Variable name missing after $")

class EditCommandDialog(wx.Dialog):
    def __init__(self, parent, command={}, title="Edit Command"):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title=title, style=style)

        self.field_name = wx.TextCtrl(self, value=command.get("name", ""))
        self.field_accel = wx.TextCtrl(self, value=command.get("accel", ""))
        self.field_cmdline = wx.TextCtrl(self, value=command.get("cmdline", ""))
        self.field_workdir = wx.TextCtrl(self, value=command.get("workdir", ""))
        self.field_before = wx.Choice(self,
            choices=["Do Nothing", "Save Current File", "Save All Files"])
        self.field_before.SetStringSelection(command.get("before", ""))

        grid = wx.FlexGridSizer(2, 2, 5, 5)
        grid.AddGrowableCol(1, 1)
        grid.Add(wx.StaticText(self, label="Name in Menu"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_name, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Accelerator Key"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_accel, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Shell Command"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_cmdline, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Working Directory"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_workdir, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Before Executing"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_before, 0, wx.EXPAND)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        btn_sizer.AddButton(wx.Button(self, wx.ID_HELP))
        btn_sizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize((max(self.Size.width, 400), self.Size.height))
        self.SetMaxSize(wx.Size(-1, self.Size.height))
        self.field_name.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, id=wx.ID_HELP)

    def _GetField(self, ctrl):
        value = ctrl.Value.strip()
        if not value:
            raise Exception("Field is required")
        return value

    def _GetAccel(self, ctrl):
        value = ctrl.Value.strip()
        return value and unparse_accelerator(*parse_accelerator(value))

    def _GetCmdline(self, ctrl):
        value = self._GetField(ctrl)
        check_variables(value)
        return value

    def _GetWorkDir(self, ctrl):
        value = ctrl.Value.strip()
        check_variables(value)
        return value

    def _GetStringSelection(self, ctrl):
        return ctrl.GetStringSelection()

    _fields = (
        ("name", _GetField),
        ("accel", _GetAccel),
        ("cmdline", _GetCmdline),
        ("workdir", _GetWorkDir),
        ("before", _GetStringSelection),
    )

    def OnOK(self, evt):
        command = {}
        for field_name, getter_method in self._fields:
            ctrl = getattr(self, "field_" + field_name)
            try:
                value = getter_method(self, ctrl)
            except Exception, e:
                ctrl.SetFocus()
                dialogs.error(self, "Error: %s" % e)
                return
            command[field_name] = value
        self.command = command
        evt.Skip()

    def OnHelp(self, evt):
        dialogs.info(self, command_help, "Edit Command Help")

class CommandsDialog(wx.Dialog):
    def __init__(self, parent, commands=[]):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title="Configure Commands", style=style)
        
        self.cmdlist = wx.ListBox(self)
        self.cmdlist.SetMinSize((300, 200))
        btn_add = wx.Button(self, label="&Add")
        btn_edit = wx.Button(self, label="&Edit")
        btn_remove = wx.Button(self, label="&Remove")
        btn_move_up = wx.Button(self, label="Move &Up")
        btn_move_down = wx.Button(self, label="Move &Down")

        for command in commands:
            self.cmdlist.Append(command["name"], command)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(btn_add, 0, wx.EXPAND)
        right_sizer.AddSpacer(5)
        right_sizer.Add(btn_edit, 0, wx.EXPAND)
        right_sizer.AddSpacer(5)
        right_sizer.Add(btn_remove, 0, wx.EXPAND)
        right_sizer.AddSpacer(15)
        right_sizer.Add(btn_move_up, 0, wx.EXPAND)
        right_sizer.AddSpacer(5)
        right_sizer.Add(btn_move_down, 0, wx.EXPAND)
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
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, btn_move_up)
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, btn_move_down)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_edit)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_remove)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_move_up)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_move_down)

    def _GetCommand(self, i):
        return self.cmdlist.GetClientData(i)

    def _SetCommand(self, i, command):
        self.cmdlist.SetString(i, command["name"])
        self.cmdlist.SetClientData(i, command)

    def _SwapCommands(self, a, b):
        command_a = self._GetCommand(a)
        command_b = self._GetCommand(b)
        self._SetCommand(a, command_b)
        self._SetCommand(b, command_a)

    def OnAdd(self, evt):
        dlg = EditCommandDialog(self, title="Add Command")
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.cmdlist.Append(dlg.command["name"], dlg.command)
        finally:
            dlg.Destroy()

    def OnEdit(self, evt):
        selection = self.cmdlist.GetSelection()
        if selection != wx.NOT_FOUND:
            command = self._GetCommand(selection)
            dlg = EditCommandDialog(self, command=command)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self._SetCommand(selection, dlg.command)
            finally:
                dlg.Destroy()        

    def OnRemove(self, evt):
        selection = self.cmdlist.GetSelection()
        if selection != wx.NOT_FOUND:
            self.cmdlist.Delete(selection)

    def OnMoveUp(self, evt):
        selection = self.cmdlist.GetSelection()
        if 0 < selection < self.cmdlist.GetCount():
            self._SwapCommands(selection, selection - 1)
            self.cmdlist.SetSelection(selection - 1)

    def OnMoveDown(self, evt):
        selection = self.cmdlist.GetSelection()
        if 0 <= selection < self.cmdlist.GetCount() - 1:
            self._SwapCommands(selection, selection + 1)
            self.cmdlist.SetSelection(selection + 1)

    def OnUpdateHasSelection(self, ui):
        ui.Enable(self.cmdlist.GetSelection() != wx.NOT_FOUND)

    def GetCommands(self):
        return [self.cmdlist.GetClientData(i) for i in xrange(self.cmdlist.GetCount())]

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dlg = CommandsDialog(None)
    dlg.ShowModal()
