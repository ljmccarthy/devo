import traceback
import wx
from async import *

class WxScheduler(Scheduler):
    def do_call(self, func, args, kwargs):
        if wx.Thread_IsMain():
            try:
                func(*args, **kwargs)
            except SystemExit:
                raise
            except:
                print traceback.format_exc()
        else:
            wx.CallAfter(func, *args, **kwargs)

class WxScheduled(object):
    scheduler = WxScheduler()

    def async_call(self, func, *args, **kwargs):
        return self.scheduler.async_call(func, *args, **kwargs)
