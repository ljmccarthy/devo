import os
import json

import fileutil

class Project(object):
    def __init__(self, name, rootdir, filename, session=None):
        self.name = name
        self.rootdir = rootdir
        self.filename = filename
        self.session = session

def read_project(filename, rootdir):
    with open(filename, "rb") as f:
        session = json.loads(f.read())
    return Project("", rootdir, filename, session)

def write_project(project):
    fileutil.mkpath(os.path.dirname(project.filename))
    data = json.dumps(project.session, indent=2)
    fileutil.atomic_write_file(project.filename, data)
