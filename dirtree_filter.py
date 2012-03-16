class DirTreeFilter(object):
    def __init__(self, show_hidden=False, show_files=True, show_dirs=True):
        self.show_hidden = show_hidden
        self.show_files = show_files
        self.show_dirs = show_dirs
        self.hidden_exts = [".pyc", ".pyo", ".o", ".a", ".obj", ".lib", ".swp", "~"]
        self.hidden_dirs = ["CVS", "__pycache__"]

    def __call__(self, info):
        if info.hidden and not self.show_hidden:
            return False
        if info.is_file and not self.show_files:
            return False
        elif info.is_dir:
            if not self.show_dirs:
                return False
            if info.filename in self.hidden_dirs:
                return False
        for ext in self.hidden_exts:
            if info.filename.endswith(ext):
                return False
        if info.filename.startswith(".#"):
            return False
        return True
