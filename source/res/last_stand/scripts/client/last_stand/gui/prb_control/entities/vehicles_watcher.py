# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/vehicles_watcher.py
import typing
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import FORBIDDEN_VEHICLE_TAGS

class VehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)
    lsCtrl = dependency.descriptor(ILSController)

    def _getUnsuitableVehicles(self, onClear=False):
        vehConfig = self.lsCtrl.getVehiclesConfig()
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(FORBIDDEN_VEHICLE_TAGS)
        if vehConfig.allowedLevels:
            criteria |= ~REQ_CRITERIA.VEHICLE.LEVELS(vehConfig.allowedLevels)
        if vehConfig.forbiddenClassTags:
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES(vehConfig.forbiddenClassTags)
        if vehConfig.forbiddenVehicles:
            criteria |= REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehConfig.forbiddenVehicles)
        criteria ^= REQ_CRITERIA.VEHICLE.FORBIDDEN_VEHICLE_TO_BATTLE
        excludeVehicles = self.itemsCache.items.getVehicles(criteria)
        for intCD in vehConfig.allowedVehicles:
            excludeVehicles.pop(intCD, None)

        return excludeVehicles.itervalues()
