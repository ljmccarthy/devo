#!/usr/bin/env python2

import sys

if sys.platform == "win32":
    import ctypes
    SEM_FAILCRITICALERRORS = 1
    ctypes.windll.kernel32.SetErrorMode(SEM_FAILCRITICALERRORS)
    ctypes.windll.user32.SetProcessDPIAware()

import os, getopt, traceback, warnings

if not hasattr(sys, "frozen"):
    module_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(module_dir)
    sys.path.append(os.path.join(module_dir, "..", "fsmonitor"))
else:
    warnings.filterwarnings("ignore")

import wx
from async import coroutine

class DevoAppHandler(object):
    def __init__(self, app):
        self.app = app

    @coroutine
    def process_args(self, args, cwd):
        try:
            mainframe = self.app.mainframe
            if mainframe.IsIconized():
                mainframe.Iconize(False)
            mainframe.Raise()
            args = DevoArgs(args, cwd)
            if args.project:
                yield mainframe.OpenProject(args.project)
            for filename in args.filenames:
                yield mainframe.OpenEditor(filename)
        except Exception:
            pass
        yield True

class DevoArgs(object):
    def __init__(self, args, cwd):
        self.raw_args = args

        opts, args = getopt.gnu_getopt(args, "", ["project=", "new-instance", "no-fork"])

        self.project = None
        self.new_instance = False
        self.fork = True

        for opt, arg in opts:
            if opt == "--project":
                self.project = arg
            elif opt == "--new-instance":
                self.new_instance = True
            elif opt == "--no-fork":
                self.fork = False

        self.filenames = [os.path.join(cwd, filename) for filename in args]

class DevoApp(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)
        self.SetAppName("Devo")
        self.first_drop = True
        self.mainframe = None
        self.listener = None
        wx.Log_SetActiveTarget(wx.LogStderr())

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
            except OSError as e:
                message = "Failed to create Devo configuration directory:\n\n" + str(e)
                dialogs.error(None, message, "Initialization Error")
                return False

            if not args.new_instance:
                instance = get_app_instance("devo")
                if instance:
                    try:
                        if instance.call("process_args", args.raw_args, os.getcwd()):
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
            self.mainframe = MainFrame.__new__(MainFrame, args)
            self.mainframe.__init__(args)
            self.SetTopWindow(self.mainframe)

            self.Bind(wx.EVT_END_SESSION, self.OnEndSession)

            return True

        except Exception:
            message = "Devo failed to initialize due to the following error:\n\n" + traceback.format_exc()
            if self.mainframe:
                try:
                    self.mainframe.Destroy()
                except Exception:
                    pass
            dialogs.error(None, message, "Initialization Error")
            return False

    def MacOpenFile(self, filename):
        if not self.first_drop or hasattr(sys, "frozen"):
            self.mainframe.OpenEditor(filename)
        self.first_drop = False

    def MacReopenApp(self):
        if self.mainframe.IsIconized():
            self.mainframe.Restore()

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
        args = DevoArgs(args, os.getcwd())
    except getopt.GetoptError as e:
        sys.stderr.write("devo: error: %s\n" % e)
        sys.exit(1)

    if args.fork and sys.platform not in ("win32", "darwin"):
        if os.fork() != 0:
            os._exit(0)

    app = DevoApp()
    if app.Startup(args):
        app.MainLoop()
        app.Shutdown()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
