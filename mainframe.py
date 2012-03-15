import os, string, traceback, errno, shutil
import wx
from functools import wraps
from wx.lib.utils import AdjustRectToScreen

import aui
import async, fileutil, ID
from about_dialog import AboutDialog
from async import async_call, coroutine, queued_coroutine, managed, CoroutineManager, CoroutineQueue
from dialogs import dialogs
from commands_dialog import CommandsDialog
from dirtree import DirTreeCtrl, DirNode
from dirtree_filter import DirTreeFilter
from editor import Editor
from file_monitor import FileMonitor
from find_in_files_ctrl import FindInFilesCtrl
from find_in_files_dialog import FindInFilesDetails, FindInFilesDialog
from lru import LruQueue
from menu import MenuItem
from menu_defs import menubar
from new_project_dialog import NewProjectDialog
from settings import read_settings, write_settings
from styled_text_ctrl import StyledTextCtrl, MARKER_FIND, MARKER_ERROR
from shell import run_shell_command
from terminal_ctrl import TerminalCtrl
from util import frozen_window, frozen_or_hidden_window, is_text_file, new_id_range, shorten_path

def make_project_filename(project_root):
    return os.path.join(project_root, ".devo-project")

def make_session_filename(project_root):
    return os.path.join(project_root, ".devo-session")

class AppEnv(object):
    def __init__(self, mainframe):
        self._mainframe = mainframe

    def open_file(self, path, line=None, marker_type=None):
        return self._mainframe.OpenEditor(path, line, marker_type)

    def open_text(self, text):
        return self._mainframe.OpenEditorWithText(text)

    def open_static_text(self, title, text):
        return self._mainframe.OpenStaticEditor(title, text)

    def add_recent_file(self, path):
        self._mainframe.AddRecentFile(path)

    def clear_highlight(self, marker_type):
        self._mainframe.ClearHighlight(marker_type)

    def set_highlighted_file(self, path, line, marker_type):
        self._mainframe.SetHighlightedFile(path, line, marker_type)

    def get_file_to_save(self):
        if self._mainframe.project_root:
            return dialogs.get_file_to_save(self._mainframe, path=self._mainframe.project_root)
        else:
            return dialogs.get_file_to_save(self._mainframe, context="open")

    def add_monitor_path(self, path):
        self._mainframe.fmon.add_path(path)

    def remove_monitor_path(self, path):
        self._mainframe.fmon.remove_path(path)

    def updating_path(self, path):
        return self._mainframe.fmon.updating_path(path)

    @property
    def find_details(self):
        return self._mainframe.find_details

    @find_details.setter
    def find_details(self, find_details):
        self._mainframe.find_details = find_details

MAX_RECENT_FILES = 20

NB_STYLE = (aui.AUI_NB_CLOSE_ON_ALL_TABS  | aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT
           | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_WINDOWLIST_BUTTON
           | wx.BORDER_NONE)

