# Monkey patches for wxPython

import wx
import aui

if wx.VERSION < (2,9):
    wx.MouseState.LeftIsDown = wx.MouseState.LeftDown
    wx.MouseState.MiddleIsDown = wx.MouseState.MiddleDown
    wx.MouseState.RightIsDown = wx.MouseState.RightDown

def AuiTabContainer_ButtonHitTest(self, x, y, state_flags=aui.AUI_BUTTON_STATE_HIDDEN|aui.AUI_BUTTON_STATE_DISABLED):
    if not self._rect.Contains((x,y)):
        return None

    for button in self._buttons:
        if button.rect.Contains((x,y)) and \
           (button.cur_state & state_flags) == 0:
            return button

    for button in self._tab_close_buttons:
        if button.rect.Contains((x,y)) and \
           (button.cur_state & state_flags) == 0:
            return button

    return None

def AuiTabCtrl_OnLeftDClick(self, event):
    x, y = event.GetX(), event.GetY()
    wnd = self.TabHitTest(x, y)

    if wnd:
        e = aui.AuiNotebookEvent(aui.wxEVT_COMMAND_AUINOTEBOOK_TAB_DCLICK, self.GetId())
        e.SetEventObject(self)
        e.SetSelection(self.GetIdxFromWindow(wnd))
        e.Page = wnd
        self.GetEventHandler().ProcessEvent(e)
    elif not self.ButtonHitTest(x, y, state_flags=aui.AUI_BUTTON_STATE_HIDDEN):
        e = aui.AuiNotebookEvent(aui.wxEVT_COMMAND_AUINOTEBOOK_BG_DCLICK, self.GetId())
        e.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(e)

aui.AuiTabContainer.ButtonHitTest = AuiTabContainer_ButtonHitTest
aui.AuiTabCtrl.OnLeftDClick = AuiTabCtrl_OnLeftDClick
