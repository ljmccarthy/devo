import sys
import traceback
import threading
import functools
import types

def call_task(future, func, args, kwargs):
    try:
        result = func(*args, **kwargs)
    except:
        exn = sys.exc_info()[1]
        tbstr = traceback.format_exc()
        future.set_failed(exn, tbstr)
    else:
        future.set_done(result)

def async_call_task(future, func, args, kwargs):
    thread = threading.Thread(target=call_task, args=(future, func, args, kwargs))
    thread.daemon = True
    thread.start()

class Scheduler(object):
    def do_call(self):
        raise NotImplementedError()

    def call(self, func, *args, **kwargs):
        self.do_call(func, args, kwargs)

    def async_call(self, func, *args, **kwargs):
        future = Future(self)
        async_call_task(future, func, args, kwargs)
        return future

WAITING, DONE, FAILED, CANCELLED = range(4)

class FutureNotReady(Exception):
    pass

class FutureAlreadySet(Exception):
    pass

class FutureCancelled(Exception):
    pass

class Future(object):
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.__on_success = []
        self.__on_failure = []
        self.__on_cancelled = []
        self.__status = WAITING
        self.__result = None
        self.__traceback = ""
        self.__cond = threading.Condition()

    def __call_handlers(self, handlers, *args):
        for handler in handlers:
            self.scheduler.call(handler, *args)

    def set_done(self, result):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise FutureAlreadySet()
            self.__result = result
            self.__status = DONE
            self.__cond.notify_all()
            self.__call_handlers(self.__on_success, result)

    def set_failed(self, exn, traceback=""):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise FutureAlreadySet()
            self.__result = exn
            self.__traceback = traceback
            self.__status = FAILED
            self.__cond.notify_all()
            self.__call_handlers(self.__on_failure, exn, traceback)

    def wait(self):
        with self.__cond:
            while self.__status == WAITING:
                self.__cond.wait()
            if self.__status == DONE:
                return self.__result
            elif self.__status == FAILED:
                raise self.__result
            elif self.__status == CANCELLED:
                raise FutureCancelled()

    @property
    def ready(self):
        with self.__cond:
            return self.__status != WAITING

    def __check_ready(self):
        if self.__status == WAITING:
            raise FutureNotReady()
        if self.__status == CANCELLED:
            raise FutureCancelled()

    @property
    def failed(self):
        with self.__cond:
            self.__check_ready()
            return self.__status == FAILED

    @property
    def result(self):
        with self.__cond:
            self.__check_ready()
            return self.__result

    def bind(self, success=None, failure=None, cancelled=None):
        with self.__cond:
            if success is not None:
                self.__on_success.append(success)
                if self.__status == DONE:
                    self.scheduler.call(success, self.__result)
            if failure is not None:
                self.__on_failure.append(failure)
                if self.__status == FAILED:
                    self.scheduler.call(failure, self.__result, self.__traceback)
            if cancelled is not None:
                self.__on_cancelled.append(cancelled)
                if self.__status == CANCELLED:
                    self.scheduler.call(cancelled, self)

    def cancel(self):
        with self.__cond:
            if self.__status == WAITING:
                self.__status = CANCELLED
                self.__cond.notify_all()
                self.__call_handlers(self.__on_cancelled, self)

    def __del__(self):
        if self.__status == FAILED and not self.__on_failure:
            print self.__traceback

class Coroutine(Future):
    def __init__(self, scheduler, gen):
        Future.__init__(self, scheduler)
        if not isinstance(gen, types.GeneratorType):
            raise TypeError("Coroutine expected generator, got %s"
                            % gen.__class__.__name__)
        self.__gen = gen
        self.__cont = None
        self.__running = False

    def start(self):
        if not self.__running:
            self.__running = True
            self.__next(self.__gen.next)

    def __next(self, func, *args, **kwargs):
        self.__cont = None
        try:
            ret = func(*args, **kwargs)
        except StopIteration:
            self.set_done(None)
        except Exception, exn:
            self.set_failed(exn, traceback.format_exc())
        else:
            if isinstance(ret, Future):
                self.__cont = ret
                ret.bind(self.__success_next, self.__failure_next, self.__cancelled_next)
            else:
                self.set_done(ret)

    def __success_next(self, result):
        self.__next(self.__gen.send, result)

    def __failure_next(self, exn, traceback):
        self.__next(self.__gen.throw, exn)

    def __cancelled_next(self, future):
        self.cancel()

    def cancel(self):
        Future.cancel(self)
        if self.__cont is not None:
            self.__cont.cancel()
            self.__cont = None

def coroutine(scheduler, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        co = Coroutine(scheduler, func(*args, **kwargs))
        co.start()
        return co
    return wrapper
