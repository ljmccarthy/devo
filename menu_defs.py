import wx
from menu import MenuBar, Menu, MenuItem, MenuSeparator, MenuHook

ID_FIND_NEXT = wx.NewId()
ID_FIND_SELECTED = wx.NewId()
ID_GO_TO_LINE = wx.NewId()
ID_UNINDENT = wx.NewId()
ID_NEW_PROJECT = wx.NewId()
ID_OPEN_PROJECT = wx.NewId()
ID_CLOSE_PROJECT = wx.NewId()
ID_EDIT_PROJECT = wx.NewId()
ID_ORGANISE_PROJECTS = wx.NewId()

edit_menu = Menu("&Edit", [
    MenuItem(wx.ID_UNDO, "&Undo", "Ctrl+Z"),
    MenuItem(wx.ID_REDO, "&Redo", "Ctrl+Shift+Z"),
    MenuSeparator,
    MenuItem(wx.ID_CUT, "Cu&t", "Ctrl+X"),
    MenuItem(wx.ID_COPY, "&Copy", "Ctrl+C"),
    MenuItem(wx.ID_PASTE, "&Paste", "Ctrl+V"),
    MenuSeparator,
    MenuItem(wx.ID_SELECTALL, "Select &All", "Ctrl+A"),
    MenuSeparator,
    MenuItem(wx.ID_FIND, "&Find...", "Ctrl+F"),
    MenuItem(ID_FIND_SELECTED, "&Find Selected...", "Ctrl+Shift+F"),
    MenuItem(ID_FIND_NEXT, "Find &Next", "F3"),
    MenuItem(ID_GO_TO_LINE, "&Go To Line...", "Ctrl+G"),
    MenuSeparator,
    MenuItem(ID_UNINDENT, "Unin&dent", "Ctrl+Shift+I"),
])

menubar = MenuBar([
    Menu("&File", [
        MenuItem(wx.ID_NEW, "&New", "Ctrl+T"),
        MenuItem(wx.ID_OPEN, "&Open...", "Ctrl+O"),
        MenuItem(wx.ID_SAVE, "&Save", "Ctrl+S"),
        MenuItem(wx.ID_SAVEAS, "Save &As", "Ctrl+Shift+S"),
        MenuItem(wx.ID_CLOSE, "&Close", "Ctrl+W"),
        MenuSeparator,
        MenuItem(wx.ID_EXIT, "E&xit"),
    ]),
    edit_menu,
    Menu("&Project", [
        MenuItem(ID_NEW_PROJECT, "&New Project", "Ctrl+Alt+T"),
        MenuItem(ID_OPEN_PROJECT, "&Open Project...", "Ctrl+Alt+O"),
        MenuItem(ID_CLOSE_PROJECT, "&Close Project", "Ctrl+Alt+W"),
        MenuSeparator,
        MenuItem(ID_EDIT_PROJECT, "&Edit Current Project..."),
        MenuItem(ID_ORGANISE_PROJECTS, "O&rganise Projects..."),
        MenuHook("projects"),
    ]),
])
