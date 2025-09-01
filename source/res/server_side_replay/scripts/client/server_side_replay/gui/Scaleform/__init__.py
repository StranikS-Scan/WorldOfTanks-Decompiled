# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/Scaleform/__init__.py
from server_side_replay.gui.shared.event_dispatcher import showReplays
from gui.shared.system_factory import registerMenuItems
from helpers import dependency
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isSsrPlayEnabled(itemsCache=None):
    return itemsCache.items.stats.isSsrPlayEnabled


def registerMainMenuEntries():
    from gui.impl.gen.view_models.views.lobby.hangar.main_menu_model import MainMenuModel
    from gui.impl.lobby.hangar.presenters.utils import MenuItemEntry
    menuItems = {MainMenuModel.REPLAYS: MenuItemEntry(showReplays, isSsrPlayEnabled, isSsrPlayEnabled)}
    registerMenuItems('hangar', menuItems)
