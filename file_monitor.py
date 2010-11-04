import os
import errno
import wx
from contextlib import contextmanager

class FileMonitor(wx.EvtHandler):
    def __init__(self, callback):
        wx.EvtHandler.__init__(self)
        self.callback = callback
        self.path_mtime = {}

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def _update_or_add_path(self, path):
        try:
            self.path_mtime[path] = os.stat(path).st_mtime
        except OSError:
            self.path_mtime[path] = None
            print "Warning:", e

    def add_path(self, path):
        path = os.path.realpath(path)
        if path not in self.path_mtime:
            self._update_or_add_path(path)

    def remove_path(self, path):
        path = os.path.realpath(path)
        if path in self.path_mtime:
            del self.path_mtime[path]

    def update_path(self, path):
        path = os.path.realpath(path)
        if path in self.path_mtime:
            self._update_or_add_path(path)

    @contextmanager
    def updating_path(self, path):
        path = os.path.realpath(path)
        was_running = self.timer.IsRunning()
        if was_running:
            self.stop()
        if path not in self.path_mtime:
            try:
                yield
            finally:
                self.update_path(path)
                if was_running:
                    self.start()
        else:
            try:
                self.remove_path(path)
                yield
            finally:
                self._update_or_add_path(path)
                if was_running:
                    self.start()

    def OnTimer(self, evt):
        updated_paths = []
        deleted_paths = []
        for path, old_mtime in sorted(self.path_mtime.iteritems()):
            try:
                new_mtime = os.stat(path).st_mtime
                if new_mtime != old_mtime:
                    self.path_mtime[path] = new_mtime
                    updated_paths.append(path)
            except OSError, e:
                if e.errno == errno.ENOENT:
                    deleted_paths.append(path)
                else:
                    print "Warning:", e
        for path in deleted_paths:
            del self.path_mtime[path]
        if updated_paths or deleted_paths:
            self.callback(updated_paths, deleted_paths)

    def start(self):
        if not self.timer.IsRunning():
            for path in self.path_mtime:
                self.update_path(path)
            self.timer.Start(200)

    def stop(self):
        self.timer.Stop()
