import os, re, traceback
from dirtree_node import get_file_info
from util import is_text_file

class SearchAborted(Exception):
    pass

def null_filter(info):
    return True

class Search(object):
    def __init__(self, path, match, output, filter=None):
        self.path = path
        self.match = match
        self.output = output
        self.filter = filter or null_filter
        self.encoding = "utf-8"
        self.quit = False

    def _search_file(self, filepath):
        if self.quit:
            raise SearchAborted()
        self.output.begin_file(self, filepath)
        if not is_text_file(filepath):
            return
        with open(filepath, "r") as f:
            matched_file = False
            for line_num, line in enumerate(f, 1):
                line = line.rstrip("\r\n")
                try:
                    line = line.decode(self.encoding)
                except UnicodeDecodeError:
                    line = line.decode("latin-1")
                if self.match(line):
                    if not matched_file:
                        self.output.add_file(self, filepath)
                        matched_file = True
                    self.output.add_line(self, line_num, line)
                if self.quit:
                    raise SearchAborted()
            if matched_file:
                self.output.end_file(self)

    def _search_dir(self, dirpath):
        if self.quit:
            raise SearchAborted()
        try:
            dirlist = os.listdir(dirpath)
        except OSError:
            pass
        else:
            dirlist.sort()
            for name in dirlist:
                self._search(dirpath, name)

    def _search(self, dirpath, name):
        if self.quit:
            raise SearchAborted()
        try:
            info = get_file_info(dirpath, name)
            if self.filter(info):
                if info.is_file:
                    self._search_file(info.path)
                elif info.is_dir:
                    self._search_dir(info.path)
        except OSError:
            pass

    def search(self):
        self.quit = False
        try:
            self._search(*os.path.split(self.path))
        except SearchAborted:
            self.output.abort_find(self)
        except Exception, e:
            self.output.end_find(self)
            if not isinstance(e, (OSError, IOError)):
                print traceback.format_exc()
        else:
            self.output.end_find(self)

    def stop(self):
        self.quit = True

class SearchFileOutput(object):
    def __init__(self, file):
        self.file = file
        self.max_line_length = 100

    def add_file(self, finder, filepath):
        self.file.write(filepath + "\n")

    def add_line(self, finder, line_num, line):
        if len(line) > self.max_line_length:
            line = line[:self.max_line_length] + "..."
        self.file.write(" %d: %s\n" % (line_num, line))

    def begin_file(self, finder, filepath):
        pass

    def end_file(self, finder):
        self.file.write("\n")

    def end_find(self, finder):
        pass

def make_matcher(pattern, case_sensitive=True, is_regexp=False):
    if not is_regexp:
        pattern = "^.*" + re.escape(pattern)
    flags = re.UNICODE
    if not case_sensitive:
        flags |= re.IGNORECASE
    return re.compile(pattern, flags).search

if __name__ == "__main__":
    import sys
    Search(".", make_matcher("class"), SearchFileOutput(sys.stdout)).search()
