import re

def compile_file_patterns(patterns):
    return re.compile("^%s$" % "|".join("(%s)" % re.escape(p).replace("\\*", ".*") for p in patterns))

hidden_files = [".*", "*~", "*.swp", "*.pyc", "*.pyo", "*.o", "*.a", "*.obj", "*.lib", "*.class"]
hidden_dirs = [".*", "CVS", "__pycache__"]

class DirTreeFilter(object):
    def __init__(self, show_hidden=False, show_files=True, show_dirs=True,
                 hidden_files=hidden_files, hidden_dirs=hidden_dirs):
        self.show_hidden = show_hidden
        self.show_files = show_files
        self.show_dirs = show_dirs
        self.r_hidden_file = compile_file_patterns(hidden_files)
        self.r_hidden_dir = compile_file_patterns(hidden_dirs)

    def __call__(self, info):
        if info.hidden and not self.show_hidden:
            return False
        if info.is_file and not self.show_files:
            return False
        if info.is_dir:
            if not self.show_dirs:
                return False
            if self.r_hidden_dir.match(info.filename):
                return False
        else:
            if self.r_hidden_file.match(info.filename):
                return False
        return True
