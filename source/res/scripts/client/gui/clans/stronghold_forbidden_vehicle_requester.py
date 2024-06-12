# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/stronghold_forbidden_vehicle_requester.py
import logging
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled
from gui.clans.clan_cache import g_clanCache
_logger = logging.getLogger(__name__)

class ForbiddenVehiclesRequester(object):
    __slots__ = ('__cache', '__isStarted')

    def __init__(self):
        super(ForbiddenVehiclesRequester, self).__init__()
        self.__cache = dict()
        self.__isStarted = False

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def canStart(self):
        return getStrongholdEventEnabled() and g_clanCache.isInClan

    def start(self):
        if not self.__isStarted and self.canStart:
            self.__isStarted = True

    def stop(self):
        self.__isStarted = False
        self.__cache.clear()

    def getCache(self):
        return self.__cache

    def isCacheEmpty(self):
        return not bool(self.__cache)

    def setInitialDataAndStart(self, data):
        self.__cache.update(data)
