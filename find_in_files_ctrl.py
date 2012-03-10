import re, time
import wx
from async import async_call
from find_in_files import FindInFiles, make_matcher
from thread_output_ctrl import ThreadOutputCtrl

class FindInFilesCtrl(wx.Panel):
    def __init__(self, parent, env):
        wx.Panel.__init__(self, parent)
        self.env = env
        self.max_line_length = 100
        self.finder = None

        self.output = ThreadOutputCtrl(self)

        self.status_label = wx.StaticText(self)
        button_stop = wx.Button(self, label="&Stop")
        button_clear = wx.Button(self, label="&Clear")
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER)
        top_sizer.Add(button_stop, 0, wx.ALIGN_CENTER)
        top_sizer.AddSpacer(5)
        top_sizer.Add(button_clear, 0, wx.ALIGN_CENTER)
        top_sizer.AddStretchSpacer()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.output, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.OnStop, button_stop)
        self.Bind(wx.EVT_BUTTON, self.OnClear, button_clear)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateStop, button_stop)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateClear, button_clear)

    def OnStop(self, evt):
        if self.finder:
            self.finder.stop()

    def OnUpdateStop(self, evt):
        evt.Enable(bool(self.finder))

    def OnClear(self, evt):
        self.output.SetValue("")

    def OnUpdateClear(self, evt):
        evt.Enable(not self.output.IsEmpty())

    def find(self, details):
        if self.finder:
            self.finder.stop()

        if details.regexp:
            matcher = re.compile(details.find)
        else:
            matcher = make_matcher(details.find)

        self.start_time = time.time()
        self.details = details
        self.finder = FindInFiles(details.path, matcher, self)
        async_call(self.finder.search)
        self.output.SetValue("")
        self.output.start()

    def add_file(self, filepath):
        self.output.write(filepath + "\n")

    def add_line(self, line_num, line):
        if len(line) > self.max_line_length:
            line = line[:self.max_line_length] + "..."
        self.output.write("  %d: %s\n" % (line_num, line))

    def end_file(self):
        self.output.write("\n")

    def finish(self, message):
        completed_time = time.time() - self.start_time
        self.output.write(message % (self.details.find, self.details.path, completed_time))
        self.output.stop()
        self.details = None
        self.finder = None

    def end_find(self):
        self.finish("Search for '%s' in %s completed in %.2f seconds")

    def abort_find(self):
        self.finish("Search for '%s' in %s aborted after %.2f seconds")
