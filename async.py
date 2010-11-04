import sys, traceback, threading, functools, types, weakref, collections

class AsyncCallThreadPool(object):
    def __init__(self, max_threads):
        self.max_threads = max_threads
        self.num_waiting = 0
        self.threads = set()
        self.calls = collections.deque()
        self.quit = False
        self.cond = threading.Condition()

    def call(self, func, args, kwargs):
        future = Future()
        with self.cond:
            self.calls.appendleft((future, func, args, kwargs))
            if self.num_waiting == 0 and len(self.threads) < self.max_threads:
                thread = threading.Thread(target=self.__call_thread)
                thread.daemon = True
                thread.start()
                self.threads.add(thread)
            self.cond.notify()
        return future

    def __call_thread(self):
        try:
            while True:
                with self.cond:
                    if not self.calls:
                        self.num_waiting += 1
                        try:
                            self.cond.wait(1)
                        finally:
                            self.num_waiting -= 1
                    if self.quit or not self.calls:
                        return
                    future, func, args, kwargs = self.calls.pop()
                future.call(func, *args, **kwargs)
        finally:
            with self.cond:
                self.threads.remove(threading.current_thread())

    def shutdown(self):
        with self.cond:
            self.quit = True
            self.cond.notify_all()
        while True:
            with self.cond:
                threads = list(self.threads)
            if not threads:
                break
            for thread in threads:
                thread.join()

class Scheduler(object):
    def __init__(self, max_threads=10):
        self.__async_pool = AsyncCallThreadPool(max_threads)

    def call(self, func, *args, **kwargs):
        raise NotImplementedError()

    def post_call(self, func, *args, **kwargs):
        raise NotImplementedError()

    def async_call(self, func, *args, **kwargs):
        return self.__async_pool.call(func, args, kwargs)

    def shutdown(self):
        self.__async_pool.shutdown()

_global_scheduler = None

def set_scheduler(scheduler):
    global _global_scheduler
    if _global_scheduler:
        raise Exception("async scheduler already set")
    if not isinstance(scheduler, Scheduler):
        raise TypeError("scheduler must be a subclass of async.Scheduler")
    _global_scheduler = scheduler

def shutdown_scheduler():
    global _global_scheduler
    if _global_scheduler:
        _global_scheduler.shutdown()

WAITING, DONE, FAILED, CANCELLED = range(4)

class FutureNotReady(Exception):
    pass

class FutureAlreadySet(Exception):
    pass

class FutureCancelled(Exception):
    pass

