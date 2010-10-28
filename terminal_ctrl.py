import wx
import subprocess, threading, Queue

class TerminalCtrl(wx.TextCtrl):
    def __init__(self, parent):
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        wx.TextCtrl.__init__(self, parent, size=(-1, 200), style=style)

        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)

        self.queue = Queue.Queue(1024)
        self.timer = wx.Timer(self)
        self.thread = None

        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def OnTimer(self, evt):
        self.__flush()

    def __flush(self):
        lines = "".join(self.queue.get_nowait() for _ in xrange(self.queue.qsize()))
        self.AppendText(lines)

    def run(self, args, env=None, cwd=None):
        if self.thread:
            return

        process = subprocess.Popen(args,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            close_fds=True, shell=True, cwd=cwd, env=env)
        self.thread = threading.Thread(target=self.__thread, args=(process,))
        self.thread.start()

        self.SetDefaultStyle(wx.TextAttr(colText=wx.BLUE))
        self.AppendText("[Running: %s]\n\n" % args)
        self.SetDefaultStyle(wx.TextAttr())

        self.timer.Start(10)

    def __thread(self, process):
        rc = None
        try:
            for line in process.stdout:
                self.queue.put(line)
            rc = process.wait()
        finally:
            wx.CallAfter(self.__thread_exit, rc)

    def __thread_exit(self, rc):
        self.thread = None
        self.timer.Stop()
        self.__flush()
        if rc is not None:
            self.SetDefaultStyle(wx.TextAttr(colText=wx.BLUE if rc == 0 else wx.RED))
            self.AppendText("\n[Process terminated with return code %d]\n" % rc)
            self.SetDefaultStyle(wx.TextAttr())
