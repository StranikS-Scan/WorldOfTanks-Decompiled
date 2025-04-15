# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/easy_tank_equip_provider.py
import logging
from typing import Optional
from gui.game_control.wotlda.loadout_model import BaseOptDeviceLoadoutModel
from gui.game_control.wotlda.response import WotldaResponse
from wg_async import wg_await, wg_async
from gui.game_control.wotlda.constants import SupportedWotldaLoadoutType, LAST_UPDATE_TIMESTAMP
from gui.game_control.wotlda.loadout_model import baseOptDeviceLoadoutSchema
from gui.game_control.wotlda.requester import WotldaRequester
from gui.game_control.wotlda.cache import EasyTankEquipCache
_logger = logging.getLogger(__name__)

class _EasyTankEquipProvider(object):

    def __init__(self):
        super(_EasyTankEquipProvider, self).__init__()
        self._loadoutType = SupportedWotldaLoadoutType.EASY_TANK_EQUIP.value
        self._requester = WotldaRequester()
        self._cache = EasyTankEquipCache()
        self._isInitialized = False

    def start(self):
        if self._isInitialized:
            return
        self._cache.read()

    def stop(self):
        self._cache.clear()
        self._requester.destroy()

    def clear(self):
        self._cache.clearCache()
        self._isInitialized = False

    @wg_async
    def updateCacheData(self):
        if self._isInitialized:
            return
        response = yield wg_await(self._requester.getEasyTankEquipLoadouts(self._cache.getUpdatedAtTimestamp()))
        if response.hasRequestFailed():
            _logger.warning('Requesting easy tank equip loadouts failed.')
            return
        if response.isNotModified():
            self._isInitialized = True
            return
        cacheData = response.getLoadoutsByType(self._loadoutType)
        cacheData.update({LAST_UPDATE_TIMESTAMP: response.getTimestamp()})
        self._cache.update(cacheData)
        self._isInitialized = True

    def getLoadoutByVehicleID(self, vehicleID):
        loadout = self._cache.getLoadout(vehicleID)
        if not loadout:
            return None
        else:
            parsedLoadout = baseOptDeviceLoadoutSchema.deserialize(loadout[0])
            return parsedLoadout