class Future(object):
    def __init__(self, context=""):
        self.__context = context
        self.__on_success = []
        self.__on_failure = []
        self.__on_cancelled = []
        self.__on_finished = []
        self.__failure_handled = False
        self.__status = WAITING
        self.__result = None
        self.__traceback = ""
        self.__cond = threading.Condition()

    def __finish(self):
        with self.__cond:
            if self.__status == DONE:
                handlers = self.__on_success
                args = (self.__result,)
            elif self.__status == FAILED:
                handlers = self.__on_failure
                args = (self.__result, self.__traceback)
                if handlers:
                    self.__failure_handled = True
            elif self.__status == CANCELLED:
                handlers = self.__on_cancelled
                args = (self,)
            else:
                return
            finished_handlers = self.__on_finished
            if finished_handlers:
                self.__failure_handled = True
            self.__on_success = []
            self.__on_failure = []
            self.__on_cancelled = []
            self.__on_finished = []
        for handler in handlers:
            _global_scheduler.call(handler, *args)
        for handler in finished_handlers:
            _global_scheduler.call(handler, self)

    def set_done(self, result):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise FutureAlreadySet()
            self.__result = result
            self.__status = DONE
            self.__cond.notify_all()
        _global_scheduler.post_call(self.__finish)

    def set_failed(self, exn, traceback):
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise FutureAlreadySet()
            self.__result = exn
            self.__traceback = traceback
            self.__status = FAILED
            self.__cond.notify_all()
        _global_scheduler.post_call(self.__finish)

    def cancel(self):
        with self.__cond:
            if self.__status != WAITING:
                return
            self.__status = CANCELLED
            self.__cond.notify_all()
        _global_scheduler.post_call(self.__finish)

    def call(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except SystemExit:
            self.cancel()
            raise
        except:
            exn = sys.exc_info()[1]
            tbstr = traceback.format_exc()
            self.set_failed(exn, tbstr)
        else:
            self.set_done(result)

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

    def bind(self, success=None, failure=None, cancelled=None, finished=None):
        with self.__cond:
            if success is not None:
                if self.__status == DONE:
                    _global_scheduler.post_call(success, self.__result)
                elif self.__status == WAITING:
                    self.__on_success.append(success)
            if failure is not None:
                if self.__status == FAILED:
                    self.__failure_handled = True
                    _global_scheduler.post_call(failure, self.__result, self.__traceback)
                elif self.__status == WAITING:
                    self.__on_failure.append(failure)
            if cancelled is not None:
                if self.__status == CANCELLED:
                    _global_scheduler.post_call(cancelled, self)
                elif self.__status == WAITING:
                    self.__on_cancelled.append(cancelled)
            if finished is not None:
                if self.__status != WAITING:
                    self.__failure_handled = True
                    _global_scheduler.post_call(finished, self)
                elif self.__status == WAITING:
                    self.__on_finished.append(finished)

    def __del__(self):
        if Future and self.__status == FAILED and not self.__failure_handled:
            message = "Future failed: %s\n" % self.__traceback.rstrip("\n")
            if self.__context:
                message += "Context of Future invocation:\n%s\n" % self.__context.rstrip("\n")
            print message

class Coroutine(Future):
    def __init__(self, gen, context):
        Future.__init__(self, context)
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

    def __next(self, func, *args):
        self.__cont = None
        try:
            ret = func(*args)
        except StopIteration:
            self.set_done(None)
        except FutureCancelled:
            self.cancel()
        except SystemExit:
            self.cancel()
            raise
        except:
            exn = sys.exc_info()[1]
            tbstr = traceback.format_exc()
            self.set_failed(exn, tbstr)
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
        self.__next(self.__gen.throw, FutureCancelled())

    def cancel(self):
        Future.cancel(self)
        if self.__cont is not None:
            self.__cont.cancel()
            self.__cont = None

class CoroutineManager(object):
    def __init__(self):
        self.__futures = set()

    def add(self, future):
        self.__futures.add(weakref.ref(future, self.__futures.discard))

    def cancel(self):
        for ref in self.__futures:
            future = ref()
            if future is not None:
                future.cancel()
        self.__futures.clear()

class CoroutineQueue(object):
    def __init__(self):
        self.__running = None
        self.__queue = []

    def run(self, func, args, kwargs):
        co = Coroutine(func(*args, **kwargs), "".join(traceback.format_stack()))
        if self.__running is not None:
            self.__queue.append(co)
        else:
            self.__running = weakref.ref(co)
            co.bind(finished=self.__next)
            co.start()
        return co

    def __next(self, future):
        if self.__queue:
            co = self.__queue.pop()
            self.__running = weakref.ref(co)
            co.bind(finished=self.__next)
            co.start()
        else:
            self.__running = None

    def cancel(self):
        self.__queue = []
        if self.__running is not None:
            co = self.__running()
            if co is not None:
                co.cancel()

def is_generator_function(func):
    return isinstance(func, (types.FunctionType, types.MethodType)) \
       and (func.func_code.co_flags & 0x20) != 0

def coroutine(func):
    if not is_generator_function(func):
        raise TypeError("@coroutine requires a generator function")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        co = Coroutine(func(*args, **kwargs), "".join(traceback.format_stack()))
        co.start()
        return co
    return wrapper

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

def queued_coroutine(queue_name):
    def decorator(func):
        if not is_generator_function(func):
            raise TypeError("@queued_coroutine requires a generator function")
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            queue = getattr(self, queue_name)
            return queue.run(func, (self,) + args, kwargs)
        return wrapper
    return decorator

def async_call(func, *args, **kwargs):
    return _global_scheduler.async_call(func, *args, **kwargs)

def async_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return async_call(func, *args, **kwargs)
    return wrapper
