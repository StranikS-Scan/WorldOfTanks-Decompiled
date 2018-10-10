# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/events.py
import Event

class _WGNCEvents(object):
    __slots__ = ('__eManager', 'onItemShowByDefault', 'onItemShowByAction', 'onItemUpdatedByAction', 'onProxyDataItemShowByDefault', 'onItemActionFired')

    def __init__(self):
        super(_WGNCEvents, self).__init__()
        self.__eManager = Event.EventManager()
        self.onItemShowByDefault = Event.Event(self.__eManager)
        self.onItemShowByAction = Event.Event(self.__eManager)
        self.onItemUpdatedByAction = Event.Event(self.__eManager)
        self.onProxyDataItemShowByDefault = Event.Event(self.__eManager)
        self.onItemActionFired = Event.Event(self.__eManager)

    def clear(self):
        self.__eManager.clear()


g_wgncEvents = _WGNCEvents()
