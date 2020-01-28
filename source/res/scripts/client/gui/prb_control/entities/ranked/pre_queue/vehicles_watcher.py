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
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def _getUnsuitableVehicles(self):
        config = self.lobbyContext.getServerSettings().rankedBattles
        vehLevels = range(MIN_VEHICLE_LEVEL, config.minLevel) + range(config.maxLevel + 1, MAX_VEHICLE_LEVEL + 1)
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        eventVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        bobVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BOB_BATTLE).itervalues()
        return chain(vehs, eventVehs, epicVehs, bobVehs)
