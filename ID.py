__all__ = """\
FIND_NEXT
FIND_PREV
SEARCH
GO_TO_LINE
COMMENT
UNCOMMENT
NEW_PROJECT
OPEN_PROJECT
CLOSE_PROJECT
EDIT_PROJECT
ORGANISE_PROJECTS
CONFIGURE_SHARED_COMMANDS
CONFIGURE_PROJECT_COMMANDS
VIEW_SETTINGS
FULL_SCREEN
REPORT_BUG
DIRTREE_EDIT
DIRTREE_PREVIEW
DIRTREE_OPEN_FOLDER
DIRTREE_SEARCH
DIRTREE_SEARCH_FOLDER
""".strip().split()

def init():
    import sys, wx
    module = sys.modules[__name__]
    wxids = []
    for id_name in dir(wx):
        if id_name.startswith("ID_"):
            setattr(module, id_name[3:], getattr(wx, id_name))
            wxids.append(id_name[3:])
    for id_name in __all__:
        if not hasattr(module, id_name):
            setattr(module, id_name, wx.NewId())
    __all__.extend(wxids)

init()
del init

from dirtree_constants import (
    ID_DIRTREE_OPEN as DIRTREE_OPEN,
    ID_DIRTREE_RENAME as DIRTREE_RENAME,
    ID_DIRTREE_DELETE as DIRTREE_DELETE,
    ID_DIRTREE_NEW_FOLDER as DIRTREE_NEW_FOLDER,
    ID_DIRTREE_EXPAND_ALL as DIRTREE_EXPAND_ALL,
    ID_DIRTREE_COLLAPSE_ALL as DIRTREE_COLLAPSE_ALL)
