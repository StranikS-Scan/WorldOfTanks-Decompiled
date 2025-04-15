# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus_assistant.py
import logging
import typing
import wg_async
from BWUtil import AsyncReturn
from gui.game_control.wot_plus_crew_assist import CrewAssistantCtrl
from gui.game_control.wot_plus_opt_device_assist import OptionalDevicesAssistantCtrl
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType, LAST_UPDATE_TIMESTAMP
from gui.game_control.wotlda.requester import WotldaRequester
from gui.game_control.wotlda.response import WotldaResponse
if typing.TYPE_CHECKING:
    from typing import Set
    from constants import PREBATTLE_TYPE
_logger = logging.getLogger(__name__)

def registerAllowedPrebattleType(prbType, loadoutType):
    CrewAssistantCtrl._SUPPORTED_PREBATTLE_TYPES.append(prbType)
    OptionalDevicesAssistantCtrl.addSupportedBattleType(prbType, loadoutType)
    WotPlusAssistant.addLoadoutType(loadoutType)


class WotPlusAssistant(object):
    _LOADOUT_TYPES_TO_REQUEST = {SupportedWotldaLoadoutType.RANDOM, SupportedWotldaLoadoutType.CREW}

    def __init__(self):
        super(WotPlusAssistant, self).__init__()
        self._optDeviceAssistant = OptionalDevicesAssistantCtrl()
        self._crewAssistant = CrewAssistantCtrl()
        self._requester = WotldaRequester()
        self._isStarted = False
        self._loadoutsObtained = False
        self._waitingForResponse = False

    @classmethod
    def addLoadoutType(cls, loadoutType):
        if loadoutType not in SupportedWotldaLoadoutType:
            _logger.warning('Trying to add loadout type %s which is not supported', loadoutType)
            return
        if loadoutType in cls._LOADOUT_TYPES_TO_REQUEST:
            _logger.warning('Trying to add loadout type %s which is already in request', loadoutType.value)
            return
        cls._LOADOUT_TYPES_TO_REQUEST.add(loadoutType)

    @property
    def optDeviceAssistant(self):
        return self._optDeviceAssistant

    @property
    def crewAssistant(self):
        return self._crewAssistant

    def start(self):
        if not self._isStarted:
            self._optDeviceAssistant.start()
            self._crewAssistant.start()
            self._isStarted = True

    def heatCache(self):
        self._crewAssistant.heatCache()
        self._optDeviceAssistant.heatCache()

    def clear(self):
        self._loadoutsObtained = False

    def clearWithCacheDelete(self):
        self.clear()
        self._optDeviceAssistant.deleteClientCacheFile()
        self._crewAssistant.deleteClientCacheFile()

    @wg_async.wg_async
    def subscriptionValidated(self):
        if self._waitingForResponse:
            _logger.debug('WotPlusAssistant in waiting for response and somebody tries to start another one, skipping')
            raise AsyncReturn(None)
        if not self._loadoutsObtained and self._isStarted:
            yield wg_async.wg_await(self._fetchLoadouts(self._LOADOUT_TYPES_TO_REQUEST))
        raise AsyncReturn(None)
        return

    @wg_async.wg_async
    def _fetchLoadouts(self, loadoutTypes):
        self._waitingForResponse = True
        try:
            clientCacheUpdatedAt = min(self._optDeviceAssistant.remoteClientCacheUpdatedAt, self._crewAssistant.remoteClientCacheUpdatedAt)
            response = yield wg_async.wg_await(self._requester.getSubscriptionLoadouts(clientCacheUpdatedAt, loadoutTypes))
        finally:
            self._waitingForResponse = False

        if response.isNotModified():
            _logger.debug('Loadouts data for subscription is not modified, skipping update')
        elif response.isSuccess():
            loadouts = response.getData()
            crewLoadouts = loadouts.pop(SupportedWotldaLoadoutType.CREW.value, {})
            crewLoadouts[LAST_UPDATE_TIMESTAMP] = loadouts.get(LAST_UPDATE_TIMESTAMP, 0)
            self._optDeviceAssistant.fillRemotePresets(loadouts)
            self._crewAssistant.fillLoadouts(crewLoadouts)
            self._loadoutsObtained = True
        raise AsyncReturn(None)
        return

    def destroy(self):
        self._isStarted = False
        self._optDeviceAssistant.destroy()
        self._crewAssistant.destroy()
        self.clear()
