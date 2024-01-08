# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsCounter.py
from gui.prb_control import prbInvitesProperty
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.shared.notifications import NotificationGroup
_COUNT_ONLY_ONCE_INDEX = 2

class _GroupCounter(object):

    def __init__(self):
        super(_GroupCounter, self).__init__()
        self.__notifications = set()
        self.__seenNotifications = set()

    def addNotification(self, typeID, entityID, countOnlyOnce):
        self.__notifications.add((typeID, entityID, countOnlyOnce))

    def removeNotification(self, typeID, entityID, countOnlyOnce):
        self.__notifications.discard((typeID, entityID, countOnlyOnce))

    def count(self):
        return len(self.__notifications - self.__seenNotifications)

    def reset(self):
        self.__seenNotifications |= {entry for entry in self.__notifications if entry[_COUNT_ONLY_ONCE_INDEX]}
        self.resetUnreadCount()

    def resetUnreadCount(self):
        self.__notifications.clear()

    @classmethod
    def getGroupID(cls):
        pass


class _InfoGroupCounter(_GroupCounter):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def resetUnreadCount(self):
        super(_InfoGroupCounter, self).resetUnreadCount()
        self.proto.serviceChannel.resetUnreadCount()

    @classmethod
    def getGroupID(cls):
        return NotificationGroup.INFO


class _InviteGroupCounter(_GroupCounter):

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def resetUnreadCount(self):
        super(_InviteGroupCounter, self).resetUnreadCount()
        if self.prbInvites is not None:
            self.prbInvites.resetUnreadCount()
        return

    @classmethod
    def getGroupID(cls):
        return NotificationGroup.INVITE


class _OfferGroupCounter(_GroupCounter):

    @classmethod
    def getGroupID(cls):
        return NotificationGroup.OFFER


class _CounterCollection(object):

    def __init__(self, seq):
        super(_CounterCollection, self).__init__()
        self.__counters = dict(((counter.getGroupID(), counter) for counter in seq))

    def clear(self):
        self.__counters.clear()

    def addNotification(self, group, typeID, entityID, countOnlyOnce):
        self.__counters[group].addNotification(typeID, entityID, countOnlyOnce)
        return self.count()

    def removeNotification(self, group, typeID, entityID, countOnlyOnce):
        if group is None:
            for counter in self.__counters.values():
                counter.removeNotification(typeID, entityID, countOnlyOnce)

        else:
            self.__counters[group].removeNotification(typeID, entityID, countOnlyOnce)
        return self.count()

    def count(self, group=None):
        return sum((counter.count() for counter in self.__counters.values())) if group is None else self.__counters[group].count()

    def reset(self, group=None):
        if group is None:
            for counter in self.__counters.values():
                counter.reset()

        else:
            self.__counters[group].reset()
        return self.count()

    def resetUnreadCount(self, group=None):
        if group is None:
            for counter in self.__counters.values():
                counter.resetUnreadCount()

        else:
            self.__counters[group].resetUnreadCount()
        return


class NotificationsCounter(_CounterCollection):

    def __init__(self):
        super(NotificationsCounter, self).__init__((_InfoGroupCounter(), _InviteGroupCounter(), _OfferGroupCounter()))
