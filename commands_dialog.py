import string
import wx

from accelerator import parse_accelerator, unparse_accelerator
from dialogs import dialogs
from file_picker import DirPicker
from html_frame import HtmlPopup
from settings import read_settings, write_settings

command_help = """\
<b>Edit Command Help</b>
<p>Example accelerator keys:</p>
<ul>
    <li>Alt+Shift+X</li>
    <li>Ctrl+F10</li>
</ul>
<p>
Commands may use the following special variables:
</p>
<table>
    <tr><td><code>$FILEPATH</code></td><td>Current file name (full path).</td></tr>
    <tr><td><code>$DIRNAME</code></td><td>Directory of current file.</td></tr>
    <tr><td><code>$BASENAME</code></td><td>Base filename of current file.</td></tr>
    <tr><td><code>$PROJECT_DIR</code></td><td>Project directory.</td></tr>
    <tr><td><code>$SELECTION</code></td><td>Currently selected text.</td></tr>
    <tr><td><code>$SELECTION_LINE</code></td><td>Currently selected text (first line).</td></tr>
    <tr><td><code>$DEVO_CONFIG_DIR</code></td><td>Devo configuration directory.</td></tr>
</table>
<p>To send multi-line selections to the input of one particular command (Unix shells only):</p>
<pre>
  cat &lt;&lt;EOF
  $SELECTION
  EOF
</pre>
"""

commands_ext = ".json"
commands_wildcard = "Devo Commands|*%s" % commands_ext

def check_variables(s):
    try:
        string.Template(s).substitute()
    except KeyError as e:
        pass
    except ValueError as e:
        raise Exception("Variable name missing after $")

save_options = [
    ("Do Not Save", "do_not_save"),
    ("Save Current File", "save_current_file"),
    ("Save All Files", "save_all_files"),
]

stdin_options = [
    ("No Input", "none"),
    ("Current Selection", "current_selection"),
    ("Current Selection (Lines)", "current_selection_lines"),
    ("Current File", "current_file"),
]

stdout_options = [
    ("Show In Terminal", "show_in_terminal"),
    ("Replace Current Selection", "replace_selection"),
    ("Send To New Editor", "new_editor"),
]

save_option_indices = {x[1]: i for i, x in enumerate(save_options)}
stdin_option_indices = {x[1]: i for i, x in enumerate(stdin_options)}
stdout_option_indices = {x[1]: i for i, x in enumerate(stdout_options)}

def get_value(ctrl):
    return ctrl.Value

def get_non_empty_string(ctrl):
    value = ctrl.Value.strip()
    if not value:
        raise Exception("Field is required.")
    return value

def get_accel(ctrl):
    value = ctrl.Value.strip()
    return value and unparse_accelerator(*parse_accelerator(value))

def get_workdir(ctrl):
    value = ctrl.Value.strip()
    check_variables(value)
    return value

def get_string_selection(ctrl):
    return ctrl.GetStringSelection()

def get_choice_option(options):
    def getter(ctrl):
        return options[ctrl.Selection][1]
    return getter

class EditCommandDialog(wx.Dialog):
    def __init__(self, parent, command={}, title="Edit Command"):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title=title, style=style)

        self.command = command.copy()
        self.help_frame = None

        self.field_name = wx.TextCtrl(self, value=command.get("name", ""))
        self.field_accel = wx.TextCtrl(self, value=command.get("accel", ""))
        self.field_cmdline = wx.TextCtrl(self,
            value=command.get("cmdline", ""), style = wx.TE_MULTILINE, size=(-1, 80))
        self.field_workdir = DirPicker(self, value=command.get("workdir", ""))

        self.field_stdin = wx.Choice(self, choices=list(x[0] for x in stdin_options))
        self.field_stdin.SetSelection(stdin_option_indices.get(command.get("stdin", ""), 0))

        self.field_stdout = wx.Choice(self, choices=list(x[0] for x in stdout_options))
        self.field_stdout.SetSelection(stdout_option_indices.get(command.get("stdout", ""), 0))

        self.field_save = wx.Choice(self, choices=list(x[0] for x in save_options))
        self.field_before = self.field_save
        if "save" in command:
            self.field_save.SetSelection(save_option_indices.get(command.get("save", ""), 0))
        else:
            # Backwards compatibility
            if not self.field_save.SetStringSelection(command.get("before", "")):
                self.field_save.SetSelection(0)

        self.field_detach = wx.CheckBox(self, label="Detach Process")
        self.field_detach.SetValue(command.get("detach", False))

        self.field_killable = wx.CheckBox(self, label="Killable Process")
        self.field_killable.SetValue(command.get("killable", True))

        grid = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        grid.AddGrowableCol(1, 1)
        grid.AddGrowableRow(2, 1)
        grid.Add(wx.StaticText(self, label="Name in Menu"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_name, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Accelerator Key"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_accel, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Shell Commands"), 1, wx.TOP | wx.EXPAND, 5)
        grid.Add(self.field_cmdline, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Working Directory"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_workdir, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Standard Input"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_stdin, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Standard Output"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_stdout, 0, wx.EXPAND)
        grid.Add(wx.StaticText(self, label="Before Executing"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.field_save, 0, wx.EXPAND)
        grid.AddSpacer(0)
        flag_sizer = wx.BoxSizer(wx.VERTICAL)
        flag_sizer.Add(self.field_detach, 1, wx.EXPAND)
        flag_sizer.AddSpacer(5)
        flag_sizer.Add(self.field_killable, 1, wx.EXPAND)
        grid.Add(flag_sizer, 0, wx.EXPAND)

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

        size = (max(500, self.Size.width), self.Size.height)
        self.SetSize(size)
        self.SetMinSize(size)
        self.Centre()

        self.field_name.SetFocus()

        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_DisableWhenDetached, self.field_killable)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_DisableWhenDetached, self.field_stdin)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI_DisableWhenDetached, self.field_stdout)
        self.Bind(wx.EVT_MOVE, self.OnMove)

    _fields = (
        ("name", get_non_empty_string),
        ("accel", get_accel),
        ("cmdline", get_non_empty_string),
        ("workdir", get_workdir),
        ("stdin", get_choice_option(stdin_options)),
        ("stdout", get_choice_option(stdout_options)),
        ("before", get_string_selection),  # Backwards compatibility
        ("save", get_choice_option(save_options)),
        ("detach", get_value),
        ("killable", get_value),
    )

    def OnOK(self, evt):
        for field_name, getter_func in self._fields:
            ctrl = getattr(self, "field_" + field_name)
            try:
                value = getter_func(ctrl)
            except Exception as e:
                ctrl.SetFocus()
                dialogs.error(self, "Error: %s" % e)
                return
            self.command[field_name] = value
        evt.Skip()

    def OnHelp(self, evt):
        if not self.help_frame:
            pos = (self.Position.x - 420, self.Position.y)
            size = (400, 420)
            self.help_frame = HtmlPopup(self, command_help, pos=pos, size=size)
        self.help_frame.Show(not self.help_frame.IsShown())

    def OnMove(self, evt):
        if self.help_frame:
            self.help_frame.SetPosition((self.Position.x - 420, self.Position.y))

    def OnUpdateUI_DisableWhenDetached(self, evt):
        evt.Enable(not self.field_detach.Value)

