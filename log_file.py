import os, time
import fileutil

def get_log_contents(filename, max_log_size):
    try:
        with open(filename) as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if size > max_log_size:
                f.seek(-max_log_size, os.SEEK_END)
                return "\n".join(f.read().split("\n")[1:])
            else:
                f.seek(0)
                return f.read()
    except Exception:
        return ""

def get_log_file(filename, max_log_size=1024**2):
    return LogFileWrapper(filename, max_log_size)

class LogFileWrapper(object):
    def __init__(self, filename, max_log_size):
        self.filename = filename
        self.max_log_size = max_log_size
        self.file = None
        self.timestamp = time.strftime("===== %Y-%m-%d %H:%M:%S =====\n")

    def write(self, s):
        if self.file is None:
            contents = get_log_contents(self.filename, self.max_log_size)
            header_newline = ""
            if contents:
                header_newline = "\n" if contents[-1] == "\n" else "\n\n"
            file = open(self.filename, "w")
            try:
                file.write(contents)
                file.write(header_newline + self.timestamp)
                file.flush()
            except Exception:
                file.close()
                raise
            else:
                self.file = file
        self.file.write(s)

    def close(self):
        if self.file:
            self.file.close()
