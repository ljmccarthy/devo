import app_info
import ID
import dirtree_constants
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
    MenuItem(ID.COMMENT, "Comment", "Ctrl+/"),
    MenuItem(ID.UNCOMMENT, "Uncomment", "Ctrl+\\"),
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
        MenuItem(ID.CONFIGURE_SHARED_COMMANDS, "Configure &Shared..."),
        MenuItem(ID.CONFIGURE_PROJECT_COMMANDS, "Configure &Project..."),
        MenuSeparator,
        MenuHook("shared_commands"),
        MenuSeparator,
        MenuHook("project_commands"),
    ]),
    Menu("&View", [
        MenuItem(ID.FULL_SCREEN, "&Full Screen", "Ctrl+Alt+F", kind=MenuItem.CHECK),
        MenuSeparator,
        MenuItem(ID.SHOW_PANE_SEARCH, "Show Searc&h Pane", kind=MenuItem.CHECK),
        MenuItem(ID.SHOW_PANE_TERMINAL, "Show &Terminal Pane", kind=MenuItem.CHECK),
        MenuSeparator,
        MenuItem(ID.VIEW_SETTINGS, "&Settings..."),
    ]),
    Menu("&Help", [
        MenuItem(ID.REPORT_BUG, "Report Bug"),
        MenuSeparator,
        MenuItem(ID.ABOUT, "&About %s..." % app_info.name),
    ]),
])

file_context_menu = Menu("", [
    MenuItem(ID.DIRTREE_OPEN, "&Open in External Application"),
    MenuItem(ID.DIRTREE_EDIT, "&Edit with Devo"),
    MenuItem(ID.DIRTREE_PREVIEW, "&Preview in Web View"),
    MenuSeparator,
    MenuItem(ID.DIRTREE_RENAME, "&Rename"),
    MenuItem(ID.DIRTREE_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID.DIRTREE_NEW_FOLDER, "&New Folder..."),
    MenuItem(ID.DIRTREE_OPEN_FOLDER, "Open Containing &Folder"),
    MenuSeparator,
    MenuItem(ID.DIRTREE_SEARCH, "Searc&h File..."),
    MenuItem(ID.DIRTREE_SEARCH_FOLDER, "Search Containing Folder..."),
    MenuSeparator,
    MenuItem(ID.DIRTREE_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID.DIRTREE_COLLAPSE_ALL, "&Collapse All"),
])

dir_context_menu = Menu("", [
    MenuItem(ID.DIRTREE_OPEN, "&Open Folder"),
    MenuItem(ID.DIRTREE_RENAME, "&Rename"),
    MenuItem(ID.DIRTREE_DELETE, "&Delete"),
    MenuSeparator,
    MenuItem(ID.DIRTREE_NEW_FOLDER, "&New Folder..."),
    MenuItem(ID.DIRTREE_OPEN_FOLDER, "Open Containing &Folder"),
    MenuSeparator,
    MenuItem(ID.DIRTREE_SEARCH, "Searc&h Folder..."),
    MenuSeparator,
    MenuItem(ID.DIRTREE_EXPAND_ALL, "E&xpand All"),
    MenuItem(ID.DIRTREE_COLLAPSE_ALL, "&Collapse All"),
])
