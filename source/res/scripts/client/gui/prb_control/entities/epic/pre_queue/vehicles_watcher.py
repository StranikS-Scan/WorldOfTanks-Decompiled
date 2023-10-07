# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/vehicles_watcher.py
from itertools import chain
import typing
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EPIC
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class EpicVehiclesWatcher(BaseVehiclesWatcher):
    _BATTLE_MODE_VEHICLE_TAGS = BATTLE_MODE_VEH_TAGS_EXCEPT_EPIC
    _VEH_STATE_PRIORITIES = {Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE: 1,
     Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE: 0}
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(EpicVehiclesWatcher, self).__init__()
        self.__validVehicleLevels = []
        self.__unlockVehicleLevels = []
        self.__forbiddenVehTypes = []

    def stop(self):
        super(EpicVehiclesWatcher, self).stop()
        self.__validVehicleLevels = []
        self.__unlockVehicleLevels = []
        self.__forbiddenVehTypes = []

    def _getUnsuitableVehicles(self, onClear=False):
        config = self.lobbyContext.getServerSettings().epicBattles
        newValidVehicleLevels = config.validVehicleLevels
        newForbiddenVehTypes = config.forbiddenVehTypes
        vehicleListChanged = newValidVehicleLevels != self.__validVehicleLevels or newForbiddenVehTypes != self.__forbiddenVehTypes
        if vehicleListChanged and not onClear:
            self._clearCustomsStates()
            self.__validVehicleLevels = newValidVehicleLevels
            self.__forbiddenVehTypes = newForbiddenVehTypes
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.LEVELS(self.__validVehicleLevels) ^ REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__forbiddenVehTypes)).itervalues()
        return chain(vehs, self._getUnsuitableVehiclesBase())

    def _getVehiclesCustomStates(self, onClear=False):
        result = super(EpicVehiclesWatcher, self)._getVehiclesCustomStates(onClear)
        result.update({Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE: self.__getWillBeUnlockedVehicles(onClear)})
        return result

    def __getWillBeUnlockedVehicles(self, onClear=False):
        config = self.lobbyContext.getServerSettings().epicBattles
        newUnlockVehicleLevels = config.unlockableInBattleVehLevels
        if newUnlockVehicleLevels != self.__unlockVehicleLevels and not onClear:
            self._clearCustomsStates()
            self.__unlockVehicleLevels = newUnlockVehicleLevels
        vehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(self.__unlockVehicleLevels)).itervalues()
        return vehicles
