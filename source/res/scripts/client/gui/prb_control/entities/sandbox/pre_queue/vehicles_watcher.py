# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/sandbox/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import MAX_VEHICLE_LEVEL
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.prb_control.settings import SANDBOX_MAX_VEHICLE_LEVEL
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class SandboxVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(range(SANDBOX_MAX_VEHICLE_LEVEL + 1, MAX_VEHICLE_LEVEL + 1))).itervalues()
        eventVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        clanWarsVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLAN_WARS).itervalues()
        return chain(vehs, eventVehs, epicVehs, clanWarsVehs)
