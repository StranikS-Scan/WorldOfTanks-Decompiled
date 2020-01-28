# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/pre_queue/vehicles_watcher.py
from itertools import chain
import typing
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IBobController
from skeletons.gui.shared import IItemsCache

class BobVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    bobCtrl = dependency.descriptor(IBobController)

    def _getUnsuitableVehicles(self):
        validLevels = self.bobCtrl.getConfig().levels
        vehLevels = list(set(range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)) - set(validLevels))
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        eventVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        return chain(vehs, eventVehs, epicVehs)
