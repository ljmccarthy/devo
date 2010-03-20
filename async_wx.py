import sys, traceback, functools, weakref, wx
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

def async_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return async_call(func, *args, **kwargs)
    return wrapper

def coroutine(func):
    return async.coroutine(scheduler, func)

def queued_coroutine(queue_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            queue = getattr(self, queue_name)
            return queue.run(func, (self,) + args, kwargs)
        return wrapper
    return decorator

def managed(manager_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            manager = getattr(self, manager_name)
            f = func(self, *args, **kwargs)
            manager.add(f)
            return f
        return wrapper
    return decorator

class CoroutineQueue(object):
    def __init__(self):
        self.__running = None
        self.__queue = []

    def run(self, func, args, kwargs):
        co = async.Coroutine(scheduler, func(*args, **kwargs))
        if self.__running is not None:
            self.__queue.append(co)
        else:
            self.__running = weakref.ref(co)
            co.bind(cleanup=self.__next)
            co.start()
        return co

    def __next(self, f):
        if self.__queue:
            co = self.__queue.pop()
            co.bind(cleanup=self.__next)
            co.start()
        else:
            self.__running = None

    def cancel(self):
        self.__queue = []
        if self.__running is not None:
            co = self.__running()
            if co is not None:
                co.cancel()

class CoroutineManager(object):
    def __init__(self):
        self.__futures = set()

    def add(self, future):
        ref = weakref.ref(future)
        self.__futures.add(ref)
        future.bind(cleanup=lambda f: self.__futures.discard(ref))

    def cancel(self):
        for ref in self.__futures:
            future = ref()
            if future is not None:
                future.cancel()
        self.__futures.clear()
