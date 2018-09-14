# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/__init__.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__author__ = 'd_dichkovsky'
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.UNIT_USER, 'gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler', 'UnitUserCMHandler')

class NavigationStack(object):
    __stacks = {}

    @classmethod
    def clear(cls, key):
        if key in cls.__stacks:
            cls.__stacks[key] = []

    @classmethod
    def exclude(cls, key, flashAlias):
        items = cls.__stacks.get(key, [])[:]
        for item in items:
            if item[0] == flashAlias:
                cls.__stacks[key].remove(item)

    @classmethod
    def hasHistory(cls, key):
        if key in cls.__stacks:
            return len(cls.__stacks[key])
        return 0

    @classmethod
    def current(cls, key):
        if key in cls.__stacks and len(cls.__stacks[key]):
            return cls.__stacks[key][-1]
        else:
            return None

    @classmethod
    def prev(cls, key):
        if key in cls.__stacks and len(cls.__stacks[key]) > 1:
            return cls.__stacks[key][-2]
        else:
            return None

    @classmethod
    def nav2Next(cls, key, flashAlias, pyAlias, itemID):
        item = (flashAlias, pyAlias, itemID)
        if key in cls.__stacks:
            if item not in cls.__stacks[key]:
                cls.__stacks[key].append(item)
        else:
            cls.__stacks[key] = [item]

    @classmethod
    def nav2Prev(cls, key):
        if key in cls.__stacks and len(cls.__stacks[key]):
            return cls.__stacks[key].pop()
        else:
            return None
