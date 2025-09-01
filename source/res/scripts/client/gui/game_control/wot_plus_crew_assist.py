# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_crew_assist.py
import logging
import typing
from constants import RENEWABLE_SUBSCRIPTION_CONFIG, PREBATTLE_TYPE
from gui.game_control.wotlda.cache import CrewCache
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_bus import SharedEvent
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import Tuple, Dict, Optional
_logger = logging.getLogger(__name__)

class CrewAssistantCtrl(object):
    CREW_ASSIST_DATA_CHANGED = 'crewAssistDataChanged'
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _platoonCtrl = dependency.descriptor(IPlatoonController)
    _SUPPORTED_PREBATTLE_TYPES = [PREBATTLE_TYPE.SQUAD,
     PREBATTLE_TYPE.STRONGHOLD,
     PREBATTLE_TYPE.CLAN,
     PREBATTLE_TYPE.TOURNAMENT,
     PREBATTLE_TYPE.EPIC,
     PREBATTLE_TYPE.MAPBOX,
     PREBATTLE_TYPE.FUN_RANDOM,
     PREBATTLE_TYPE.TRAINING]

    def __init__(self):
        super(CrewAssistantCtrl, self).__init__()
        self.__isEnabled = False
        self._cache = CrewCache()

    @property
    def remoteClientCacheUpdatedAt(self):
        return self._cache.getUpdatedAtTimestamp()

    def deleteClientCacheFile(self):
        self._cache.deleteCacheFile()

    def destroy(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self._cache.clear()

    def fillLoadouts(self, loadouts):
        if not loadouts:
            _logger.warning('Trying to cache empty crew loadouts ')
            return
        _logger.debug('Crew loadouts cache is updated')
        self._cache.update(loadouts)

    def heatCache(self):
        self._cache.read()

    def start(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.__isEnabled = self._lobbyContext.getServerSettings().isCrewAssistantEnabled()

    def isEnabled(self):
        return self.__isEnabled

    def hasOrderSets(self, vehIntCD, tankmanRole):
        return self.validateOrderSets(self.getOrderSets(vehIntCD, tankmanRole))

    def validateOrderSets(self, orderSets):
        hasCommonSet, hasLegendarySet = False, False
        for commonPercent, legendaryPercent in orderSets.itervalues():
            hasCommonSet |= commonPercent > 0.0
            hasLegendarySet |= legendaryPercent > 0.0
            if hasCommonSet and hasLegendarySet:
                break

        return (hasCommonSet, hasLegendarySet)

    def getOrderSets(self, vehIntCD, tankmanRole):
        if not self.__isEnabled:
            return self._formEmptyResponse()
        if self._cache.isCacheEmpty():
            _logger.warning('Crew cache is empty')
            return self._formEmptyResponse()
        if self._platoonCtrl.getPrbEntityType() not in self._SUPPORTED_PREBATTLE_TYPES:
            return self._formEmptyResponse()
        crewData = self._cache.getLoadout(vehIntCD, role=tankmanRole)
        if crewData:
            _logger.debug('Requesting crew loadouts for vehicleID = %s and tankmanRole = %s, result = %s', vehIntCD, tankmanRole, crewData)
            return crewData
        _logger.debug("Couldn't find crew data for tankman role=%s, (vehicle id=%d)", tankmanRole, vehIntCD)
        return self._formEmptyResponse()

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            newIsEnabled = self._lobbyContext.getServerSettings().isCrewAssistantEnabled()
            if self.__isEnabled is not newIsEnabled:
                self.__isEnabled = newIsEnabled
                g_eventBus.handleEvent(SharedEvent(self.CREW_ASSIST_DATA_CHANGED), EVENT_BUS_SCOPE.LOBBY)

    def _formEmptyResponse(self):
        return {}
