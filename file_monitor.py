import os
import wx

class FileMonitor(wx.EvtHandler):
    def __init__(self, callback):
        wx.EvtHandler.__init__(self)
        self.callback = callback
        self.path_mtime = {}

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Start()

    def AddPath(self, path):
        path = os.path.realpath(path)
        if path not in self.path_mtime:
            try:
                self.path_mtime[path] = os.stat(path).st_mtime
            except OSError, e:
                self.path_mtime[path] = None
                print "Warning:", e

    def RemovePath(self, path):
        if path in self.path_mtime:
            del self.path_mtime[path]

    def OnTimer(self, evt):
        updated_paths = []
        for path, old_mtime in sorted(self.path_mtime.iteritems()):
            try:
                new_mtime = os.stat(path).st_mtime
                if new_mtime != old_mtime:
                    self.path_mtime[path] = new_mtime
                    updated_paths.append(path)
            except OSError, e:
                print "Warning:", e
        if updated_paths:
            self.callback(updated_paths)

    def Start(self):
        if not self.timer.IsRunning():
            self.timer.Start(200)

    def Stop(self):
        self.timer.Stop()
