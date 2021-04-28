# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/weekend_brawl/pre_queue/vehicles_watcher.py
from itertools import chain
import typing
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController
from skeletons.gui.shared import IItemsCache

class WeekendBrawlVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    wBrawlController = dependency.descriptor(IWeekendBrawlController)

    def _getUnsuitableVehicles(self, onClear=False):
        validLevels = self.wBrawlController.getConfig().levels
        forbiddenClassTags = self.wBrawlController.getConfig().forbiddenClassTags
        forbiddenVehTypes = self.wBrawlController.getConfig().forbiddenVehTypes
        allVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        vehLevels = list(set(range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)) - set(validLevels))
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        forbiddenByClass = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLASSES(forbiddenClassTags)).itervalues()
        forbiddenByType = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(forbiddenVehTypes)).itervalues()
        eventVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        epicVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EPIC_BATTLE).itervalues()
        bobVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BOB_BATTLE).itervalues()
        return chain(vehs, forbiddenByClass, forbiddenByType, eventVehs, bobVehs, epicVehs) if not onClear else allVehs
