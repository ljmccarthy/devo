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

    def log_error(self, traceback):
        self.post_call(sys.stdout.write, traceback + "\n")

_global_scheduler = None

def get_scheduler():
    global _global_scheduler
    return _global_scheduler

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

class _FutureCleanup(object):
    __slots__ = (
        "__future_ref",
        "__context",
        "__on_finished",
        "__traceback",
    )

    def __init__(self, future, context, on_finished):
        self.__future_ref = weakref.ref(future, self.__finish)
        self.__context = context
        self.__on_finished = on_finished
        self.__traceback = ""

    def failure_traceback(self, traceback):
        self.__traceback = traceback

    def failure_handled(self):
        self.__future_ref = None
        self.__traceback = ""

    def finish_handled(self):
        self.__on_finished = ()

    def __finish(self, ref):
        if self.__future_ref:
            self.__future_ref = None
            self.__on_finished, on_finished = None, self.__on_finished
            if self.__traceback:
                message = "Future failed: %s\n" % self.__traceback.rstrip("\n")
                if self.__context:
                    message += "Context of Future invocation:\n%s\n" % self.__context.rstrip("\n")
                _global_scheduler.log_error(message)
            for handler in on_finished:
                _global_scheduler.post_call(handler)

class Future(object):
    __slots__ = (
        "__weakref__",
        "name",
        "context",
        "__on_success",
        "__on_failure",
        "__on_cancelled",
        "__on_finished",
        "__status",
        "__result",
        "__traceback",
        "__cond",
        "__cleanup",
    )

    def __init__(self, name="", context=""):
        self.name = name
        self.context = context
        self.__on_success = []
        self.__on_failure = []
        self.__on_cancelled = []
        self.__on_finished = []
        self.__status = WAITING
        self.__result = None
        self.__traceback = ""
        self.__cond = threading.Condition()
        self.__cleanup = _FutureCleanup(self, context, self.__on_finished)

    def __repr__(self):
        cls = self.__class__
        return "<%s.%s of %r>" % (cls.__module__, cls.__name__, self.name)

    def __finish(self):
        with self.__cond:
            failure_handled = True
            if self.__status == DONE:
                handlers = self.__on_success
                args = (self.__result,)
            elif self.__status == FAILED:
                handlers = self.__on_failure
                args = (self.__result, self.__traceback)
                if not handlers:
                    failure_handled = False
            elif self.__status == CANCELLED:
                handlers = self.__on_cancelled
                args = (self,)
            else:
                return
            finished_handlers = self.__on_finished
            self.__on_success = None
            self.__on_failure = None
            self.__on_cancelled = None
            self.__on_finished = None
            self.__cleanup.finish_handled()
            if failure_handled:
                self.__cleanup.failure_handled()
        for handler in handlers:
            _global_scheduler.call(handler, *args)
        for handler in finished_handlers:
            _global_scheduler.call(handler)

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
        if not isinstance(traceback, basestring):
            raise TypeError("Future traceback must be a string")
        with self.__cond:
            if self.__status == CANCELLED:
                return
            if self.__status != WAITING:
                raise FutureAlreadySet()
            self.__result = exn
            self.__traceback = traceback
            self.__status = FAILED
            self.__cleanup.failure_traceback(traceback)
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
                self.__cleanup.failure_handled()
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
        calls = []
        with self.__cond:
            if success is not None:
                if self.__status == DONE:
                    calls.append((success, self.__result))
                elif self.__status == WAITING:
                    self.__on_success.append(success)
            if failure is not None:
                if self.__status == FAILED:
                    self.__cleanup.failure_handled()
                    calls.append((failure, self.__result, self.__traceback))
                elif self.__status == WAITING:
                    self.__on_failure.append(failure)
            if cancelled is not None:
                if self.__status == CANCELLED:
                    calls.append((cancelled, self))
                elif self.__status == WAITING:
                    self.__on_cancelled.append(cancelled)
            if finished is not None:
                if self.__status != WAITING:
                    calls.append((finished,))
                elif self.__status == WAITING:
                    self.__on_finished.append(finished)
        for call in calls:
            _global_scheduler.post_call(*call)

class Coroutine(Future):
    __slots__ = (
        "__generator",
        "__continuation",
        "__running",
    )

    def __init__(self, generator, name="", context=""):
        Future.__init__(self, name, context)
        if not isinstance(generator, types.GeneratorType):
            raise TypeError("Coroutine expected generator, got %s"
                            % generator.__class__.__name__)
        self.__generator = generator
        self.__continuation = None
        self.__running = False

    def start(self):
        if not self.__running and self.__generator:
            self.__running = True
            self.__next(self.__generator.next)

    def __next(self, func, *args):
        self.__continuation = None
        try:
            ret = func(*args)
        except StopIteration:
            self.set_done(None)
        except FutureCancelled:
            Future.cancel(self)
        except SystemExit:
            Future.cancel(self)
            raise
        except:
            self.set_failed(sys.exc_info()[1], traceback.format_exc())
        else:
            if isinstance(ret, Future):
                self.__continuation = ret
                ret.bind(self.__success_next, self.__failure_next, self.__cancelled_next)
            else:
                try:
                    self.__generator.close()
                except SystemExit:
                    Future.cancel(self)
                    raise
                except:
                    self.set_failed(sys.exc_info()[1], traceback.format_exc())
                else:
                    self.set_done(ret)

    def __success_next(self, result):
        if self.__generator:
            self.__next(self.__generator.send, result)

    def __failure_next(self, exn, traceback):
        if self.__generator:
            self.__next(self.__generator.throw, exn)

    def __cancelled_next(self, future):
        if self.__generator:
            self.__next(self.__generator.throw, FutureCancelled())

    def cancel(self):
        Future.cancel(self)

        if self.__continuation:
            self.__continuation.cancel()
            self.__continuation = None

        if self.__generator:
            try:
                self.__generator.close()
            except SystemExit:
                raise
            except:
                pass
            finally:
                self.__generator = None

class CoroutineManager(object):
    def __init__(self):
        self.__futures = weakref.WeakSet()

    def add(self, future):
        self.__futures.add(future)

    def cancel(self):
        for future in self.__futures:
            future.cancel()
        self.__futures.clear()

class CoroutineQueue(object):
    def __init__(self):
        self.__running = None
        self.__queue = []

    def add(self, co):
        if self.__running is not None:
            self.__queue.append(co)
        else:
            self.__running = weakref.ref(co)
            co.bind(finished=self.__next)
            co.start()

    def run(self, func, args, kwargs):
        co = Coroutine(func(*args, **kwargs), func.__name__, "".join(traceback.format_stack()))
        self.add(co)
        return co

    def __next(self):
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
        co = Coroutine(func(*args, **kwargs), func.__name__, "".join(traceback.format_stack()))
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
