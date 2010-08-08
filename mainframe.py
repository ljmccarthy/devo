import sys, os, traceback, errno, wx
from functools import wraps
from wx.lib.agw import aui
from wx.lib.utils import AdjustRectToScreen

import dialogs, fileutil, ID
from async_wx import async_call, coroutine, managed, CoroutineManager, scheduler
from dirtree import DirTreeCtrl, DirNode
from editor import Editor
from menu_defs import menubar
from project import read_project, write_project
from util import frozen_window, is_text_file

from new_project_dialog import NewProjectDialog

class AppEnv(object):
    def __init__(self, mainframe):
        self.mainframe = mainframe

    @coroutine
    def OpenFile(self, path):
        if not (yield async_call(is_text_file, path)):
            dialogs.error(self.mainframe, "Selected file is not a text file:\n\n%s" % path)
        else:
            yield self.mainframe.OpenEditor(path)

    def NewEditor(self):
        self.mainframe.NewEditor()

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

        self.config_dir = fileutil.get_user_config_dir("devo")
        self.project = None

        self.cm = CoroutineManager()
        self.env = AppEnv(self)

        self.manager = aui.AuiManager(self)
        self.notebook = aui.AuiNotebook(self, style=NB_STYLE)
        self.tree = DirTreeCtrl(self, self.env)

        self.manager.AddPane(self.tree,
            aui.AuiPaneInfo().Left().BestSize(wx.Size(220, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook,
            aui.AuiPaneInfo().CentrePane())
        self.manager.Update()

        self.OpenDefaultProject()

        self.Bind(wx.EVT_CLOSE, self.OnClose)
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
        self.Bind(wx.EVT_MENU, self.EditorAction("GoToLine"), id=ID.GO_TO_LINE)
        self.Bind(wx.EVT_MENU, self.EditorAction("Unindent"), id=ID.UNINDENT)

        self.Bind(wx.EVT_MENU, self.OnNewProject, id=ID.NEW_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnOpenProject, id=ID.OPEN_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnCloseProject, id=ID.CLOSE_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnEditProject, id=ID.EDIT_PROJECT)
        self.Bind(wx.EVT_MENU, self.OnOrganiseProjects, id=ID.ORGANISE_PROJECTS)

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
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.GO_TO_LINE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID.UNINDENT)

        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.CLOSE_PROJECT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_ProjectIsOpen, id=ID.EDIT_PROJECT)

    @property
    def editors(self):
        for i in xrange(self.notebook.GetPageCount()):
            yield self.notebook.GetPage(i)

    def OnClose(self, evt):
        self.DoClose()

    @managed("cm")
    @coroutine
    def DoClose(self):
        self.Hide()
        if not self.project or (yield self.SaveSession()):
            wx.CallAfter(self._DoShutdown)
        else:
            self.Show()

    def _DoShutdown(self):
        scheduler.shutdown()
        self.Destroy()

    @managed("cm")
    @coroutine
    def SaveSession(self):
        try:
            session = {}
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
        self.notebook.Freeze()
        try:
            editors = []
            if "editors" in session:
                for p in session["editors"]:
                    editor = self.NewEditor()
                    future = editor.LoadPerspective(p)
                    editors.append((editor, future))
                if "notebook" in session and session["editors"]:
                    self.notebook.LoadPerspective(session["notebook"])
            if "selection" in session:
                selection = session["selection"]
                if 0 <= selection < self.notebook.GetPageCount():
                    self.notebook.SetSelection(selection)
                    self.notebook.GetPage(selection).SetFocus()
            if "dirtree" in session:
                self.tree.LoadPerspective(session["dirtree"])
            for i, (editor, future) in reversed(list(enumerate(editors))):
                try:
                    if future:
                        yield future
                except Exception, e:
                    if not (isinstance(e, IOError) and e.errno == errno.ENOENT):
                        errors.append(e)
                    self.notebook.DeletePage(i)
            errors.reverse()
        finally:
            self.notebook.Thaw()
            self.notebook.Show()
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

    @managed("cm")
    @coroutine
    def LoadProject(self, project):
        if not self.project or (yield self.SaveSession()):
            old_project = self.project
            self.SetProject(project)
            try:
                self.LoadSession(project.session)
            except Exception:
                if old_project:
                    self.SetProject(old_project)
                    self.LoadSession(old_project.session)
                raise

    @managed("cm")
    @coroutine
    def OpenNewProject(self, project):
        if not self.project or (yield self.SaveSession()):
            self.SetProject(project)

    @managed("cm")
    @coroutine
    def OpenProject(self, filename, rootdir):
        try:
            project = (yield async_call(read_project, filename, rootdir))
            yield self.LoadProject(project)
        except Exception, e:
            if isinstance(e, IOError) and e.errno == errno.ENOENT:
                dialogs.error(self, "Project file not found:\n\n" + rootdir)
            else:
                dialogs.error(self, "Error loading session:\n\n%s" % traceback.format_exc())

    def OpenDefaultProject(self):
        return self.OpenProject(os.path.join(self.config_dir, "session"), "")

    def OnPageClose(self, evt):
        evt.Veto()
        editor = self.notebook.GetPage(evt.GetSelection())
        self.ClosePage(editor)

    @managed("cm")
    @coroutine
    def ClosePage(self, editor):
        if (yield editor.TryClose()):
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
        editor = Editor(self.notebook, self.env)      
        with frozen_window(self.notebook):
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
            self.OpenProject(os.path.join(rootdir, ".devo-session"), rootdir)

    def OnCloseProject(self, evt):
        if self.project:
            self.OpenDefaultProject()

    def OnEditProject(self, evt):
        pass

    def OnOrganiseProjects(self, evt):
        pass

    def EditorAction(self, method):
        def handler(evt):
            editor = self.GetCurrentEditor()
            if editor is not None:
                return getattr(editor, method)()
        return handler

    def EditorUpdateUI(self, method):
        def handler(evt):
            editor = self.GetCurrentEditor()
            if editor is not None:
                evt.Enable(getattr(editor, method)())
            else:
                evt.Enable(False)
        return handler

    def UpdateUI_HasEditor(self, evt):
        evt.Enable(self.GetCurrentEditor() is not None)

    def UpdateUI_EditorHasSelection(self, evt):
        editor = self.GetCurrentEditor()
        if editor is not None:
            start, end = editor.GetSelection()
            evt.Enable(start != end)
        else:
            evt.Enable(False)

    def UpdateUI_ProjectIsOpen(self, evt):
        evt.Enable(bool(self.project and self.project.rootdir))
