import sys, os, string, traceback, errno, wx
from functools import wraps
from wx.lib.agw import aui
from wx.lib.utils import AdjustRectToScreen

import async, fileutil, ID
from async import async_call, coroutine, managed, CoroutineManager
from dialogs import dialogs
from commands_dialog import CommandsDialog
from dirtree import DirTreeCtrl, DirNode
from editor import Editor
from file_monitor import FileMonitor
from find_replace_dialog import FindReplaceDetails
from menu import MenuItem
from menu_defs import menubar
from project import read_project, write_project
from terminal_ctrl import TerminalCtrl
from util import frozen_window, is_text_file

from new_project_dialog import NewProjectDialog

class AppEnv(object):
    def __init__(self, mainframe):
        self._mainframe = mainframe

    @coroutine
    def OpenFile(self, path):
        if not (yield async_call(is_text_file, path)):
            dialogs.error(self._mainframe, "Selected file is not a text file:\n\n%s" % path)
        else:
            yield self._mainframe.OpenEditor(path)

    def NewEditor(self):
        self._mainframe.NewEditor()

    def AddMonitorPath(self, path):
        self._mainframe.fmon.AddPath(path)

    def RemoveMonitorPath(self, path):
        self._mainframe.fmon.RemovePath(path)

    @property
    def find_details(self):
        return self._mainframe.find_details

    @find_details.setter
    def find_details(self, find_details):
        self._mainframe.find_details = find_details

