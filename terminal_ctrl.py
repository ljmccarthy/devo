import re, threading
import wx

from dialogs import dialogs
from shell import run_shell_command, kill_shell_process
from styled_text_ctrl import MARKER_ERROR
from thread_output_ctrl import ThreadOutputCtrl
from util import get_text_extent, shorten_text

file_line_patterns = [
    re.compile(ur"^\s*File \"(?P<file>.*)\", line (?P<line>\d+)", re.UNICODE),
]

class TerminalCtrl(wx.Panel):
    def __init__(self, parent, env):
        wx.Panel.__init__(self, parent)
        self.env = env

        self.thread = None
        self.process = None
        self.output = ThreadOutputCtrl(self, env, auto_scroll=True)

        text_width, text_height = get_text_extent(self.GetFont(), "Copy to Editor")
        button_size = (text_width + 30, text_height + 10)

        self.status_label = wx.StaticText(self)
        button_kill = wx.Button(self, label="&Kill", size=button_size)
        button_stop = wx.Button(self, label="&Stop", size=button_size)
        button_copy = wx.Button(self, label="&Copy to Editor", size=button_size)
        button_clear = wx.Button(self, label="C&lear", size=button_size)

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
        self.output.Bind(wx.EVT_LEFT_DCLICK, self.OnLineDoubleClicked)

    def OnCopyToEditor(self, evt):
        self.env.open_text(self.output.GetText())

    def Clear(self):
        self.output.ClearAll()
        self.env.clear_highlight(MARKER_ERROR)

    def OnClear(self, evt):
        self.Clear()

    def OnUpdateClear(self, evt):
        evt.Enable(not self.output.IsEmpty())

    def OnStop(self, evt):
        self.stop()

    def OnKill(self, evt):
        if dialogs.ask_kill_process(self):
            self.kill()

    def OnUpdateStop(self, evt):
        evt.Enable(self.process is not None)

    def OpenFileOnLine(self, output_line, highlight_line):
        s = self.output.GetLine(output_line)
        for pattern in file_line_patterns:
            m = pattern.match(s)
            if m:
                path = m.group("file")
                line = int(m.group("line"))
                self.env.open_file(path, line, MARKER_ERROR)
                self.output.SetHighlightedLine(highlight_line, MARKER_ERROR)
                return True
        return False

    def OnLineDoubleClicked(self, evt):
        output_line = self.output.GetCurrentLine()
        if self.OpenFileOnLine(output_line, output_line):
            return
        if self.OpenFileOnLine(output_line - 1, output_line):
            return
        evt.Skip()

    def set_status(self, status):
        self.status_label.SetLabel(status.replace("&", "&&"))
        self.Layout()

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
        self.set_status(shorten_text(cmdline, 60) + "\nRunning (pid %d)" % self.process.pid)
        self.Clear()
        self.output.start()

    def stop(self):
        if self.process:
            kill_shell_process(self.process)

    def kill(self):
        if self.process:
            kill_shell_process(self.process, force=True)

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
        self.set_status("%s\nProcess terminated%s" % (
            shorten_text(self.cmdline, 60),
            " with return code %d" % rc if rc is not None else ""))
        if self.process is process:
            self.thread = None
            self.process = None
            self.output.stop()
