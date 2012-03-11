import Queue
import wx, wx.stc
from editor_fonts import init_stc_style

class ThreadOutputCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, parent, style=wx.TE_READONLY):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        init_stc_style(self)
        self.SetIndent(4)
        self.SetTabWidth(8)
        self.SetUseTabs(False)

        self.queue = Queue.Queue(1024)
        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.__OnTimer, self.timer)

    def __OnTimer(self, evt):
        self.flush()

    def flush(self):
        lines = "".join(self.queue.get_nowait() for _ in xrange(self.queue.qsize()))
        if lines:
            self.AppendText(lines)

    def start(self, interval=100):
        self.timer.Start(interval)

    def stop(self):
        self.timer.Stop()
        wx.CallAfter(self.flush)

    def write(self, s):
        self.queue.put(s)

    def IsEmpty(self):
        return self.GetTextLength() == 0
