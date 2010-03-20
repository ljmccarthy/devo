import sys, os, traceback, wx, cPickle as pickle
from functools import wraps
from wx.lib.agw import aui
from wx.lib.utils import AdjustRectToScreen

import dialogs, fileutil
from async_wx import async_call, coroutine, managed, CoroutineManager
from dirtree import DirTreeCtrl
from editor import Editor
from menu_defs import *
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

class MainFrame(wx.Frame):
    def __init__(self):
        rect = AdjustRectToScreen(wx.Rect(0, 0, 1000, 1500))
        if wx.Platform == "__WXGTK__":
            size = rect.Size
            pos = (0, 0)
        else:
            size = (rect.width, rect.height - 50)
            pos = (25, 25)

        wx.Frame.__init__(self, None, title="Devo", pos=pos, size=size)
        self.SetMenuBar(menubar.Create())

        self.config_dir = fileutil.get_user_config_dir("devo")
        self.session_file = os.path.join(self.config_dir, "session")

        self.cm = CoroutineManager()
        self.env = AppEnv(self)

        self.manager = aui.AuiManager(self)
        nbstyle = (aui.AUI_NB_CLOSE_ON_ALL_TABS  | aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT
                  | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | wx.BORDER_NONE)
        self.notebook = aui.AuiNotebook(self, style=nbstyle)
        self.tree = DirTreeCtrl(self, self.env)

        self.manager.AddPane(self.tree,
            aui.AuiPaneInfo().Left().BestSize(wx.Size(200, -1)).CaptionVisible(False))
        self.manager.AddPane(self.notebook,
            aui.AuiPaneInfo().CentrePane())
        self.manager.Update()

        self.LoadSession()

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        self.Bind(wx.EVT_MENU, self.OnNewFile, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnCloseFile, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.EditorAction("Save"), id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.EditorAction("SaveAs"), id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.EditorAction("Undo"), id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.EditorAction("Redo"), id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.EditorAction("Cut"), id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.EditorAction("Copy"), id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.EditorAction("Paste"), id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.EditorAction("SelectAll"), id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.EditorAction("Find"), id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.EditorAction("FindSelected"), id=ID_FIND_SELECTED)
        self.Bind(wx.EVT_MENU, self.EditorAction("FindNext"), id=ID_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.EditorAction("GoToLine"), id=ID_GO_TO_LINE)
        self.Bind(wx.EVT_MENU, self.EditorAction("Unindent"), id=ID_UNINDENT)

        self.Bind(wx.EVT_MENU, self.OnNewProject, id=ID_NEW_PROJECT)

        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("GetModify"), id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanUndo"), id=wx.ID_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanRedo"), id=wx.ID_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasSelection, id=wx.ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasSelection, id=wx.ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanPaste"), id=wx.ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=wx.ID_FIND)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_EditorHasSelection, id=ID_FIND_SELECTED)
        self.Bind(wx.EVT_UPDATE_UI, self.EditorUpdateUI("CanFindNext"), id=ID_FIND_NEXT)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID_GO_TO_LINE)
        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUI_HasEditor, id=ID_UNINDENT)

    @property
    def editors(self):
        for i in xrange(self.notebook.GetPageCount()):
            yield self.notebook.GetPage(i)

    def OnClose(self, evt):
        self.DoClose()

    @managed("cm")
    @coroutine
    def DoClose(self):
        if (yield self.SaveSession()):
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
            data = pickle.dumps(session, pickle.HIGHEST_PROTOCOL)
            fileutil.mkpath(self.config_dir)
            yield async_call(fileutil.atomic_write_file, self.session_file, data)
            yield True
        except Exception, e:
            dialogs.error(self, "Error saving session:\n\n%s" % e)
            yield False

    @managed("cm")
    @coroutine
    def LoadSession(self):
        try:
            with (yield async_call(open, self.session_file, "rb")) as f:
                session = pickle.loads((yield async_call(f.read)))
            if "editors" in session:
                for p in session["editors"]:
                    editor = self.NewEditor()
                    yield editor.LoadPerspective(p)
                if "notebook" in session and session["editors"]:
                    self.notebook.LoadPerspective(session["notebook"])
            if "dirtree" in session:
                self.tree.LoadPerspective(session["dirtree"])
            if "selection" in session:
                selection = session["selection"]
                if 0 <= selection < self.notebook.GetPageCount():
                    self.notebook.SetSelection(selection)
                    self.notebook.GetPage(selection).SetFocus()
        except (IOError, OSError):
            pass
        except Exception, e:
            dialogs.error(self, "Error loading session:\n\n%s" % traceback.format_exc())
        self.Show()

    @managed("cm")
    @coroutine
    def CloseSession(self, shutdown=False):
        for editor in self.editors:
            try:
                if not (yield editor.TryClose()):
                    yield False
            except Exception, e:
                dialogs.error(self, str(e))
                yield False
        if shutdown:
            self.Destroy()
        else:
            with frozen_window(self):
                for i in xrange(self.notebook.GetPageCount()-1, -1, -1):
                    self.notebook.DeletePage(i)
        yield True

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
            try:
                yield editor.LoadFile(realpath)
            except Exception, e:
                dialogs.error(self, "Error opening file:\n\n%s" % e)
                editor.Destroy()
            else:
                with frozen_window(self.notebook):
                    self.AddPage(editor)

    def OnNewFile(self, evt):
        self.NewEditor()

    def OnOpenFile(self, evt):
        path = dialogs.get_file_to_open(self)
        if path:
            self.OpenEditor(path)

    @with_current_editor
    def OnCloseFile(self, editor, evt):
        self.ClosePage(editor)

    def OnNewProject(self, evt):
        dlg = NewProjectDialog(self)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()

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
