# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/cache.py
import typing
from wotdecorators import singleton

def getCache():
    return GFNotificationsCache


class IGFNotificationsCache(object):
    __slots__ = ('__data',)

    def setPayload(self, id, payload):
        raise NotImplementedError

    def getPayload(self, id):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


@singleton
class GFNotificationsCache(IGFNotificationsCache):

    def __init__(self):
        self.__data = {}

    def setPayload(self, id, payload):
        self.__data[id] = payload

    def getPayload(self, id):
        return self.__data.get(id, {})

    def clear(self):
        self.__data.clear()
