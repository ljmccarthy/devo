#!/usr/bin/env python2

import sys, os, getopt, tempfile, traceback

if not hasattr(sys, "frozen"):
    module_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(module_dir)
    sys.path.append(os.path.join(module_dir, "..", "fsmonitor"))

import wx

class App(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.SetAppName("Devo")
        self.first_drop = True

    def OnInit(self):
        try:
            import async_wx, log_file
            async_wx.set_wx_scheduler()
            if hasattr(sys, "frozen"):
                log_filename = os.path.join(tempfile.gettempdir(), "devo-errors.log")
                self.log_file = log_file.get_log_file(log_filename)
                sys.stdout, self.stdout = self.log_file, sys.stdout
                sys.stderr, self.stderr = self.log_file, sys.stderr
            return True
        except Exception:
            message = "Devo failed to initialize due to the following error:\n\n" + traceback.format_exc()
            dlg = wx.MessageDialog(None, message, "Devo Initialization Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

    def MacOpenFile(self, filename):
        if not self.first_drop or hasattr(sys, "frozen"):
            self.mainframe.OpenEditor(filename)
        self.first_drop = False

    def Shutdown(self):
        if hasattr(sys, "frozen"):
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            f, self.log_file = self.log_file, None
            f.close()

def process_args(args):
    try:
        opts, args = getopt.gnu_getopt(args, "", ["project="])
    except getopt.GetoptError, e:
        sys.stderr.write("devo: error: %s\n" % e)
        sys.exit(1)

    project = None
    for opt, arg in opts:
        if opt == "--project":
            project = arg

    from mainframe import MainFrame
    mainframe = MainFrame(project)

    for arg in args:
        mainframe.OpenEditor(arg)

    return mainframe

def main():
    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()
    app = App()
    mainframe = process_args(sys.argv[1:])
    app.SetTopWindow(mainframe)
    app.MainLoop()
    app.Shutdown()

if __name__ == "__main__":
    main()
