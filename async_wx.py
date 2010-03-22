import sys, traceback, functools, wx

import async
from async import CoroutineManager, CoroutineQueue, managed, queued_coroutine

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

def async_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return async_call(func, *args, **kwargs)
    return wrapper

def coroutine(func):
    return async.coroutine(scheduler, func)

def CoroutineQueue():
    return async.CoroutineQueue(scheduler)
