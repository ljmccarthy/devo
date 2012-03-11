#!/usr/bin/env python2.7

import os.path, subprocess

def run(*args):
    subprocess.check_call(args)

if os.path.isdir("aui"):
    run("svn", "update", "aui")
else:
    run("svn", "checkout", "http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/agw/aui", "aui")
