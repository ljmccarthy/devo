import threading
import wx, wx.stc
from editor_fonts import init_stc_style

class ThreadOutputCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, parent, style=wx.TE_READONLY):
        wx.stc.StyledTextCtrl.__init__(self, parent)
        init_stc_style(self)
        self.SetIndent(4)
        self.SetTabWidth(8)
        self.SetUseTabs(False)

        self.__lock = threading.Lock()
        self.__queue = []
        self.__timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.__OnTimer, self.__timer)

    def __OnTimer(self, evt):
        self.flush()

    def flush(self):
        with self.__lock:
            queue, self.__queue = self.__queue, []
        lines = "".join(queue)
        if lines:
            self.AppendText(lines)

    def start(self, interval=100):
        self.__timer.Start(interval)

    def stop(self):
        self.__timer.Stop()
        wx.CallAfter(self.flush)

    def write(self, s):
        with self.__lock:
            self.__queue.append(s)

    def IsEmpty(self):
        return self.GetTextLength() == 0