class MainFrame(wx.Frame, wx.FileDropTarget):
    def __init__(self, project_root=None):
        display_rect = wx.Display(wx.Display.GetFromPoint((0, 0))).GetClientArea()
        width = min(display_rect.width, 1050)
        rect = wx.Rect(display_rect.width - width, display_rect.y, width, display_rect.height)

        wx.Frame.__init__(self, None, title="Devo", pos=rect.Position, size=rect.Size)
        wx.FileDropTarget.__init__(self)

        self.SetDropTarget(self)
        self.SetMenuBar(menubar.Create())
        self.CreateStatusBar(2)
        self.SetStatusWidths([200, -1])

        self.recent_file_first_id, self.recent_file_last_id = new_id_range(MAX_RECENT_FILES)
        self.shared_command_first_id, self.shared_command_last_id = new_id_range(100)
        self.project_command_first_id, self.project_command_last_id = new_id_range(100)
        self.project_first_id, self.project_last_id = new_id_range(100)

        self.config_dir = fileutil.get_user_config_dir("devo")
        self.settings_filename = os.path.join(self.config_dir, "devo.conf")
        self.project_filename = ""
        self.session_filename = ""

        self.settings = {}
        self.project = {}
        self.project_root = ""
        self.project_info = {}
        self.recent_files = LruQueue(maxlen=MAX_RECENT_FILES)

        self.cm = CoroutineManager()
        self.cq = CoroutineQueue()
        self.env = AppEnv(self)
        self.fmon = FileMonitor(self.OnFilesChanged)
        self.updated_paths = set()
        self.deleted_paths = set()
        self.reloading = False
        self.find_details = None
        self.find_in_files_details = None
        self.editor_focus = None
        self.editor_highlight = [None, None]

        agwFlags = aui.AUI_MGR_TRANSPARENT_HINT \
                 | aui.AUI_MGR_HINT_FADE \
                 | aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE
        self.manager = aui.AuiManager(self, agwFlags=agwFlags)
        self.notebook = aui.AuiNotebook(self, agwStyle=NB_STYLE)
        self.filter = DirTreeFilter()
        self.tree = DirTreeCtrl(self, self.env, filter=self.filter)
        self.terminal = TerminalCtrl(self, self.env)
        self.find_in_files = FindInFilesCtrl(self, self.env)

        self.manager.AddPane(self.tree,
            aui.AuiPaneInfo().Left().BestSize((220, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook,
            aui.AuiPaneInfo().CentrePane())
        self.manager.AddPane(self.terminal,
            aui.AuiPaneInfo().Hide().Bottom().BestSize((width, 180)).Caption("Terminal"))
        self.manager.AddPane(self.find_in_files,
            aui.AuiPaneInfo().Hide().Top().BestSize((width, 250)).Caption("Find in Files"))
        self.manager.Update()

        self.Startup(project_root)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_END_SESSION, self.OnClose)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        self.Bind(wx.EVT_CHILD_FOCUS, self.OnChildFocus)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_MIDDLE_UP, self.OnPageClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(aui.EVT_AUINOTEBOOK_BG_DCLICK, self.OnTabAreaDClick)

        self.Bind(wx.EVT_MENU, self.OnNewFile, id=ID.NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=ID.OPEN)
        self.Bind(wx.EVT_MENU, self.OnCloseFile, id=ID.CLOSE)
        self.Bind(wx.EVT_MENU, self.OnClose, id=ID.EXIT)
        self.Bind(wx.EVT_MENU, self.OnFindInFiles, id=ID.FIND_IN_FILES)
        self.Bind(wx.EVT_MENU_RANGE, self.OnRecentFile,
                  id=self.recent_file_first_id, id2=self.recent_file_last_id)

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
        self.Bind(wx.EVT_MENU, self.OnConfigureSharedCommands, id=ID.CONFIGURE_SHARED_COMMANDS)
        self.Bind(wx.EVT_MENU, self.OnConfigureProjectCommands, id=ID.CONFIGURE_PROJECT_COMMANDS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdate_ConfigureProjectCommands, id=ID.CONFIGURE_PROJECT_COMMANDS)

        self.Bind(wx.EVT_MENU_RANGE, self.OnSelectProject,
                  id=self.project_first_id, id2=self.project_last_id)

        self.Bind(wx.EVT_MENU_RANGE, self.OnSharedCommand,
                  id=self.shared_command_first_id, id2=self.shared_command_last_id)
        self.Bind(wx.EVT_MENU_RANGE, self.OnProjectCommand,
                  id=self.project_command_first_id, id2=self.project_command_last_id)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnUpdateUI_SharedCommand,
                  id=self.shared_command_first_id, id2=self.shared_command_last_id)
        self.Bind(wx.EVT_UPDATE_UI_RANGE, self.OnUpdateUI_ProjectCommand,
                  id=self.project_command_first_id, id2=self.project_command_last_id)

        self.Bind(wx.EVT_MENU, self.OnAboutBox, id=ID.ABOUT_BOX)

        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("GetModify"), id=ID.SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasMethod("SaveAs"), id=ID.SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditorTab, id=ID.CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanUndo"), id=ID.UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanRedo"), id=ID.REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanCut"), id=ID.CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanCopy"), id=ID.COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanPaste"), id=ID.PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasMethod("SelectAll"), id=ID.SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasMethod("Find"), id=ID.FIND)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanFindNext"), id=ID.FIND_NEXT)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanFindPrev"), id=ID.FIND_PREV)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasMethod("GoToLine"), id=ID.GO_TO_LINE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasMethod("Unindent"), id=ID.UNINDENT)

        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.CLOSE_PROJECT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.EDIT_PROJECT)

    @property
    def editors(self):
        for i in xrange(self.notebook.GetPageCount()):
            yield self.notebook.GetPage(i)

    @property
    def projects_sorted(self):
        return sorted(self.project_info.iteritems(), key=lambda x: x[1]["name"].lower())

    def GetMenuHooks(self):
        shared_commands = self.settings.get("commands", [])
        project_commands = self.project.get("commands", [])
        return {
            "shared_commands" : [
                MenuItem(i + self.shared_command_first_id, command["name"], command["accel"])
                for i, command in enumerate(shared_commands)
            ],
            "project_commands" : [
                MenuItem(i + self.project_command_first_id, command["name"], command["accel"])
                for i, command in enumerate(project_commands)
            ],
            "projects" : [
                MenuItem(i + self.project_first_id, p["name"])
                for i, (_, p) in enumerate(self.projects_sorted)
            ],
            "recent_files" : [
                MenuItem(i + self.recent_file_first_id, shorten_path(path))
                for i, path in enumerate(self.recent_files)
            ]
        }

    def UpdateMenuBar(self):
        with frozen_window(self):
            old_menubar = self.GetMenuBar()
            new_menubar = menubar.Create(self.GetMenuHooks())
            if wx.Platform == "__WXGTK__":
                self.SetMenuBar(None)
            self.SetMenuBar(new_menubar)
            if old_menubar:
                old_menubar.Destroy()

    def OnClose(self, evt):
        self.DoClose()

    @managed("cm")
    @coroutine
    def DoClose(self):
        if (yield self.SaveProject()):
            self.fmon.stop()
            if (yield self.SaveSettings()):
                self.Hide()
                wx.CallAfter(self._DoShutdown)
                return
        self.Show()
        self.fmon.Start()

    def _DoShutdown(self):
        self.fmon.stop()
        async.shutdown_scheduler()
        self.tree.Destroy()
        self.find_in_files.Destroy()
        self.Destroy()

    @managed("cm")
    @queued_coroutine("cq")
    def Startup(self, project_root=None):
        try:
            self.settings = (yield async_call(read_settings, self.settings_filename))
        except Exception:
            self.settings = {}
            try:
                backup_filename = self.settings_filename + ".bak"
                if not os.path.exists(backup_filename):
                    shutil.copy2(self.settings_filename, backup_filename)
            except OSError:
                pass

        self.recent_files = LruQueue(self.settings.get("recent_files", []), MAX_RECENT_FILES)

        for project_path in self.settings.get("projects", ()):
            try:
                project = (yield async_call(read_settings, make_project_filename(project_path)))
                project.setdefault("name", os.path.basename(project_path))
                self.project_info[project_path] = project
            except Exception:
                pass

        if "dialogs" in self.settings:
            dialogs.load_state(self.settings["dialogs"])

        success = True
        if project_root:
            success = (yield self.OpenProject(project_root))
        else:
            last_project = self.settings.get("last_project")
            if last_project:
                success = (yield self.OpenProject(last_project))
            else:
                yield self.OpenDefaultProject()

        if not success:
            yield self.OpenDefaultProject()

        yield self.SaveSettings()

    @managed("cm")
    @coroutine
    def SaveSettings(self):
        self.settings["projects"] = sorted(self.project_info)
        self.settings["last_project"] = self.project_root
        self.settings["recent_files"] = list(self.recent_files)
        self.settings["dialogs"] = dialogs.save_state()
        try:
            yield async_call(write_settings, self.settings_filename, self.settings)
            yield True
        except Exception, e:
            dialogs.error(self, "Error saving settings:\n\n%s" % e)
            yield False

    @managed("cm")
    @coroutine
    def SaveSession(self):
        session = {}
        session["dirtree"] = self.tree.SavePerspective()
        if self.notebook.GetPageCount() > 0:
            session["notebook"] = self.notebook.SavePerspective()
            session["editors"] = editors = []
            session["selection"] = self.notebook.GetSelection()
            for editor in self.editors:
                if editor.path and editor.modified:
                    if not (yield editor.TryClose()):
                        yield False
                editors.append(editor.SavePerspective())
        yield async_call(write_settings, self.session_filename, session)
        yield True

    @managed("cm")
    @coroutine
    def SaveProject(self):
        self.fmon.stop()
        try:
            if self.session_filename:
                try:
                    if not (yield self.SaveSession()):
                        yield False
                except Exception, e:
                    dialogs.error(self, "Error saving session:\n\n%s" % e)
                    yield False
            try:
                if self.project_filename:
                    yield async_call(write_settings, self.project_filename, self.project)
            except Exception, e:
                dialogs.error(self, "Error saving project:\n\n%s" % e)
                yield False
            yield True
        finally:
            self.fmon.start()

    @managed("cm")
    @coroutine
    def LoadSession(self):
        session = (yield async_call(read_settings, self.session_filename))

        with frozen_or_hidden_window(self.notebook):
            errors = []
            try:
                editors = []
                seen_paths = set()

                for p in session.get("editors", ()):
                    editor = self.NewEditor()
                    if "path" in p:
                        path = self.GetFullPath(p["path"])
                        if path in seen_paths:
                            editors.append((editor, None))
                            continue
                        seen_paths.add(path)
                    future = editor.LoadPerspective(p)
                    editors.append((editor, future))

                if "dirtree" in session:
                    self.tree.LoadPerspective(session["dirtree"])

                to_remove = []
                for i, (editor, future) in reversed(list(enumerate(editors))):
                    if future is None:
                        to_remove.append(i)
                    else:
                        try:
                            yield future
                        except Exception, e:
                            to_remove.add(i)
                            if not (isinstance(e, IOError) and e.errno == errno.ENOENT):
                                errors.append(e)
                errors.reverse()

                if "notebook" in session:
                    self.notebook.LoadPerspective(session["notebook"])

                if "selection" in session:
                    selection = session["selection"]
                    if 0 <= selection < self.notebook.GetPageCount():
                        self.notebook.SetSelection(selection)
                        self.notebook.GetPage(selection).SetFocus()

                # to_remove is already in reverse order
                for i in to_remove:
                    self.notebook.DeletePage(i)
            finally:
                if errors:
                    self.Show()
                    dialogs.error(self, "Errors loading session:\n\n%s" %
                        ("\n\n".join(str(e) for e in errors)))

    def DeleteAllPages(self):
        with frozen_or_hidden_window(self.notebook):
            for i in xrange(self.notebook.GetPageCount()-1, -1, -1):
                self.notebook.DeletePage(i)

    def StartFileMonitor(self):
        self.updated_paths.clear()
        self.deleted_paths.clear()
        self.fmon.start()

    def SetProject(self, project, project_root):
        project_root = os.path.realpath(project_root)
        self.project = project
        self.project_root = project_root
        self.project_filename = make_project_filename(project_root)
        self.session_filename = make_session_filename(project_root)
        project.setdefault("name", os.path.basename(project_root))
        self.project_info[project_root] = project

        self.DeleteAllPages()
        self.tree.SetTopLevel([DirNode(self.project_root)])
        self.UpdateMenuBar()
        self.SetTitle("Devo [%s]" % project["name"])
        self.StartFileMonitor()

    @managed("cm")
    @coroutine
    def OpenNewProject(self, project, project_root):
        if (yield self.SaveProject()):
            if os.path.exists(make_project_filename(project_root)):
                yield self.OpenProject(project_root, update=project)
            else:
                self.SetProject(project, project_root)
                yield self.SaveProject()
                yield self.SaveSettings()

    def _ShowLoadProjectError(self, exn, filename):
        self.Show()
        if isinstance(exn, IOError) and exn.errno == errno.ENOENT:
            dialogs.error(self, "Project file not found:\n\n" + filename)
        else:
            dialogs.error(self, "Error loading project:\n\n%s" % traceback.format_exc())

    @managed("cm")
    @coroutine
    def OpenProject(self, project_root, update={}):
        project_root = os.path.realpath(project_root)
        newly_added = project_root not in self.project_info
        if (yield self.SaveProject()):
            try:
                project = (yield async_call(read_settings, make_project_filename(project_root)))
                project.update(update)
                self.SetProject(project, project_root)
                try:
                    yield self.LoadSession()
                except IOError:
                    pass
                if newly_added:
                    yield self.SaveSettings()
                self.Show()
                yield True
            except Exception, e:
                self._ShowLoadProjectError(e, project_root)
                if project_root in self.project_info:
                    del self.project_info[project_root]
                    yield self.SaveSettings()
                    self.UpdateMenuBar()
                yield False
            finally:
                self.StartFileMonitor()

    @managed("cm")
    @coroutine
    def OpenDefaultProject(self):
        if (yield self.SaveProject()):
            self.project = {}
            self.project_root = ""
            self.project_filename = ""
            self.session_filename = os.path.join(self.config_dir, "session")

            self.DeleteAllPages()
            self.tree.SetTopLevel()
            try:
                yield self.LoadSession()
            except Exception:
                pass
            finally:
                self.Show()
                self.UpdateMenuBar()
                self.SetTitle("Devo")
                self.StartFileMonitor()

    def OnPaneClose(self, evt):
        window = evt.GetPane().window
        if window is self.find_in_files:
            self.ClearHighlight(MARKER_FIND)
        elif window is self.terminal:
            self.ClearHighlight(MARKER_ERROR)

    def OnPageClose(self, evt):
        evt.Veto()
        editor = self.notebook.GetPage(evt.GetSelection())
        self.ClosePage(editor)

    def ForgetEditor(self, editor):
        if editor is self.editor_focus:
            self.editor_focus = None
        for marker_type, editor_highlight in enumerate(self.editor_highlight):
            if editor is editor_highlight:
                self.editor_highlight[marker_type] = None

    @managed("cm")
    @coroutine
    def ClosePage(self, editor):
        if (yield editor.TryClose()):
            self.ForgetEditor(editor)
            with frozen_window(self.notebook):
                self.notebook.DeletePage(self.notebook.GetPageIndex(editor))
                if self.notebook.GetPageCount() == 0:
                    self.SetStatusText("", 0)
                    self.SetStatusText("", 1)

    def AddPage(self, win, index=None):
        if index is None:
            index = self.notebook.GetSelection() + 1
        self.notebook.InsertPage(index, win, win.title, select=True)
        win.sig_title_changed.bind(self.OnPageTitleChanged)
        win.sig_status_changed.bind(self.OnPageStatusChanged)
        win.SetFocus()

    def OnPageChanged(self, evt):
        editor = self.notebook.GetPage(evt.GetSelection())
        editor.SetFocus()
        self.SetStatusText(editor.status_text, 0)
        self.SetStatusText(editor.path or "Untitled", 1)

    def OnPageTitleChanged(self, win):
        i = self.notebook.GetPageIndex(win)
        if i != wx.NOT_FOUND:
            self.notebook.SetPageText(i, win.title)

    def OnPageStatusChanged(self, win):
        if win is self.notebook.GetCurrentPage():
            self.SetStatusText(win.status_text, 0)

    def OnTabAreaDClick(self, evt):
        self.NewEditor(index=self.notebook.GetPageCount())

    def NewEditor(self, index=None):
        with frozen_window(self.notebook):
            editor = Editor(self.notebook, self.env)
            self.AddPage(editor, index=index)
            return editor

    def FindEditor(self, path):
        for editor in self.editors:
            if editor.path == path:
                return editor

    def GetCurrentEditorTab(self):
        sel = self.notebook.GetSelection()
        if sel != wx.NOT_FOUND:
            return self.notebook.GetPage(sel)

    def GetFullPath(self, path):
        return os.path.realpath(os.path.join(self.project_root, path))

    def AddRecentFile(self, path):
        self.recent_files.add(self.GetFullPath(path))
        self.UpdateMenuBar()

    @managed("cm")
    @queued_coroutine("cq")
    def OpenEditor(self, path, line=None, marker_type=None):
        path = self.GetFullPath(path)

        try:
            if not (yield async_call(is_text_file, path)):
                if not dialogs.ask_open_binary(self, path):
                    yield False
        except IOError:
            pass

        editor = self.FindEditor(path)
        if editor:
            i = self.notebook.GetPageIndex(editor)
            if i != wx.NOT_FOUND:
                self.notebook.SetSelection(i)
            if line is not None:
                editor.SetCurrentLine(line - 1)
                if marker_type is not None:
                    self.SetHighlightedEditor(editor, line, marker_type)
            editor.SetFocus()
        else:
            editor = Editor(self.notebook, self.env, path)
            if not (yield editor.TryLoadFile(path)):
                editor.Destroy()
            else:
                with frozen_window(self.notebook):
                    self.AddPage(editor)
                    self.AddRecentFile(path)
                    if line is not None:
                        editor.SetCurrentLine(line - 1)
                        if marker_type is not None:
                            self.SetHighlightedEditor(editor, line, marker_type)
                    editor.SetFocus()

    def OpenEditorWithText(self, text):
        editor = self.NewEditor()
        editor.SetText(text)

    def OpenStaticEditor(self, title, text):
        editor = self.NewEditor()
        editor.SetStatic(title, text)

    def OnNewFile(self, evt):
        self.NewEditor()

    def OnOpenFile(self, evt):
        if self.project_root:
            path = dialogs.get_file_to_open(self, path=self.project_root)
        else:
            path = dialogs.get_file_to_open(self, context="open")
        if path:
            self.OpenEditor(path)

    def OnCloseFile(self, evt):
        editor = self.GetCurrentEditorTab()
        if editor:
            self.ClosePage(editor)

    def OnRecentFile(self, evt):
        index = evt.GetId() - self.recent_file_first_id
        if 0 <= index < len(self.recent_files):
            path = self.recent_files.access(index)
            self.OpenEditor(path)
            self.UpdateMenuBar()

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            self.OpenEditor(filename)
        return True

    def GetNewProject(self):
        dlg = NewProjectDialog(self)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                project_root = dlg.GetRoot()
                project = {"name": dlg.GetName()}
                return project, project_root
        finally:
            dlg.Destroy()
        return None, None

    def OnNewProject(self, evt):
        project, project_root = self.GetNewProject()
        if project:
            self.OpenNewProject(project, project_root)

    def OnOpenProject(self, evt):
        project_root = dialogs.get_directory(self, "Select Project Directory")
        if project_root:
            self.OpenProject(project_root)

    def OnCloseProject(self, evt):
        if self.project_filename:
            self.OpenDefaultProject()

    def OnEditProject(self, evt):
        pass

    def OnOrganiseProjects(self, evt):
        pass

    def ShowPane(self, window):
        pane = self.manager.GetPane(window)
        if not pane.IsShown():
            pane.Show()
            self.manager.Update()

    def GetCurrentSelection(self):
        if self.editor_focus:
            return self.editor_focus.GetSelectedText().strip().split("\n", 1)[0]
        return ""

    def ClearHighlight(self, marker_type):
        if self.editor_highlight[marker_type]:
            self.editor_highlight[marker_type].ClearHighlight(marker_type)
            self.editor_highlight[marker_type] = None

    def SetHighlightedEditor(self, editor, line, marker_type):
        self.ClearHighlight(marker_type)
        self.editor_highlight[marker_type] = editor
        editor.SetHighlightedLine(line - 1, marker_type)

    def SetHighlightedFile(self, path, line, marker_type):
        editor = self.FindEditor(self.GetFullPath(path))
        if editor:
            self.SetHighlightedEditor(editor, line, marker_type)

    def OnFindInFiles(self, evt):
        details = self.find_in_files_details
        selection = self.GetCurrentSelection()
        if selection:
            if not details:
                details = FindInFilesDetails()
            details.find = selection
            details.case = False
            details.regexp = False

        dlg = FindInFilesDialog(self, details)
        try:
            dlg.path = self.project_root
            if dlg.ShowModal() == wx.ID_OK:
                self.find_in_files_details = dlg.GetDetails()
                self.find_in_files.find(self.find_in_files_details, filter=self.filter)
                self.ShowPane(self.find_in_files)
        finally:
            dlg.Destroy()

    def OnConfigureSharedCommands(self, evt):
        dlg = CommandsDialog(self, self.settings.get("commands", []), title="Configure Shared Commands")
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.settings["commands"] = dlg.GetCommands()
                self.UpdateMenuBar()
                self.SaveSettings()
        finally:
            dlg.Destroy()

    def OnConfigureProjectCommands(self, evt):
        if not self.project_filename:
            return
        dlg = CommandsDialog(self, self.project.get("commands", []), title="Configure Project Commands")
        try:
            if dlg.ShowModal() == wx.ID_OK:
                self.project["commands"] = dlg.GetCommands()
                self.UpdateMenuBar()
                self.SaveProject()
        finally:
            dlg.Destroy()

    def OnUpdate_ConfigureProjectCommands(self, evt):
        evt.Enable(bool(self.project_filename))

    def RunCommand(self, cmdline, workdir=None, detach=False):
        workdir = workdir or None
        if detach:
            run_shell_command(cmdline, pipe_output=False, cwd=workdir)
        else:
            try:
                self.terminal.run(cmdline, cwd=workdir)
                self.ShowPane(self.terminal)
            except Exception, e:
                dialogs.error(self, "Error executing command:\n\n%s" % e)

    @managed("cm")
    @coroutine    
    def DoUserCommand(self, command):
        editor = self.GetCurrentEditorTab()
        current_file = editor.path if editor else ""
        env = dict(
            FILE = current_file,
            DIR = os.path.dirname(current_file),
            BASENAME = os.path.basename(current_file),
            PROJECT_DIR = self.project_root,
        )
        cmdline = string.Template(command["cmdline"]).safe_substitute(env)
        cmdline = cmdline.encode("utf-8")
        workdir = os.path.expanduser(command.get("workdir", ""))
        workdir = string.Template(workdir).safe_substitute(env)
        workdir = os.path.join(self.project_root, workdir)
        
        before = command.get("before", "")
        if before == "Save Current File":
            if editor and editor.path and editor.modified and not (yield editor.Save()):
                yield False
        elif before == "Save All Files":
            for editor in self.editors:
                if editor.path and editor.modified and not (yield editor.Save()):
                    yield False

        detach = command.get("detach", False)
        self.RunCommand(cmdline, workdir, detach)
        yield True

    def GetSharedCommandById(self, id):
        index = id - self.shared_command_first_id
        commands = self.settings.get("commands", [])
        if 0 <= index < len(commands):
            return commands[index]

    def GetProjectCommandById(self, id):
        index = id - self.project_command_first_id
        commands = self.project.get("commands", [])
        if 0 <= index < len(commands):
            return commands[index]

    def OnSharedCommand(self, evt):
        command = self.GetSharedCommandById(evt.GetId())
        if command:
            self.DoUserCommand(command)

    def OnProjectCommand(self, evt):
        command = self.GetProjectCommandById(evt.GetId())
        if command:
            self.DoUserCommand(command)

    def ShouldEnabledCommand(self, command):
        return bool(command and (not self.terminal.is_running or command.get("detach", False)))

    def OnUpdateUI_SharedCommand(self, evt):
        command = self.GetSharedCommandById(evt.GetId())
        evt.Enable(self.ShouldEnabledCommand(command))

    def OnUpdateUI_ProjectCommand(self, evt):
        command = self.GetProjectCommandById(evt.GetId())
        evt.Enable(self.ShouldEnabledCommand(command))

    def OnSelectProject(self, evt):
        index = evt.GetId() - self.project_first_id
        if 0 <= index < len(self.project_info):
            self.OpenProject(self.projects_sorted[index][0])

    def OnAboutBox(self, evt):
        dlg = AboutDialog(self, self.env)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

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
                    if dialogs.ask_reload(self, os.path.basename(editor.path)):
                        yield editor.Reload()
                    else:
                        editor.SetModified()
                for editor in reversed(to_unload):
                    if os.path.exists(editor.path):
                        if dialogs.ask_reload(self, os.path.basename(editor.path)):
                            yield editor.Reload()                        
                        else:
                            editor.SetModified()
                    else:
                        if dialogs.ask_unload(self, os.path.basename(editor.path)):
                            yield self.ClosePage(editor)
                        else:
                            editor.SetModified()
            finally:
                self.reloading = False
            if self.updated_paths or self.deleted_paths:
                self.NotifyUpdatedPaths()

    def TryNotifyUpdatedPaths(self):
        if (self.updated_paths or self.deleted_paths) and not self.reloading:
            mouse = wx.GetMouseState()
            if mouse.LeftDown() or mouse.MiddleDown() or mouse.RightDown():
                wx.CallLater(500, self.TryNotifyUpdatedPaths)
            else:
                self.NotifyUpdatedPaths()

    def OnActivate(self, evt):
        if evt.GetActive():
            self.TryNotifyUpdatedPaths()

    def OnChildFocus(self, evt):
        focus = wx.Window.FindFocus()
        if focus is self:
            return
        while focus:
            if isinstance(focus, StyledTextCtrl):
                self.editor_focus = focus
                return
            focus = focus.Parent
        self.editor_focus = None

    def OnFilesChanged(self, updated_paths, deleted_paths):
        for path in updated_paths:
            self.updated_paths.add(path)
        for path in deleted_paths:
            self.deleted_paths.add(path)
        self.updated_paths.difference_update(self.deleted_paths)
        if self.IsActive():
            self.TryNotifyUpdatedPaths()

    def IsEditorFocused(self, editor):
        return editor is self.editor_focus

    def EditorAction(self, method):
        def handler(evt):
            editor = self.editor_focus
            if editor:
                return getattr(editor, method)()
        return handler

    def EditorUpdateUI(self, method):
        def handler(evt):
            editor = self.editor_focus
            if editor and hasattr(editor, method):
                evt.Enable(getattr(editor, method)())
            else:
                evt.Enable(False)
        return handler

    def UpdateUI_HasEditorTab(self, evt):
        evt.Enable(self.GetCurrentEditorTab() is not None)

    def UpdateUI_EditorHasMethod(self, method):
        def handler(evt):
            editor = self.editor_focus
            evt.Enable(bool(editor and hasattr(editor, method)))
        return handler

    def UpdateUI_ProjectIsOpen(self, evt):
        evt.Enable(bool(self.project_root))
