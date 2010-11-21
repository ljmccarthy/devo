import sys
import wx

__all__ = """\
FIND_NEXT
FIND_PREV
GO_TO_LINE
UNINDENT
NEW_PROJECT
OPEN_PROJECT
CLOSE_PROJECT
EDIT_PROJECT
ORGANISE_PROJECTS
CONFIGURE_COMMANDS
ABOUT_BOX
""".strip().split()

def init():
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
