import wx
from find_replace_dialog import FindReplaceDetails, FindReplaceDialog

class OutputCtrlMixin(object):

    def CanUndo(self):
        return self.output.CanUndo()

    def CanRedo(self):
        return self.output.CanRedo()

    def CanCut(self):
        return self.output.CanCut()

    def CanCopy(self):
        return self.output.CanCopy()

    def CanPaste(self):
        return self.output.CanPaste()

    def CanFindNext(self):
        return self.output.CanFindNext()

    def CanFindPrev(self):
        return self.output.CanFindPrev()

    def Undo(self):
        self.output.Undo()

    def Redo(self):
        self.output.Redo()

    def Cut(self):
        self.output.Cut()

    def Copy(self):
        self.output.Copy()

    def Paste(self):
        self.output.Paste()

    def SelectAll(self):
        self.output.SelectAll()

    def FindNext(self):
        self.output.FindNext()

    def FindPrev(self):
        self.output.FindPrev()

    def Find(self):
        self.output.Find()

    def GoToLine(self):
        self.output.GoToLine()

    def Unindent(self):
        self.output.Unindent()
