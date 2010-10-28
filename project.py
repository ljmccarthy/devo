import os
import json

import fileutil

class Project(object):
    def __init__(self, name="", rootdir="", filename="", session=None):
        if session is None:
            session = {}
        if "project" not in session:
            session["project"] = {}
        project = session["project"]
        project.setdefault("name", name)
        project.setdefault("rootdir", rootdir)
        project.setdefault("filename", filename)
        project.setdefault("commands", [])
        self._session = session

    @property
    def name(self):
        return self._session["project"]["name"]

    @property
    def filename(self):
        return self._session["project"]["filename"]

    @property
    def rootdir(self):
        return self._session["project"]["rootdir"]

    @property
    def commands(self):
        return self._session["project"]["commands"]

    @commands.setter
    def commands(self, commands):
        self._session["project"]["commands"] = commands

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        session["project"] = self._session["project"]
        self._session = session

def read_project(filename):
    with open(filename, "rb") as f:
        session = json.loads(f.read())
    return Project(filename=filename, session=session)

def write_project(project):
    fileutil.mkpath(os.path.dirname(project.filename))
    data = json.dumps(project.session, indent=2)
    fileutil.atomic_write_file(project.filename, data)
