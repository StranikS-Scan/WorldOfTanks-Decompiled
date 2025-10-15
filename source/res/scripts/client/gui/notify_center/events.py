# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/notify_center/events.py
import Event

class _NotifyCenterEvents(object):
    __slots__ = ('__eManager', 'onItemShowByDefault', 'onItemShowByAction', 'onItemUpdatedByAction', 'onProxyDataItemShowByDefault', 'onItemActionFired')

    def __init__(self):
        super(_NotifyCenterEvents, self).__init__()
        self.__eManager = Event.EventManager()
        self.onItemShowByDefault = Event.Event(self.__eManager)
        self.onItemShowByAction = Event.Event(self.__eManager)
        self.onItemUpdatedByAction = Event.Event(self.__eManager)
        self.onProxyDataItemShowByDefault = Event.Event(self.__eManager)
        self.onItemActionFired = Event.Event(self.__eManager)

    def clear(self):
        self.__eManager.clear()


g_notifyCenterEvents = _NotifyCenterEvents()
