import mimetypes

class frozen_window(object):
    def __init__(self, win):
        self.win = win

    def __enter__(self):
        self.win.Freeze()

    def __exit__(self, exn_type, exn_value, exn_traceback):
        self.win.Thaw()

def is_text_file(path):
    filetype, encoding = mimetypes.guess_type(path)
    return filetype is None or filetype.startswith("text/")
