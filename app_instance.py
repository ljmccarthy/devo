import os.path, json, threading, tempfile, getpass
from multiprocessing.connection import Client, Listener

import fileutil
from async import Future, get_scheduler
from util import pid_exists

class AppInstance(object):
    def __init__(self, instance_filename):
        instance = json.loads(fileutil.read_file(instance_filename))
        self.pid = instance["pid"]
        self.address = str(instance["address"])
        self.client = None
        if not pid_exists(self.pid):
            raise Exception("Instance pid is invalid")

    def connect(self):
        if self.client is None:
            self.client = Client(self.address)
        return self.client

    def call(self, name, *args, **kwargs):
        client = self.connect()
        client.send((name, args, kwargs))
        return client.recv()

def make_instance_filename(name):
    return os.path.join(tempfile.gettempdir(), "." + getpass.getuser() + ".devo-instance")

def get_app_instance(app_name):
    try:
        return AppInstance(make_instance_filename(app_name))
    except Exception:
        pass

class AppListener(object):
    def __init__(self, app_name, handler):
        self.handler = handler
        self.listener = Listener()
        self.instance_filename = make_instance_filename(app_name)

        with open(self.instance_filename, "w") as f:
            f.write(json.dumps({"pid": os.getpid(), "address": self.listener.address}, sort_keys=True))

        self.thread = threading.Thread(target=self.accept_loop)
        self.thread.daemon = True
        self.thread.start()

    def accept_loop(self):
        listener = self.listener
        while True:
            try:
                conn = listener.accept()
            except Exception:
                pass
            else:
                try:
                    thread = threading.Thread(target=self.call_loop, args=(conn,))
                    thread.daemon = True
                    thread.start()
                except Exception:
                    conn.close()

    def get_call(self, call):
        try:
            method_name = call[0]
            args = call[1] if len(call) >= 1 else ()
            kwargs = call[2] if len(call) >= 2 else {}
            method = getattr(self.handler, method_name, None)
            return method, args, kwargs
        except Exception:
            return None, (), {}

    def call(self, method, args, kwargs):
        future = Future()
        scheduler = get_scheduler()
        scheduler.post_call(future.call, method, *args, **kwargs)
        result = future.wait()
        if isinstance(result, Future):
            result = result.wait()
        return result

    def call_loop(self, conn):
        while True:
            try:
                call = conn.recv()
            except EOFError:
                return
            if call is None:
                return

            result = None
            method, args, kwargs = self.get_call(call)
            if method:
                try:
                    result = self.call(method, args, kwargs)
                except Exception:
                    pass

            try:
                conn.send(result)
            except Exception:
                pass

    def shutdown(self):
        if self.listener:
            try:
                os.remove(self.instance_filename)
            except OSError:
                pass

            self.listener.close()
            self.listener = None
