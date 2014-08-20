import re
from util import compile_file_patterns

hidden_files = ".*;*~;*.swp;*.pyc;*.pyo;*.o;*.a;*.obj;*.lib;*.class"
hidden_dirs = ".*;CVS;__pycache__"

re_hidden_files = compile_file_patterns(hidden_files)
re_hidden_dirs = compile_file_patterns(hidden_dirs)

class DirTreeFilter(object):
    def __init__(self, show_hidden=False, show_files=True, show_dirs=True,
                 hidden_files=hidden_files, hidden_dirs=hidden_dirs):
        self.show_hidden = show_hidden
        self.show_files = show_files
        self.show_dirs = show_dirs
        self.re_hidden_file = re_hidden_files
        self.re_hidden_dirs = re_hidden_dirs

    def __call__(self, info):
        if info.hidden and not self.show_hidden:
            return False
        if info.is_file and not self.show_files:
            return False
        if info.is_dir:
            if not self.show_dirs:
                return False
            if self.re_hidden_dirs.match(info.filename):
                return False
        else:
            if self.re_hidden_file.match(info.filename):
                return False
        return True
