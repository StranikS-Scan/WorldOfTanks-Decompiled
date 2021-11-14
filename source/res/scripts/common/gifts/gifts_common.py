# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/gifts/gifts_common.py
from constants import IS_DEVELOPMENT
from soft_exception import SoftException
UNKNOWN_SENDER_ID = 0

class ClientReqStrategy(object):
    AUTO = 'auto'
    DEMAND = 'demand'
    ALL = (AUTO, DEMAND)


class GiftEventID(object):
    UNKNOWN = 0
    DEV_TEST = 1
    ALL = (UNKNOWN,) + ((DEV_TEST,) if IS_DEVELOPMENT else ())


class GiftEventState(object):
    ENABLED = 'enabled'
    SUSPENDED = 'suspended'
    DISABLED = 'disabled'
    ALL = (ENABLED, SUSPENDED, DISABLED)


class GiftStatus(object):
    TYPE = int
    NEW = 1
    AVAILABLE = 2
    OPENED = 3
    ACTIVE = (NEW, AVAILABLE)
    ALL = (NEW, AVAILABLE, OPENED)


class Gift(object):
    __slots__ = ('_giftID', '_senderID', '_giftItemID', '_status', '_meta')

    def __init__(self, giftID, senderID, giftItemID, status, meta):
        self._giftID = giftID
        self._senderID = senderID
        self._giftItemID = giftItemID
        self._status = status
        self._meta = meta

    @property
    def giftID(self):
        return self._giftID

    @property
    def giftItemID(self):
        return self._giftItemID

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in GiftStatus.ALL:
            raise SoftException('Wrong status', value)
        self._status = value

    def toOpenExtra(self):
        return (self._senderID, self._meta)

    def __str__(self):
        return 'Gift:[giftID: {}, senderID: {}, giftItemID: {}, meta: {}, status: {}]'.format(self._giftID, self._senderID, self._giftItemID, self._meta, self._status)
