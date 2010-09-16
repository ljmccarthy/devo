import os, cPickle as pickle
import fileutil

class Project(object):
    def __init__(self, name, rootdir, filename, session=None):
        self.name = name
        self.rootdir = rootdir
        self.filename = filename
        self.session = session

def read_project(filename, rootdir):
    with open(filename, "rb") as f:
        session = pickle.loads(f.read())
    return Project("", rootdir, filename, session)

def write_project(project):
    fileutil.mkpath(os.path.dirname(project.filename))
    data = pickle.dumps(project.session, pickle.HIGHEST_PROTOCOL)
    fileutil.atomic_write_file(project.filename, data)
