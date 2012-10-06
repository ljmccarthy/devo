#!/usr/bin/env python2

import sys, os, getopt, traceback

if not hasattr(sys, "frozen"):
    module_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(module_dir)
    sys.path.append(os.path.join(module_dir, "..", "fsmonitor"))

import wx
import wx_patches
from async import coroutine

class DevoAppHandler(object):
    def __init__(self, app):
        self.app = app

    @coroutine
    def process_args(self, cwd, args):
        try:
            mainframe = self.app.mainframe
            if mainframe.IsIconized():
                mainframe.Iconize(False)
            mainframe.Raise()
            args = DevoArgs(args)
            if args.project:
                yield mainframe.OpenProject(args.project)
            for filename in args.filenames:
                yield mainframe.OpenEditor(os.path.join(cwd, filename))
        except Exception:
            pass
        yield True

class DevoArgs(object):
    def __init__(self, args):
        self.raw_args = args

        opts, args = getopt.gnu_getopt(args, "", ["project=", "new-instance"])

        project = None
        new_instance = False
        for opt, arg in opts:
            if opt == "--project":
                project = arg
            elif opt == "--new-instance":
                new_instance = True

        self.filenames = args
        self.project = project
        self.new_instance = new_instance

class DevoApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.SetAppName("Devo")
        self.first_drop = True
        self.mainframe = None
        self.listener = None

    def OnInit(self):
        return True

    def Startup(self, args):
        from dialogs import dialogs
        try:
            import async_wx
            from app_instance import AppListener, get_app_instance
            from fileutil import get_user_config_dir, mkpath
            from log_file import get_log_file

            async_wx.set_wx_scheduler()

            config_dir = get_user_config_dir("devo")
            try:
                mkpath(config_dir)
            except OSError, e:
                message = "Failed to create Devo configuration directory:\n\n" + str(e)
                dialogs.error(None, message, "Initialization Error")
                return False

            if not args.new_instance:
                instance = get_app_instance("devo")
                if instance:
                    try:
                        if instance.call("process_args", os.getcwd(), args.raw_args):
                            return False
                    except Exception:
                        pass

                self.listener = AppListener("devo", DevoAppHandler(self))

            if hasattr(sys, "frozen"):
                log_filename = os.path.join(config_dir, "errors.log")
                self.log_file = get_log_file(log_filename)
                sys.stdout, self.stdout = self.log_file, sys.stdout
                sys.stderr, self.stderr = self.log_file, sys.stderr

            from mainframe import MainFrame
            self.mainframe = MainFrame(args)
            self.SetTopWindow(self.mainframe)

            self.Bind(wx.EVT_END_SESSION, self.OnEndSession)

            return True

        except Exception:
            message = "Devo failed to initialize due to the following error:\n\n" + traceback.format_exc()
            dialogs.error(None, message, "Initialization Error")
            return False

    def MacOpenFile(self, filename):
        if not self.first_drop or hasattr(sys, "frozen"):
            self.mainframe.OpenEditor(filename)
        self.first_drop = False

    def OnEndSession(self, evt):
        if self.mainframe:
            self.mainframe.OnClose(evt)

    def Shutdown(self):
        if self.listener:
            self.listener.shutdown()
        if hasattr(sys, "frozen"):
            self.log_file.flush()

def main():
    if sys.platform == "darwin" and hasattr(sys, "frozen"):
        args = []
    else:
        args = sys.argv[1:]

    try:
        args = DevoArgs(args)
    except getopt.GetoptError, e:
        sys.stderr.write("devo: error: %s\n" % e)
        sys.exit(1)

    if sys.platform not in ("win32", "darwin"):
        if os.fork() != 0:
            os._exit(0)

    if wx.VERSION < (2,9):
        wx.InitAllImageHandlers()

    app = DevoApp()
    if app.Startup(args):
        app.MainLoop()
        app.Shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
