import os, re
from util import is_text_file

class FindInFilesAborted(Exception):
    pass

class FindInFiles(object):
    def __init__(self, path, match, output):
        self.path = path
        self.match = match
        self.output = output
        self.encoding = "utf-8"
        self.quit = False

    def _search_file(self, filepath):
        if self.quit:
            raise FindInFilesAborted()
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
                        self.output.add_file(filepath)
                        matched_file = True
                    self.output.add_line(line_num, line)
                if self.quit:
                    raise FindInFilesAborted()
            if matched_file:
                self.output.end_file()

    def _search_dir(self, dirpath):
        if self.quit:
            raise FindInFilesAborted()
        try:
            dirlist = os.listdir(dirpath)
        except OSError:
            pass
        else:
            dirlist.sort()
            for name in dirlist:
                if self.quit:
                    raise FindInFilesAborted()
                path = os.path.join(dirpath, name)
                try:
                    if os.path.isfile(path):
                        self._search_file(path)
                    elif os.path.isdir(path):
                        self._search_dir(path)
                except OSError:
                    pass

    def search(self):
        self.quit = False
        try:
            self._search_dir(self.path)
        except FindInFilesAborted:
            self.output.abort_find()
        except Exception:
            self.output.end_find()
        else:
            self.output.end_find()

    def stop(self):
        self.quit = True

class FindInFilesFileOutput(object):
    def __init__(self, file):
        self.file = file
        self.max_line_length = 100

    def add_file(self, filepath):
        self.file.write(filepath + "\n")

    def add_line(self, line_num, line):
        if len(line) > self.max_line_length:
            line = line[:self.max_line_length] + "..."
        self.file.write(" %d: %s\n" % (line_num, line))

    def end_file(self):
        self.file.write("\n")

    def end_find(self):
        pass

def find_in_files(path, matcher, output):
    return FindInFiles(path, matcher, output).search()

def make_matcher(s, case_sensitive=True):
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile("^.*" + re.escape(s) + ".*$", flags).match

if __name__ == "__main__":
    import sys
    find_in_files(".", make_matcher("class"), FindInFilesFileOutput(sys.stdout))
