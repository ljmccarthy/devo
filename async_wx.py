import sys, traceback, wx
import async

class WxScheduler(async.Scheduler):
    def call(self, func, *args, **kwargs):
        if wx.Thread_IsMain():
            try:
                func(*args, **kwargs)
            except SystemExit:
                raise
            except:
                sys.stdout.write(traceback.format_exc())
        else:
            wx.CallAfter(func, *args, **kwargs)

    def post_call(self, func, *args, **kwargs):
        wx.CallAfter(func, *args, **kwargs)

def set_wx_scheduler():
    async.set_scheduler(WxScheduler())
