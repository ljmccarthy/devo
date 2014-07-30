#!/usr/bin/env python2.7

import os.path, subprocess

def run(*args, **kwargs):
    subprocess.check_call(args, **kwargs)

def get_aui():
    if os.path.isdir("aui"):
        run("svn", "update", cwd="aui")
    else:
        run("svn", "checkout", "http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/agw/aui", "aui")

def get_fsmonitor():
    if os.path.isdir("fsmonitor"):
        run("git", "pull", cwd="fsmonitor")
    else:
        run("git", "clone", "https://github.com/shaurz/fsmonitor.git")


def get_components():
    get_fsmonitor()

if __name__ == "__main__":
    get_components()
