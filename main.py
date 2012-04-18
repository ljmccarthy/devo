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
        self.mainframe = None

    def OnInit(self):
        return True

    def Startup(self, args):
        try:
            import async_wx, log_file
            async_wx.set_wx_scheduler()

            if hasattr(sys, "frozen"):
                log_filename = os.path.join(tempfile.gettempdir(), "devo-errors.log")
                self.log_file = log_file.get_log_file(log_filename)
                sys.stdout, self.stdout = self.log_file, sys.stdout
                sys.stderr, self.stderr = self.log_file, sys.stderr

            try:
                opts, args = getopt.gnu_getopt(args, "", ["project="])
            except getopt.GetoptError, e:
                sys.stderr.write("devo: error: %s\n" % e)
                return False

            project = None
            for opt, arg in opts:
                if opt == "--project":
                    project = arg

            from mainframe import MainFrame
            self.mainframe = MainFrame(project)
            self.SetTopWindow(self.mainframe)

            for arg in args:
                self.mainframe.OpenEditor(arg)

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
            self.log_file.flush()

def main():
    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()

    if sys.platform == "darwin" and hasattr(sys, "frozen"):
        args = []
    else:
        args = sys.argv[1:]

    app = App()
    if app.Startup(args):
        app.MainLoop()
        app.Shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
