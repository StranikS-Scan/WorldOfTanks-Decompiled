# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/stronghold_event_requester.py
import json
import logging
import typing
import Event
import wg_async
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled
from gui.clans.clan_cache import g_clanCache
from gui.game_control.reactive_comm import Subscription
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IReactiveCommunicationService
_logger = logging.getLogger(__name__)

class FrozenVehiclesConstants(CONST_CONTAINER):
    ALL_VEHICLES_FROZEN = 'ALL_VEHICLES_FROZEN'
    E_VEHICLE_FREEZE = 'vehicle_freeze'
    E_VEHICLE_FREEZE_ALL = 'vehicle_freeze_all'
    E_VEHICLE_UNFREEZE = 'vehicle_unfreeze'
    E_VEHICLE_UNFREEZE_ALL = 'vehicle_unfreeze_all'


class FrozenVehiclesRequester(object):
    __slots__ = ('onUpdated', '__cache', '__isStarted', '__subscription', '__eventsManager')
    __RCService = dependency.descriptor(IReactiveCommunicationService)

    def __init__(self):
        super(FrozenVehiclesRequester, self).__init__()
        self.__cache = dict()
        self.__isStarted = False
        self.__subscription = None
        self.__eventsManager = Event.EventManager()
        self.onUpdated = Event.Event(self.__eventsManager)
        return

    @property
    def isStarted(self):
        return self.__isStarted

    @property
    def canStart(self):
        return getStrongholdEventEnabled() and g_clanCache.isInClan

    def start(self):
        if not self.__isStarted and self.canStart:
            self.__isStarted = True
            self.__subscribe()

    def stop(self):
        self.__isStarted = False
        self.__clearSubscription()
        self.__eventsManager.clear()
        self.__cache.clear()

    def getCache(self):
        return self.__cache

    def isCacheEmpty(self):
        return not bool(self.__cache)

    def setInitialDataAndStart(self, data):
        for playerData in data:
            if not isinstance(playerData, dict):
                continue
            spaID = playerData.get('spa_id')
            if spaID is None:
                continue
            allVehicles = playerData.get('all_vehicles')
            if allVehicles is not None and allVehicles:
                self.__cache[spaID] = FrozenVehiclesConstants.ALL_VEHICLES_FROZEN
                continue
            self.__cache[spaID] = set([ v.get('vehicle_cd', -1) for v in playerData.get('vehicles', []) ])

        if not self.isCacheEmpty():
            self.onUpdated(self.__cache.keys())
        self.start()
        return

    def _onMessage(self, message):
        updatedSpaIDs = []
        message = json.loads(message)
        for record in message:
            event = record.get('event')
            if event is None:
                continue
            spaID = record.get('spa_id')
            if event == FrozenVehiclesConstants.E_VEHICLE_UNFREEZE_ALL and spaID is None:
                updatedSpaIDs.extend(self.__cache.keys())
                self.__cache.clear()
                continue
            if spaID is None:
                continue
            vehicleCds = set(record.get('vehicle_cds', []))
            currentFrozenVehicles = self.__cache.get(spaID, set())
            if event == FrozenVehiclesConstants.E_VEHICLE_UNFREEZE:
                newFrozenVehicles = currentFrozenVehicles - vehicleCds
            elif event == FrozenVehiclesConstants.E_VEHICLE_UNFREEZE_ALL:
                newFrozenVehicles = set()
            elif event == FrozenVehiclesConstants.E_VEHICLE_FREEZE_ALL:
                newFrozenVehicles = FrozenVehiclesConstants.ALL_VEHICLES_FROZEN
            else:
                newFrozenVehicles = currentFrozenVehicles | vehicleCds
            self.__cache[spaID] = newFrozenVehicles
            updatedSpaIDs.append(spaID)

        if updatedSpaIDs:
            self.onUpdated(updatedSpaIDs)
        return

    def __onClosed(self, reason):
        self.__clearSubscription()

    @wg_async.wg_async
    def __subscribe(self):
        self.__subscription = Subscription(self.__getChannelName())
        result = yield wg_async.wg_await(self.__RCService.subscribeToChannel(self.__subscription))
        if result:
            self.__subscription.onMessage += self._onMessage
            self.__subscription.onClosed += self.__onClosed
        else:
            self.__clearSubscription()

    def __clearSubscription(self):
        if self.__subscription is not None:
            self.__subscription.onMessage -= self._onMessage
            self.__subscription.onClosed -= self.__onClosed
            self.__RCService.unsubscribeFromChannel(self.__subscription)
            self.__subscription = None
        return

    @staticmethod
    def __getChannelName():
        return 'wgshevents_clan_{}'.format(g_clanCache.clanDBID)
