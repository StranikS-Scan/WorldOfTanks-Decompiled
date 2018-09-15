# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/__init__.py
from gui.shared.items_cache import ItemsCache
from gui.shared.event_bus import EventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.factories import GuiItemFactory
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
__all__ = ('g_eventBus', 'getSharedServices', 'EVENT_BUS_SCOPE')
g_eventBus = EventBus()

def getSharedServices(manager):
    """ Configures services for package game_control.
    :param manager: instance of dependency manager.
    """
    cache = ItemsCache()
    cache.init()
    manager.addInstance(IItemsCache, cache, finalizer='fini')
    itemsFactory = GuiItemFactory()
    manager.addInstance(IGuiItemsFactory, itemsFactory)