def clean_commands(commands):
    commands = [command.copy() for command in commands]
    before_dict = dict(save_options)
    for command in commands:
        if "before" in command:
            if "save" not in command:
                command["save"] = before_dict.get(command["before"], "do_not_save")
            del command["before"]
    return commands

class CommandsDialog(wx.Dialog):
    def __init__(self, parent, commands=[], title="Configure Commands"):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, title=title, style=style)
        
        self.cmdlist = wx.ListBox(self)
        self.cmdlist.SetMinSize((300, 200))
        btn_add = wx.Button(self, label="&Add")
        btn_edit = wx.Button(self, label="&Edit")
        btn_remove = wx.Button(self, label="&Remove")
        btn_move_up = wx.Button(self, label="Move &Up")
        btn_move_down = wx.Button(self, label="Move &Down")
        btn_import = wx.Button(self, label="&Import...")
        btn_export = wx.Button(self, label="E&xport...")

        for command in commands:
            self.cmdlist.Append(command["name"], command)

        spacer = 10 if wx.Platform == "__WXMAC__" else 5
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(btn_add, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer)
        right_sizer.Add(btn_edit, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer)
        right_sizer.Add(btn_remove, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer * 3)
        right_sizer.Add(btn_move_up, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer)
        right_sizer.Add(btn_move_down, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer * 3)
        right_sizer.Add(btn_import, 0, wx.EXPAND)
        right_sizer.AddSpacer(spacer)
        right_sizer.Add(btn_export, 0, wx.EXPAND)
        right_sizer.AddStretchSpacer()
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.cmdlist, 1, wx.EXPAND | wx.ALL, spacer)
        main_sizer.Add(right_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, spacer)
        
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
        self.Centre()
        self.SetMinSize(self.Size)
        self.cmdlist.SetFocus()

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnEdit)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, btn_add)
        self.Bind(wx.EVT_BUTTON, self.OnEdit, btn_edit)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, btn_remove)
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, btn_move_up)
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, btn_move_down)
        self.Bind(wx.EVT_BUTTON, self.OnImport, btn_import)
        self.Bind(wx.EVT_BUTTON, self.OnExport, btn_export)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_edit)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_remove)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_move_up)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasSelection, btn_move_down)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateHasAnyCommands, btn_export)

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
            if selection >= self.cmdlist.Count:
                selection = selection - 1
            if selection < self.cmdlist.Count:
                self.cmdlist.SetSelection(selection)

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

    def OnImport(self, evt):
        path = dialogs.get_file_to_open(self, wildcard=commands_wildcard, context="commands")
        if path:
            try:
                commands = read_settings(path)
                if isinstance(commands, dict):
                    commands = commands.get("commands", [])
                if isinstance(commands, list):
                    for command in commands:
                        if isinstance(command, dict) and "name" in command:
                            self.cmdlist.Append(command["name"], command)
            except Exception as e:
                dialogs.error(self, "Error importing commands file: %s" % e)

    def OnExport(self, evt):
        path = dialogs.get_file_to_save(self, wildcard=commands_wildcard, context="commands")
        if path:
            if not path.endswith(commands_ext) and "." not in path:
                path = path + commands_ext
            try:
                commands = clean_commands(self.GetCommands())
                write_settings(path, commands)
            except Exception as e:
                dialogs.error(self, "Error exporting commands file: %s" % e)

    def OnUpdateHasSelection(self, evt):
        evt.Enable(self.cmdlist.GetSelection() != wx.NOT_FOUND)

    def OnUpdateHasAnyCommands(self, evt):
        evt.Enable(self.cmdlist.Count > 0)

    def GetCommands(self):
        return [self.cmdlist.GetClientData(i) for i in xrange(self.cmdlist.GetCount())]

if __name__ == "__main__":
    app = wx.App()
    dlg = CommandsDialog(None)
    if dlg.ShowModal() == wx.ID_OK:
        print dlg.GetCommands()
