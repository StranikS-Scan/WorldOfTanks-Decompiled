# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/__init__.py
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EventBus, EVENT_BUS_SCOPE
__all__ = ['g_eventBus',
 'g_itemsCache',
 'init',
 'start',
 'fini',
 'EVENT_BUS_SCOPE']
g_eventBus = EventBus()