def with_current_editor(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        editor = self.GetCurrentEditor()
        if editor is not None:
            return method(self, editor, *args, **kwargs)
    return wrapper

NB_STYLE = (aui.AUI_NB_CLOSE_ON_ALL_TABS  | aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT
           | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | wx.BORDER_NONE)

class MainFrame(wx.Frame, wx.FileDropTarget):
    def __init__(self):
        rect = AdjustRectToScreen(wx.Rect(0, 0, 1050, 1500))
        if wx.Platform == "__WXGTK__":
            size = rect.Size
            pos = (0, 0)
        else:
            size = (rect.width, rect.height - 50)
            pos = (25, 25)

        wx.Frame.__init__(self, None, title="Devo", pos=pos, size=size)
        wx.FileDropTarget.__init__(self)

        self.SetDropTarget(self)
        self.SetMenuBar(menubar.Create())

        self.user_first_id = wx.NewId()
        self.user_last_id = self.user_first_id + 1000
        wx.RegisterId(self.user_last_id)

        self.config_dir = fileutil.get_user_config_dir("devo")
        self.project = None

        self.cm = CoroutineManager()
        self.env = AppEnv(self)
        self.fmon = FileMonitor(self.OnFilesChanged)
        self.updated_paths = set()
        self.deleted_paths = set()
        self.reloading = False
        self.find_details = FindReplaceDetails("", "")
        self.editor_focus = None

        self.manager = aui.AuiManager(self)
        self.notebook = aui.AuiNotebook(self, style=NB_STYLE)
        self.tree = DirTreeCtrl(self, self.env)
        self.terminal = TerminalCtrl(self)

        self.manager.AddPane(self.tree,
            aui.AuiPaneInfo().Left().BestSize((220, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook,
            aui.AuiPaneInfo().CentrePane())
        self.manager.AddPane(self.terminal,
            aui.AuiPaneInfo().Hide().Bottom().BestSize((-1, 200)).Caption("Terminal"))
        self.manager.Update()

        self.OpenDefaultProject()

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        self.Bind(wx.EVT_MENU, self.OnNewFile, id=ID.NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=ID.OPEN)
        self.Bind(wx.EVT_MENU, self.OnCloseFile, id=ID.CLOSE)
        self.Bind(wx.EVT_MENU, self.OnClose, id=ID.EXIT)

        self.Bind(wx.EVT_MENU, self.EditorAction("Save"), id=ID.SAVE)
        self.Bind(wx.EVT_MENU, self.EditorAction("SaveAs"), id=ID.SAVEAS)
        self.Bind(wx.EVT_MENU, self.EditorAction("Undo"), id=ID.UNDO)
        self.Bind(wx.EVT_MENU, self.EditorAction("Redo"), id=ID.REDO)
        self.Bind(wx.EVT_MENU, self.EditorAction("Cut"), id=ID.CUT)
        self.Bind(wx.EVT_MENU, self.EditorAction("Copy"), id=ID.COPY)
        self.Bind(wx.EVT_MENU, self.EditorAction("Paste"), id=ID.PASTE)
        self.Bind(wx.EVT_MENU, self.EditorAction("SelectAll"), id=ID.SELECTALL)
        self.Bind(wx.EVT_MENU, self.EditorAction("Find"), id=ID.FIND)
        self.Bind(wx.EVT_MENU, self.EditorAction("FindNext"), id=ID.FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.EditorAction("FindPrev"), id=ID.FIND_PREV)
        self.Bind(wx.EVT_MENU, self.EditorAction("GoToLine"), id=ID.GO_TO_LINE)
        self.Bind(wx.EVT_MENU, self.EditorAction("Unindent"), id=ID.UNINDENT)

        self.Bind(wx.EVT_MENU, self.OnNewProject, id=ID.NEW_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnOpenProject, id=ID.OPEN_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnCloseProject, id=ID.CLOSE_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnEditProject, id=ID.EDIT_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnOrganiseProjects, id=ID.ORGANISE_PROJECTS)
        self.Bind(wx.EVT_MENU, self.OnConfigureCommands, id=ID.CONFIGURE_COMMANDS)
        self.Bind(wx.EVT_MENU_RANGE, self.OnUserCommand,
                  id=self.user_first_id, id2=self.user_last_id)

        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("GetModify"), id=ID.SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanUndo"), id=ID.UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanRedo"), id=ID.REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasSelection, id=ID.CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasSelection, id=ID.COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanPaste"), id=ID.PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.FIND)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanFindNext"), id=ID.FIND_NEXT)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanFindPrev"), id=ID.FIND_PREV)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.GO_TO_LINE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.UNINDENT)

        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.CLOSE_PROJECT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.EDIT_PROJECT)

    @property
    def editors(self):
        for i in xrange(self.notebook.GetPageCount()):
            yield self.notebook.GetPage(i)

    def GetMenuHooks(self):
        return {
            "commands" : [MenuItem(i + self.user_first_id, command["name"], command["accel"])
                          for i, command in enumerate(self.project.commands)],
        }

    def UpdateMenuBar(self):
        with frozen_window(self):
            old_menubar = self.GetMenuBar()
            new_menubar = menubar.Create(self.GetMenuHooks())
            self.SetMenuBar(new_menubar)
            if old_menubar:
                old_menubar.Destroy()

    def OnClose(self, evt):
        self.DoClose()

    @managed("cm")
    @coroutine
    def DoClose(self):
        if not self.project or (yield self.SaveSession()):
            wx.CallAfter(self._DoShutdown)
        else:
            self.Show()

    def _DoShutdown(self):
        self.Hide()
        self.fmon.Stop()
        async.shutdown_scheduler()
        self.Destroy()

    @managed("cm")
    @coroutine
    def SaveSession(self):
        try:
            session = {}
            session["dialogs"] = dialogs.save_state()
            session["dirtree"] = self.tree.SavePerspective()
            if self.notebook.GetPageCount() > 0:
                session["notebook"] = self.notebook.SavePerspective()
                session["editors"] = editors = []
                session["selection"] = self.notebook.GetSelection()
            for editor in self.editors:
                if editor.path and editor.changed:
                    if not (yield editor.TryClose()):
                        yield False
                editors.append(editor.SavePerspective())
            self.project.session = session
            yield async_call(write_project, self.project)
            yield True
        except Exception, e:
            dialogs.error(self, "Error saving session:\n\n%s" % e)
            yield False

    @managed("cm")
    @coroutine
    def LoadSession(self, session):
        errors = []
        if wx.Platform == "__WXGTK__":
            self.notebook.Hide()
        else:
            self.notebook.Freeze()
        try:
            if "dialogs" in session:
                dialogs.load_state(session["dialogs"])

            editors = []
            if "editors" in session:
                for p in session["editors"]:
                    editor = self.NewEditor()
                    future = editor.LoadPerspective(p)
                    editors.append((editor, future))

            if "dirtree" in session:
                self.tree.LoadPerspective(session["dirtree"])

            for i, (editor, future) in reversed(list(enumerate(editors))):
                try:
                    yield future
                except Exception, e:
                    if not (isinstance(e, IOError) and e.errno == errno.ENOENT):
                        errors.append(e)
                    self.notebook.DeletePage(i)
            errors.reverse()

            if "notebook" in session:
                self.notebook.LoadPerspective(session["notebook"])

            if "selection" in session:
                selection = session["selection"]
                if 0 <= selection < self.notebook.GetPageCount():
                    self.notebook.SetSelection(selection)
                    self.notebook.GetPage(selection).SetFocus()
        finally:
            if wx.Platform == "__WXGTK__":
                self.notebook.Show()
            else:
                self.notebook.Thaw()
            self.Show()
            if errors:
                dialogs.error(self, "Errors loading session:\n\n%s" %
                    ("\n\n".join(str(e) for e in errors)))

    def DeleteAllPages(self):
        if wx.Platform == "__WXGTK__":
            self.notebook.Hide()
        try:
            self.notebook.Freeze()
            for i in xrange(self.notebook.GetPageCount()-1, -1, -1):
                self.notebook.DeletePage(i)
        finally:
            self.notebook.Thaw()
            self.notebook.Show()

    def SetProject(self, project):
        self.DeleteAllPages()
        if project and project.rootdir:
            self.tree.SetTopLevel([DirNode(project.rootdir)])
        else:
            self.tree.SetTopLevel()
        self.project = project
        self.UpdateMenuBar()

    @managed("cm")
    @coroutine
    def LoadProject(self, project):
        if not self.project or (yield self.SaveSession()):
            old_project = self.project
            self.SetProject(project)
            try:
                yield self.LoadSession(project.session)
            except Exception:
                if old_project:
                    self.SetProject(old_project)
                    yield self.LoadSession(old_project.session)
                raise

    @managed("cm")
    @coroutine
    def OpenNewProject(self, project):
        if not self.project or (yield self.SaveSession()):
            self.SetProject(project)

    @managed("cm")
    @coroutine
    def OpenProject(self, filename):
        try:
            project = (yield async_call(read_project, filename))
            yield self.LoadProject(project)
        except Exception, e:
            if isinstance(e, IOError) and e.errno == errno.ENOENT:
                dialogs.error(self, "Project file not found:\n\n" + filename)
            else:
                dialogs.error(self, "Error loading session:\n\n%s" % traceback.format_exc())

    def OpenDefaultProject(self):
        return self.OpenProject(os.path.join(self.config_dir, "session"))

    def OnPageClose(self, evt):
        evt.Veto()
        editor = self.notebook.GetPage(evt.GetSelection())
        self.ClosePage(editor)

    @managed("cm")
    @coroutine
    def ClosePage(self, editor):
        if (yield editor.TryClose()):
            if editor is self.editor_focus:
                self.editor_focus = None
            with frozen_window(self.notebook):
                self.notebook.DeletePage(self.notebook.GetPageIndex(editor))

    def AddPage(self, win):
        i = self.notebook.GetSelection() + 1
        self.notebook.InsertPage(i, win, win.title, select=True)
        win.sig_title_changed.bind(self.OnPageTitleChanged)
        win.SetFocus()

    def OnPageChanged(self, evt):
        editor = self.notebook.GetPage(evt.GetSelection())
        editor.SetFocus()

    def OnPageTitleChanged(self, win):
        i = self.notebook.GetPageIndex(win)
        if i != wx.NOT_FOUND:
            self.notebook.SetPageText(i, win.title)

    def NewEditor(self):
        with frozen_window(self.notebook):
            editor = Editor(self.notebook, self.env)
            self.AddPage(editor)
            return editor

    def FindEditor(self, path):
        for editor in self.editors:
            if editor.path == path:
                return editor

    def GetCurrentEditor(self):
        sel = self.notebook.GetSelection()
        if sel != wx.NOT_FOUND:
            return self.notebook.GetPage(sel)

    @managed("cm")
    @coroutine
    def OpenEditor(self, path):
        realpath = os.path.realpath(path)
        editor = self.FindEditor(realpath)
        if editor is not None:
            i = self.notebook.GetPageIndex(editor)
            if i != wx.NOT_FOUND:
                self.notebook.SetSelection(i)
        else:
            editor = Editor(self.notebook, self.env, realpath)
            if not (yield editor.TryLoadFile(realpath)):
                editor.Destroy()
            else:
                with frozen_window(self.notebook):
                    self.AddPage(editor)

    def OnNewFile(self, evt):
        self.NewEditor()

    def OnOpenFile(self, evt):
        path = dialogs.get_file_to_open(self, context="open")
        if path:
            self.OpenEditor(path)

    @with_current_editor
    def OnCloseFile(self, editor, evt):
        self.ClosePage(editor)

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            self.OpenEditor(filename)

    def GetNewProject(self):
        dlg = NewProjectDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetProject()
        finally:
            dlg.Destroy()

    def OnNewProject(self, evt):
        project = self.GetNewProject()
        if project:
            self.OpenNewProject(project)

    def OnOpenProject(self, evt):
        rootdir = dialogs.get_directory(self, "Select Project Directory")
        if rootdir:
            self.OpenProject(os.path.join(rootdir, ".devo-session"))

    def OnCloseProject(self, evt):
        if self.project:
            self.OpenDefaultProject()

    def OnEditProject(self, evt):
        pass

    def OnOrganiseProjects(self, evt):
        pass

    def OnConfigureCommands(self, evt):
        dlg = CommandsDialog(self, self.project.commands)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.project.commands = dlg.GetCommands()
                self.UpdateMenuBar()
        finally:
            dlg.Destroy()

    def ShowTerminal(self):
        pane = self.manager.GetPane(self.terminal)
        if not pane.IsShown():
            pane.Show()
            self.manager.Update()

    def RunCommand(self, cmdline):
        self.terminal.run(cmdline, cwd = self.project.rootdir or None)
        self.ShowTerminal()

    def OnUserCommand(self, evt):
        index = evt.GetId() - self.user_first_id
        if 0 <= index < len(self.project.commands):
            command = self.project.commands[index]
            editor = self.GetCurrentEditor()
            current_file = editor.path if editor else ""
            cmdline = string.Template(command["cmdline"]).safe_substitute(
                CURRENT_FILE = current_file,
                CURRENT_DIR = os.path.dirname(current_file),
                CURRENT_BASENAME = os.path.basename(current_file),
                PROJECT_ROOT = self.project.rootdir,
            )
            self.RunCommand(cmdline)

    @managed("cm")
    @coroutine
    def NotifyUpdatedPaths(self):
        if (self.updated_paths or self.deleted_paths) and not self.reloading:
            try:
                self.reloading = True
                to_reload = []
                to_unload = []
                for editor in self.editors:
                    if editor.path in self.updated_paths:
                        to_reload.append(editor)
                    elif editor.path in self.deleted_paths:
                        to_unload.append(editor)
                self.updated_paths.clear()
                self.deleted_paths.clear()
                for editor in to_reload:
                    self.notebook.SetSelection(self.notebook.GetPageIndex(editor))
                    if dialogs.ask_reload(self, os.path.basename(editor.path)):
                        yield editor.Reload()
                for editor in reversed(to_unload):
                    self.notebook.SetSelection(self.notebook.GetPageIndex(editor))
                    if dialogs.ask_unload(self, os.path.basename(editor.path)):
                        yield self.ClosePage(editor)
                    else:
                        # Mark as modified
                        editor.AppendText(" ")
                        editor.SetSavePoint()
                        editor.Undo()
            finally:
                self.reloading = False
            if self.updated_paths or self.deleted_paths:
                self.NotifyUpdatedPaths()

    def OnActivate(self, evt):
        self.NotifyUpdatedPaths()

    def OnChildFocus(self, evt):
        focus = wx.Window.FindFocus()
        self.editor_focus = focus if isinstance(focus, Editor) else None

    def OnFilesChanged(self, updated_paths, deleted_paths):
        for path in updated_paths:
            self.updated_paths.add(path)
        for path in deleted_paths:
            self.deleted_paths.add(path)
        self.updated_paths.difference_update(self.deleted_paths)
        if self.IsActive():
            self.NotifyUpdatedPaths()

    def IsEditorFocused(self, editor):
        return editor is self.editor_focus

    def EditorAction(self, method):
        def handler(evt):
            editor = self.GetCurrentEditor()
            if editor is not None and self.IsEditorFocused(editor):
                return getattr(editor, method)()
        return handler

    def EditorUpdateUI(self, method):
        def handler(evt):
            editor = self.GetCurrentEditor()
            if editor is not None and self.IsEditorFocused(editor):
                evt.Enable(getattr(editor, method)())
            else:
                evt.Enable(False)
        return handler

    def UpdateUI_HasEditor(self, evt):
        editor = self.GetCurrentEditor()
        evt.Enable(editor is not None and self.IsEditorFocused(editor))

    def UpdateUI_EditorHasSelection(self, evt):
        editor = self.GetCurrentEditor()
        if editor is not None and self.IsEditorFocused(editor):
            start, end = editor.GetSelection()
            evt.Enable(start != end)
        else:
            evt.Enable(False)

    def UpdateUI_ProjectIsOpen(self, evt):
        evt.Enable(bool(self.project and self.project.rootdir))
