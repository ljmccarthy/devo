import wx
import sys, subprocess, threading, Queue

class TerminalCtrl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.queue = Queue.Queue(1024)
        self.thread = None
        self.process = None
        self.timer = wx.Timer(self)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.text = wx.TextCtrl(self, style=style)
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text.SetFont(font)

        self.status_label = wx.StaticText(self)
        button_clear = wx.Button(self, label="Clear")
        button_stop = wx.Button(self, label="Stop")

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER)
        top_sizer.AddStretchSpacer()
        top_sizer.Add(button_clear, 0, wx.ALIGN_CENTER)
        top_sizer.AddSpacer(5)
        top_sizer.Add(button_stop, 0, wx.ALIGN_CENTER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.text, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnClear, button_clear)
        self.Bind(wx.EVT_BUTTON, self.OnStop, button_stop)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateClear, button_clear)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateStop, button_stop)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def OnClear(self, evt):
        self.text.SetValue("")

    def OnUpdateClear(self, evt):
        evt.Enable(not self.text.IsEmpty())

    def OnStop(self, evt):
        self.stop()

    def OnUpdateStop(self, evt):
        evt.Enable(self.process is not None)

    def OnTimer(self, evt):
        self.__flush()

    def __flush(self):
        lines = "".join(self.queue.get_nowait() for _ in xrange(self.queue.qsize()))
        if lines:
            self.text.AppendText(lines)

    def run(self, args, env=None, cwd=None):
        if self.process:
            return

        self.process = subprocess.Popen(args,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            close_fds=(sys.platform != "win32"), shell=True, cwd=cwd, env=env)
        self.thread = threading.Thread(target=self.__thread, args=(self.process,))
        self.thread.start()

        self.process_args = args
        self.status_label.SetLabel("%s\nRunning" % args)
        self.text.SetValue("")

        self.timer.Start(10)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

    def __thread(self, process):
        rc = None
        try:
            while True:
                rc = process.poll()
                if rc is not None:
                    break
                line = process.stdout.readline()
                if not line:
                    break
                self.queue.put(line)
            rc = process.wait()
        finally:
            wx.CallAfter(self.__thread_exit, process, rc)

    def __thread_exit(self, process, rc):
        self.__flush()
        self.status_label.SetLabel(
            "%s\nProcess terminated%s" % (self.process_args,
                " with return code %d" % rc if rc is not None else ""))
        if self.process is process:
            self.thread = None
            self.process = None
            self.timer.Stop()
