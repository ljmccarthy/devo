import sys
import traceback
import wx
import async

class WxScheduler(async.Scheduler):
    def do_call(self, func, args, kwargs):
        if wx.Thread_IsMain():
            try:
                func(*args, **kwargs)
            except SystemExit:
                raise
            except:
                sys.stdout.write(traceback.format_exc())
        else:
            wx.CallAfter(func, *args, **kwargs)

scheduler = WxScheduler()
async_call = scheduler.async_call

def coroutine(func):
    return async.coroutine(scheduler, func)
