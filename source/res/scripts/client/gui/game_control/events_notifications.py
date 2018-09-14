# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/events_notifications.py
from collections import namedtuple
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from helpers import getLocalizedData
from skeletons.gui.game_control import IEventsNotificationsController

class EventsNotificationsController(IEventsNotificationsController):

    def __init__(self):
        super(EventsNotificationsController, self).__init__()
        self.__eventMgr = Event.EventManager()
        self.onEventNotificationsChanged = Event.Event(self.__eventMgr)

    def fini(self):
        self.__stop()
        self.__eventMgr = None
        super(EventsNotificationsController, self).fini()
        return

    def onLobbyInited(self, event):
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotification

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def getEventsNotifications(self, filterFunc=None):
        return filter(filterFunc or (lambda a: True), map(EventNotification.make, BigWorld.player().eventNotifications))

    def __stop(self):
        self.__eventMgr.clear()
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotification

    def __onEventNotification(self, diff):
        added = map(EventNotification.make, diff.get('added', ()))
        removed = map(EventNotification.make, diff.get('removed', ()))
        self.onEventNotificationsChanged(added, removed)


class EventNotification(namedtuple('EventNotification', 'eventType data text')):

    @classmethod
    def default(cls):
        return cls.__new__(cls, None, None, None)

    @classmethod
    def make(cls, data):
        text = getLocalizedData(data, 'text')
        return cls.__new__(cls, data['type'], data.get('data'), text)
