#!/usr/bin/env python2.7

import os.path, subprocess

def run(*args, **kwargs):
    subprocess.check_call(args, **kwargs)

def get_submodules():
    run("git", "submodule", "update", "--init")

def get_aui():
    if os.path.isdir("aui"):
        run("svn", "update", cwd="aui")
    else:
        run("svn", "checkout", "http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/agw/aui", "aui")

def get_components():
    get_submodules()
    get_aui()

if __name__ == "__main__":
    get_components()
