import wx

def main():
    app = wx.PySimpleApp()
    from mainframe import MainFrame
    mainframe = MainFrame()
    mainframe.Show()
    app.SetTopWindow(mainframe)
    app.MainLoop()

if __name__ == "__main__":
    main()
