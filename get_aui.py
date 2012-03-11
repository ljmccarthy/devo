#!/usr/bin/env python2.7

import os.path, subprocess

def run(*args):
    subprocess.check_call(args)

def get_aui():
    if os.path.isdir("aui"):
        run("svn", "update", "aui")
    else:
        run("svn", "checkout", "http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/agw/aui", "aui")

if __name__ == "__main__":
    get_aui()
