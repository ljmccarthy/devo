import wx
import threading
from dialogs import dialogs
from shell import run_shell_command, kill_shell_process
from thread_output_ctrl import ThreadOutputCtrl

class TerminalCtrl(wx.Panel):
    def __init__(self, parent, env):
        wx.Panel.__init__(self, parent)
        self.env = env

        self.thread = None
        self.process = None
        self.output = ThreadOutputCtrl(self)

        self.status_label = wx.StaticText(self)
        button_kill = wx.Button(self, label="Kill", size=(120, 25))
        button_stop = wx.Button(self, label="Stop", size=(120, 25))
        button_copy = wx.Button(self, label="Copy to Editor", size=(120, 25))
        button_clear = wx.Button(self, label="Clear", size=(120, 25))

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER)
        top_sizer.AddStretchSpacer()
        top_sizer.Add(button_kill, 0, wx.ALIGN_CENTER)
        top_sizer.AddSpacer(5)
        top_sizer.Add(button_stop, 0, wx.ALIGN_CENTER)
        top_sizer.AddSpacer(5)
        top_sizer.Add(button_copy, 0, wx.ALIGN_CENTER)
        top_sizer.AddSpacer(5)
        top_sizer.Add(button_clear, 0, wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.output, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnKill, button_kill)
        self.Bind(wx.EVT_BUTTON, self.OnStop, button_stop)
        self.Bind(wx.EVT_BUTTON, self.OnCopyToEditor, button_copy)
        self.Bind(wx.EVT_BUTTON, self.OnClear, button_clear)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateStop, button_kill)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateStop, button_stop)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateClear, button_copy)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateClear, button_clear)

    def CanUndo(self):
        return self.output.CanUndo()

    def CanRedo(self):
        return self.output.CanRedo()

    def CanCut(self):
        return not self.output.GetReadOnly() and self.CanCopy()

    def CanCopy(self):
        start, end = self.output.GetSelection()
        return start != end

    def CanPaste(self):
        return self.output.CanPaste()

    def Undo(self):
        self.output.Undo()

    def Redo(self):
        self.output.Redo()

    def Cut(self):
        self.output.Cut()

    def Copy(self):
        self.output.Copy()

    def Paste(self):
        self.output.Paste()

    def SelectAll(self):
        self.output.SelectAll()

    def OnCopyToEditor(self, evt):
        self.env.open_text(self.output.GetText())

    def OnClear(self, evt):
        self.output.ClearAll()

    def OnUpdateClear(self, evt):
        evt.Enable(not self.output.IsEmpty())

    def OnStop(self, evt):
        self.stop()

    def OnKill(self, evt):
        if dialogs.ask_kill_process(self):
            self.kill()

    def OnUpdateStop(self, evt):
        evt.Enable(self.process is not None)

    @property
    def is_running(self):
        return bool(self.process)

    def run(self, cmdline, env=None, cwd=None):
        if self.process:
            return

        self.process = run_shell_command(cmdline, env=env, cwd=cwd)
        self.thread = threading.Thread(target=self.__thread, args=(self.process,))
        self.thread.start()

        self.cmdline = cmdline
        self.status_label.SetLabel(cmdline + "\nRunning")
        self.output.ClearAll()
        self.output.start()

    def stop(self):
        if self.process:
            kill_shell_process(self.process)
            self.process = None

    def kill(self):
        if self.process:
            kill_shell_process(self.process, force=True)
            self.process = None

    def __thread(self, process):
        rc = None
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.output.write(line.decode("utf-8", "replace"))
            rc = process.wait()
        finally:
            wx.CallAfter(self.__thread_exit, process, rc)

    def __thread_exit(self, process, rc):
        self.output.flush()
        self.status_label.SetLabel(
            "%s\nProcess terminated%s" % (self.cmdline,
                " with return code %d" % rc if rc is not None else ""))
        if self.process is process:
            self.thread = None
            self.process = None
            self.output.stop()
