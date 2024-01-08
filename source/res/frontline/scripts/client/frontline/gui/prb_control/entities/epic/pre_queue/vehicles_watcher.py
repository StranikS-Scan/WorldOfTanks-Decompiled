# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/entities/epic/pre_queue/vehicles_watcher.py
from itertools import chain
import typing
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_EPIC
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import isVehLevelUnlockableInBattle
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

    def _getUnsuitableVehicles(self, onClear=False):
        config = self.lobbyContext.getServerSettings().epicBattles
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.LEVELS(config.validVehicleLevels)).itervalues()
        return chain(vehs, self._getUnsuitableVehiclesBase())

    def _getVehiclesCustomStates(self, onClear=False):
        result = super(EpicVehiclesWatcher, self)._getVehiclesCustomStates(onClear)
        result.update({Vehicle.VEHICLE_STATE.WILL_BE_UNLOCKED_IN_BATTLE: self.__getWillBeUnlockedVehicles()})
        return result

    def __getWillBeUnlockedVehicles(self):
        vehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.CUSTOM(lambda v: isVehLevelUnlockableInBattle(v.level))).itervalues()
        return vehicles
