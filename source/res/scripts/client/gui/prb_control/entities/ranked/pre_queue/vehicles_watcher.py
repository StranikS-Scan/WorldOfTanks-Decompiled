# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/vehicles_watcher.py
import typing
from itertools import chain
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class RankedVehiclesWatcher(BaseVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def _getUnsuitableVehicles(self, onClear=False):
        allVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        config = self.__lobbyContext.getServerSettings().rankedBattles
        vehLevels = range(MIN_VEHICLE_LEVEL, config.minLevel) + range(config.maxLevel + 1, MAX_VEHICLE_LEVEL + 1)
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        classVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLASSES(config.forbiddenClassTags)).itervalues()
        typeVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(config.forbiddenVehTypes)).itervalues()
        eventVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        battleRoyaleVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BATTLE_ROYALE).itervalues()
        clanWarsVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLAN_WARS).itervalues()
        return chain(vehs, classVehs, typeVehs, eventVehs, epicVehs, battleRoyaleVehs, clanWarsVehs) if not onClear else allVehs
