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

    def Build(self, menu, hooks):
        text = "%s\t%s" % (self.label, self.accel) if self.accel else self.label
        menu.Append(self.id, text, kind=self.kind)

class MenuSeparator(object):
    def Build(self, menu, hooks):
        last = menu.GetMenuItemCount() - 1
        if last >= 0 and menu.FindItemByPosition(last).GetKind() != wx.ITEM_SEPARATOR:
            menu.AppendSeparator()

class MenuHook(object):
    def __init__(self, id):
        self.id = id

    def Build(self, menu, hooks):
        for item in hooks.get(self.id, []):
            item.Build(menu, hooks)

MenuSeparator = MenuSeparator()

class Menu(object):
    def __init__(self, label, items):
        self.label = label
        self.items = items

    def Build(self, menu, hooks):
        menu.AppendSubMenu(self.Create(), self.label)

    def Create(self, **hooks):
        menu = wx.Menu()
        for item in self.items:
            item.Build(menu, hooks)
        last = menu.GetMenuItemCount() - 1
        if last >= 0:
            item = menu.FindItemByPosition(last)
            if item.GetKind() == wx.ITEM_SEPARATOR:
                menu.DeleteItem(item)
        return menu

class MenuBar(object):
    def __init__(self, menus):
        self.menus = menus

    def Create(self, **hooks):
        menubar = wx.MenuBar()
        for menu in self.menus:
            menubar.Append(menu.Create(**hooks), menu.label)
        return menubar
