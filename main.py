#!/usr/bin/env python2

import sys, os, getopt, traceback

if not hasattr(sys, "frozen"):
    module_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(module_dir)
    sys.path.append(os.path.join(module_dir, "..", "fsmonitor"))

import wx
from async import coroutine

class DevoAppHandler(object):
    def __init__(self, app):
        self.app = app

    @coroutine
    def process_args(self, args):
        try:
            self.app.mainframe.Raise()
            args = DevoArgs(args)
            if args.project:
                yield self.app.mainframe.OpenProject(args.project)
            for filename in args.filenames:
                yield self.app.mainframe.OpenEditor(filename)
        except Exception:
            pass
        yield True

class DevoArgs(object):
    def __init__(self, args):
        opts, args = getopt.gnu_getopt(args, "", ["project="])

        project = None
        for opt, arg in opts:
            if opt == "--project":
                project = arg

        self.filenames = args
        self.project = project

class DevoApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.SetAppName("Devo")
        self.first_drop = True
        self.mainframe = None

    def OnInit(self):
        return True

    def Startup(self, args):
        try:
            import async_wx
            from app_instance import AppListener, get_app_instance
            from fileutil import get_user_config_dir
            from log_file import get_log_file

            async_wx.set_wx_scheduler()

            instance = get_app_instance("devo")
            if instance:
                try:
                    if instance.call("process_args", args):
                        return False
                except Exception:
                    pass

            self.listener = AppListener("devo", DevoAppHandler(self))

            if hasattr(sys, "frozen"):
                log_filename = os.path.join(get_user_config_dir("devo"), "errors.log")
                self.log_file = get_log_file(log_filename)
                sys.stdout, self.stdout = self.log_file, sys.stdout
                sys.stderr, self.stderr = self.log_file, sys.stderr

            try:
                args = DevoArgs(args)
            except getopt.GetoptError, e:
                sys.stderr.write("devo: error: %s\n" % e)
                return False

            from mainframe import MainFrame
            self.mainframe = MainFrame(args.project)
            self.SetTopWindow(self.mainframe)

            for filename in args.filenames:
                self.mainframe.OpenEditor(filename)

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
        self.listener.shutdown()
        if hasattr(sys, "frozen"):
            self.log_file.flush()

def main():
    if sys.platform != "win32":
        if os.fork() != 0:
            os._exit(0)

    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()

    if sys.platform == "darwin" and hasattr(sys, "frozen"):
        args = []
    else:
        args = sys.argv[1:]

    app = DevoApp()
    if app.Startup(args):
        app.MainLoop()
        app.Shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
