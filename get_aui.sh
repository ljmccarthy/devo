#!/bin/sh

if [ -d aui ]; then
    svn update aui
else
    svn co 'http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/agw/aui' aui
fi
