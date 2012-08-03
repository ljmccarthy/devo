import app_info
import ID
from menu import MenuBar, Menu, MenuItem, MenuSeparator, MenuHook

edit_menu = Menu("&Edit", [
    MenuItem(ID.UNDO, "&Undo", "Ctrl+Z"),
    MenuItem(ID.REDO, "&Redo", "Ctrl+Shift+Z"),
    MenuSeparator,
    MenuItem(ID.CUT, "Cu&t", "Ctrl+X"),
    MenuItem(ID.COPY, "&Copy", "Ctrl+C"),
    MenuItem(ID.PASTE, "&Paste", "Ctrl+V"),
    MenuSeparator,
    MenuItem(ID.SELECTALL, "Select &All", "Ctrl+A"),
    MenuSeparator,
    MenuItem(ID.FIND, "&Find...", "Ctrl+F"),
    MenuItem(ID.FIND_NEXT, "Find &Next", "F3"),
    MenuItem(ID.FIND_PREV, "Find Pre&vious", "Shift+F3"),
    MenuItem(ID.GO_TO_LINE, "&Go To Line...", "Ctrl+G"),
    MenuSeparator,
    MenuItem(ID.INDENT, "&Indent", "Ctrl+I"),
    MenuItem(ID.UNINDENT, "Unin&dent", "Ctrl+U"),
    MenuSeparator,
    MenuItem(ID.COMMENT, "Comment", "Ctrl+R"),
    MenuItem(ID.UNCOMMENT, "Uncomment", "Ctrl+E"),
])

menubar = MenuBar([
    Menu("&File", [
        MenuItem(ID.NEW, "&New", "Ctrl+T"),
        MenuItem(ID.OPEN, "&Open...", "Ctrl+O"),
        MenuItem(ID.SAVE, "&Save", "Ctrl+S"),
        MenuItem(ID.SAVEAS, "Save &As", "Ctrl+Shift+S"),
        MenuItem(ID.CLOSE, "&Close", "Ctrl+W"),
        MenuSeparator,
        MenuItem(ID.SEARCH, "Searc&h...", "Ctrl+Shift+F"),
        MenuSeparator,
        MenuHook("recent_files"),
        MenuSeparator,
        MenuItem(ID.EXIT, "E&xit"),
    ]),
    edit_menu,
    Menu("&Project", [
        MenuItem(ID.NEW_PROJECT, "&New Project...", "Ctrl+Alt+T"),
        MenuItem(ID.OPEN_PROJECT, "&Open Project...", "Ctrl+Alt+O"),
        MenuItem(ID.CLOSE_PROJECT, "&Close Project", "Ctrl+Alt+W"),
        #MenuSeparator,
        #MenuItem(ID.EDIT_PROJECT, "&Edit Current Project..."),
        #MenuItem(ID.ORGANISE_PROJECTS, "O&rganise Projects..."),
        MenuSeparator,
        MenuHook("projects"),
    ]),
    Menu("&Commands", [
        MenuItem(ID.CONFIGURE_SHARED_COMMANDS, "Configure &Shared...", "Ctrl+Shift+F12"),
        MenuItem(ID.CONFIGURE_PROJECT_COMMANDS, "Configure &Project...", "Ctrl+F12"),
        MenuSeparator,
        MenuHook("shared_commands"),
        MenuSeparator,
        MenuHook("project_commands"),
    ]),
    Menu("&Help", [
        MenuItem(ID.REPORT_BUG, "Report Bug"),
        MenuSeparator,
        MenuItem(ID.ABOUT, "&About %s..." % app_info.name),
    ]),
])
