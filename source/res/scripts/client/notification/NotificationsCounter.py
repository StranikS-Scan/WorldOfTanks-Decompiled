# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsCounter.py
from debug_utils import LOG_DEBUG
from gui.prb_control.prb_helpers import prbInvitesProperty
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from notification.settings import NOTIFICATION_GROUP

class _GroupCounter(object):
    """
    Simple base counter with group ID
    """

    def __init__(self):
        super(_GroupCounter, self).__init__()
        self.__notifications = set()

    def addNotification(self, typeID, entityID):
        self.__notifications.add((typeID, entityID))

    def removeNotification(self, typeID, entityID):
        self.__notifications.discard((typeID, entityID))

    def count(self):
        return len(self.__notifications)

    def reset(self):
        self.__notifications.clear()
        self.resetUnreadCount()

    def resetUnreadCount(self):
        pass

    @classmethod
    def getGroupID(cls):
        pass


class _InfoGroupCounter(_GroupCounter):

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def resetUnreadCount(self):
        self.proto.serviceChannel.resetUnreadCount()

    @classmethod
    def getGroupID(cls):
        return NOTIFICATION_GROUP.INFO


class _InviteGroupCounter(_GroupCounter):

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def resetUnreadCount(self):
        self.prbInvites.resetUnreadCount()

    @classmethod
    def getGroupID(cls):
        return NOTIFICATION_GROUP.INVITE


class _OfferGroupCounter(_GroupCounter):

    @classmethod
    def getGroupID(cls):
        return NOTIFICATION_GROUP.OFFER


class _CounterCollection(object):

    def __init__(self, seq):
        super(_CounterCollection, self).__init__()
        self.__counters = dict(map(lambda counter: (counter.getGroupID(), counter), seq))

    def clear(self):
        self.__counters.clear()

    def addNotification(self, group, typeID, entityID):
        self.__counters[group].addNotification(typeID, entityID)
        return self.count()

    def removeNotification(self, group, typeID, entityID):
        if group is None:
            for counter in self.__counters.itervalues():
                counter.removeNotification(typeID, entityID)

        else:
            self.__counters[group].removeNotification(typeID, entityID)
        return self.count()

    def count(self, group=None):
        if group is None:
            return sum((counter.count() for counter in self.__counters.itervalues()))
        else:
            return self.__counters[group].count()
            return

    def reset(self, group=None):
        if group is None:
            for counter in self.__counters.itervalues():
                counter.reset()

        else:
            self.__counters[group].reset()
        return self.count()

    def resetUnreadCount(self, group=None):
        if group is None:
            for counter in self.__counters.itervalues():
                counter.resetUnreadCount()

        else:
            self.__counters[group].resetUnreadCount()
        return


class NotificationsCounter(_CounterCollection):

    def __init__(self):
        super(NotificationsCounter, self).__init__((_InfoGroupCounter(), _InviteGroupCounter(), _OfferGroupCounter()))
