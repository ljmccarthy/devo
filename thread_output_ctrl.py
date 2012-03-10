import Queue
import wx

class ThreadOutputCtrl(wx.TextCtrl):
    def __init__(self, parent):
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        wx.TextCtrl.__init__(self, parent, style=style)

        fontsize = 12 if wx.Platform == "__WXMAC__" else 10
        font = wx.Font(fontsize, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)

        self.queue = Queue.Queue(1024)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def OnTimer(self, evt):
        self.flush()

    def flush(self):
        lines = "".join(self.queue.get_nowait() for _ in xrange(self.queue.qsize()))
        if lines:
            self.AppendText(lines)

    def start(self, interval=100):
        self.timer.Start(interval)

    def stop(self):
        self.timer.Stop()

    def write(self, s):
        self.queue.put(s)
