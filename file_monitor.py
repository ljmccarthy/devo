import os
import errno
import wx
from contextlib import contextmanager
from util import get_top_level_focus

class FileMonitor(wx.EvtHandler):
    def __init__(self, callback, top_level_focus=None):
        wx.EvtHandler.__init__(self)
        self.callback = callback
        self.top_level_focus = top_level_focus
        self.path_mtime = {}
        self.running_refcount = 0

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    def _update_or_add_path(self, path):
        try:
            self.path_mtime[path] = os.stat(path).st_mtime
        except OSError:
            self.path_mtime[path] = None

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
        self.stop()
        if path not in self.path_mtime:
            try:
                yield
            finally:
                self.update_path(path)
                self.start()
        else:
            try:
                self.remove_path(path)
                yield
            finally:
                self._update_or_add_path(path)
                self.start()

    def OnTimer(self, evt):
        if self.top_level_focus:
            if get_top_level_focus() is not self.top_level_focus:
                return

        updated_paths = []
        deleted_paths = []
        for path, old_mtime in sorted(self.path_mtime.iteritems()):
            try:
                new_mtime = os.stat(path).st_mtime
                if new_mtime != old_mtime:
                    self.path_mtime[path] = new_mtime
                    updated_paths.append(path)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    deleted_paths.append(path)
        for path in deleted_paths:
            del self.path_mtime[path]
        if updated_paths or deleted_paths:
            self.callback(updated_paths, deleted_paths)

    @property
    def is_running(self):
        return self.running_refcount > 0

    def start(self, update_paths=True):
        if self.running_refcount <= 0:
            if update_paths:
                for path in self.path_mtime:
                    self.update_path(path)
            self.timer.Start(200)
            self.running_refcount += 1

    def stop(self):
        if self.running_refcount > 0:
            self.timer.Stop()
            self.running_refcount -= 1

    @contextmanager
    def stopped_context(self):
        self.stop()
        try:
            yield
        finally:
            self.start(update_paths=False)
