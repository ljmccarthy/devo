import wx

class MenuItem(object):
    NORMAL = wx.ITEM_NORMAL
    CHECK = wx.ITEM_CHECK
    RADIO = wx.ITEM_RADIO

    def __init__(self, id, label="", accel="", kind=NORMAL):
        self.id = id
        self.label = label
        self.accel = accel
        self.kind = kind

    def Build(self, menu):
        text = "%s\t%s" % (self.label, self.accel) if self.accel else self.label
        menu.Append(self.id, text, kind=self.kind)

class MenuSeparator(object):
    def Build(self, menu):
        menu.AppendSeparator()

MenuSeparator = MenuSeparator()

class Menu(object):
    def __init__(self, label, items):
        self.label = label
        self.items = items

    def Build(self, menu):
        menu.AppendSubMenu(self.Create(), self.label)

    def Create(self):
        menu = wx.Menu()
        for item in self.items:
            item.Build(menu)
        return menu

class MenuBar(object):
    def __init__(self, menus):
        self.menus = menus

    def Create(self):
        menubar = wx.MenuBar()
        for menu in self.menus:
            menubar.Append(menu.Create(), menu.label)
        return menubar
