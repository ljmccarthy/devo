import wx
import sys
import threading
import traceback
import inspect
import weakref

EVT_DESTROY = wx.PyEventBinder(wx.wxEVT_DESTROY, 0)

class Signal(object):
    def __init__(self, owner=None):
        self.__lock = threading.Lock()
        self.__handlers = []
        if isinstance(owner, wx.Window):
            owner.Bind(EVT_DESTROY, lambda evt: self.destroy())
        elif owner is not None:
            self.__owner_ref = weakref.ref(owner, lambda ref: self.destroy())

    def signal(self, arg):
        if self.__lock is None:
            return
        wx.CallAfter(self.__dosignal, arg)

    def __dosignal(self, arg):
        if self.__lock is None:
            return
        with self.__lock:
            dead = []
            for i, (func, ref) in enumerate(self.__handlers):
                try:
                    if ref is None:
                        func(arg)
                    else:
                        obj = ref()
                        if isinstance(obj, wx._core._wxPyDeadObject):
                            dead.append(i)
                        if obj is not None:
                            func(obj, arg)
                except SystemExit:
                    raise
                except:
                    sys.stdout.write(
                        "\nError signalling %s with argument %s:\n\n%s" %
                        (func, arg, traceback.format_exc()))
            for i in reversed(dead):
                del self.__handlers[i]

    def bind(self, func):
        if self.__lock is None:
            return
        if not inspect.isfunction(func) and not inspect.ismethod(func) and hasattr(func, "__call__"):
            func = func.__call__
        if inspect.ismethod(func):
            handler = (func.__func__, weakref.ref(func.__self__, self.__unbind_weakref))
        elif inspect.isfunction(func):
            handler = (func, None)
        else:
            raise TypeError("Callable required")
        with self.__lock:
            self.__handlers.append(handler)

    def __unbind_weakref(self, ref):
        if self.__lock is None:
            return
        with self.__lock:
            for i in xrange(len(self.__handlers)-1, -1, -1):
                if self.__handlers[i][1] is ref:
                    del self.__handlers[i]

    def unbind(self, func):
        if self.__lock is None:
            return
        with self.__lock:
            obj = None
            if inspect.ismethod(func) and func.__self__ is not None:
                obj = func.__self__
                func = func.__func__
            for i in xrange(len(self.__handlers)-1, -1, -1):
                ref = self.__handlers[i][1]
                if self.__handlers[i][0] is func and \
                (obj is None or (ref is not None and obj is ref())):
                    del self.__handlers[i]

    def unbind_object(self, obj):
        if self.__lock is None:
            return
        with self.__lock:
            for i in xrange(len(self.__handlers)-1, -1, -1):
                ref = self.__handlers[i][1]
                if ref is not None and obj() is ref():
                    del self.__handlers[i]

    def clear(self):
        if self.__lock is None:
            return
        with self.__lock:
            self.__handlers = []

    def destroy(self):
        if self.__lock is None:
            return
        with self.__lock:
            self.__handlers = []
            self.__lock = None
