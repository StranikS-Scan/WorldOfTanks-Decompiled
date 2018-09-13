# Embedded file name: scripts/client/notification/NotificationsCounter.py
from gui.prb_control.prb_helpers import prbInvitesProperty
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter

class NotificationsCounter(object):

    def __init__(self):
        super(NotificationsCounter, self).__init__()
        self.__count = 0

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def increment(self):
        self.__count += 1
        return self.__count

    def decrement(self):
        self.__count -= 1
        return self.__count

    def count(self):
        return self.__count

    def reset(self):
        self.proto.serviceChannel.resetUnreadCount()
        self.prbInvites.resetUnreadCount()
        self.__count = 0
        return self.__count
