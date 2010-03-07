import sys
import traceback
import threading
import functools
import types

def call_task(task, func, args, kwargs):
    try:
        result = func(*args, **kwargs)
    except:
        exn = sys.exc_info()[1]
        tbstr = traceback.format_exc()
        task.set_failed(exn, tbstr)
    else:
        task.set_done(result)

def async_call_task(task, func, args, kwargs):
    thread = threading.Thread(target=call_task, args=(task, func, args, kwargs))
    thread.daemon = True
    thread.start()

class Scheduler(object):
    def do_call(self):
        raise NotImplementedError()

    def call(self, func, *args, **kwargs):
        self.do_call(func, args, kwargs)

    def async_call(self, func, *args, **kwargs):
        task = Task(self)
        async_call_task(task, func, args, kwargs)
        return task

WAITING, DONE, FAILED, CANCELLED = range(4)

class TaskNotReady(Exception):
    pass

class TaskAlreadySet(Exception):
    pass

class TaskCancelled(Exception):
    pass

class Task(object):
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.__on_success = []
        self.__on_failure = []
        self.__on_cleanup = []
        self.__status = WAITING
        self.__result = None
        self.__traceback = ""
        self.__cond = threading.Condition()

    def set_done(self, result):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise TaskAlreadySet()
            self.__result = result
            self.__status = DONE
            self.__cond.notify_all()
            for handler in self.__on_success:
                self.scheduler.call(handler, result)

    def set_failed(self, exn, traceback=""):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise TaskAlreadySet()
            self.__result = exn
            self.__traceback = traceback
            self.__status = FAILED
            self.__cond.notify_all()
            for handler in self.__on_failure:
                self.scheduler.call(handler, exn, traceback)

    def wait(self):
        with self.__cond:
            while self.__status == WAITING:
                self.__cond.wait()
            if self.__status == DONE:
                return self.__result
            elif self.__status == FAILED:
                raise self.__result
            elif self.__status == CANCELLED:
                raise TaskCancelled()

    @property
    def ready(self):
        with self.__cond:
            return self.__status != WAITING

    def __check_ready(self):
        if self.__status == WAITING:
            raise TaskNotReady()
        if self.__status == CANCELLED:
            raise TaskCancelled()

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

    def bind(self, success=None, failure=None, cleanup=None):
        with self.__cond:
            if success is not None:
                self.__on_success.append(success)
                if self.__status == DONE:
                    self.scheduler.call(success, self.__result)
            if failure is not None:
                self.__on_failure.append(failure)
                if self.__status == FAILED:
                    self.scheduler.call(failure, self.__result, self.__traceback)
            if cleanup is not None:
                self.__on_cleanup.append(cleanup)

    def cancel(self):
        with self.__cond:
            if self.__status == WAITING:
                self.__status = CANCELLED
                self.__cond.notify_all()

    def __del__(self):
        if self.__status == FAILED and not self.__on_failure:
            print self.__traceback
        for handler in self.__on_cleanup:
            self.scheduler.call(handler, self)

class CoroutineTask(Task):
    def __init__(self, scheduler, gen):
        Task.__init__(self, scheduler)
        if not isinstance(gen, types.GeneratorType):
            raise TypeError("CoroutineTask expected generator, got %s"
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
            if isinstance(ret, Task):
                self.__cont = ret
                ret.bind(self.__success_next, self.__failure_next)
            else:
                self.set_done(ret)

    def __success_next(self, result):
        self.__next(self.__gen.send, result)

    def __failure_next(self, exn, traceback):
        self.__next(self.__gen.throw, exn)

    def cancel(self):
        Task.cancel(self)
        if self.__cont is not None:
            self.__cont.cancel()
            self.__cont = None

def coroutine(scheduler, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        co = CoroutineTask(scheduler, func(*args, **kwargs))
        co.start()
        return co
    return wrapper
