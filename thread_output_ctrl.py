import threading
import wx
from editor_fonts import init_stc_style
from styled_text_ctrl import StyledTextCtrl

class ThreadOutputCtrl(StyledTextCtrl):
    def __init__(self, parent, env, auto_scroll=False):
        StyledTextCtrl.__init__(self, parent, env)
        init_stc_style(self)
        self.SetIndent(4)
        self.SetTabWidth(8)
        self.SetUseTabs(False)

        self.auto_scroll = auto_scroll

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
            with self.ModifyReadOnly():
                self.AppendText(lines)
                self.EmptyUndoBuffer()
            if self.auto_scroll:
                self.ScrollToLine(self.GetLineCount() - 1)

    def start(self, interval=100):
        self.SetReadOnly(True)
        self.__timer.Start(interval)

    def stop(self):
        self.__timer.Stop()
        self.flush()
        self.SetReadOnly(False)

    def write(self, s):
        with self.__lock:
            self.__queue.append(s)

    def ClearAll(self):
        with self.ModifyReadOnly():
            StyledTextCtrl.ClearAll(self)
