# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/vehicles_watcher.py
from itertools import chain
import logging
import typing
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BaseVehiclesWatcher(object):

    def __init__(self):
        self.__isWatching = False

    def start(self):
        self.__setUnsuitableState()
        g_clientUpdateManager.addCallbacks({'inventory': self._update,
         'eventsData': self._update})
        self.__isWatching = True
        _logger.info("BaseVehiclesWatcher:start() self = '%r'", self)

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._clearUnsuitableState()
        self.__isWatching = False
        _logger.info("BaseVehiclesWatcher:stop() self = '%r'", self)

    def _getUnsuitableVehicles(self, onClear=False):
        raise NotImplementedError

    def _update(self, *_):
        if self.__isWatching:
            self.__setUnsuitableState()

    def __setUnsuitableState(self):
        vehicles = self._getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def _clearUnsuitableState(self):
        vehicles = self._getUnsuitableVehicles(True)
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)


class LimitedLevelVehiclesWatcher(BaseVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LimitedLevelVehiclesWatcher, self).__init__()
        self.__validLevels = None
        return

    def stop(self):
        super(LimitedLevelVehiclesWatcher, self).stop()
        self.__validLevels = None
        return

    def _getUnsuitableVehicles(self, onClear=False):
        newValidLevels = self._getValidLevels()
        if newValidLevels != self.__validLevels and not onClear:
            self._clearUnsuitableState()
        self.__validLevels = self.__validLevels if onClear else newValidLevels
        vehLevels = list(set(range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)) - set(self.__validLevels)) if self.__validLevels is not None else []
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        return vehs

    def _getValidLevels(self):
        raise NotImplementedError


class ForbiddenVehiclesWatcher(BaseVehiclesWatcher):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ForbiddenVehiclesWatcher, self).__init__()
        self.__forbiddenVehicleClasses = None
        self.__forbiddenVehicleTypes = None
        return

    def stop(self):
        super(ForbiddenVehiclesWatcher, self).stop()
        self.__forbiddenVehicleTypes = None
        self.__forbiddenVehicleClasses = None
        return

    def _getUnsuitableVehicles(self, onClear=False):
        newForbiddenTypes = self._getForbiddenVehicleTypes()
        newForbiddenClasses = self._getForbiddenVehicleClasses()
        forbiddenListChanged = newForbiddenTypes != self.__forbiddenVehicleTypes or newForbiddenClasses != self.__forbiddenVehicleClasses
        if forbiddenListChanged and not onClear:
            self._clearUnsuitableState()
        self.__forbiddenVehicleTypes = self.__forbiddenVehicleTypes if onClear else newForbiddenTypes
        self.__forbiddenVehicleClasses = self.__forbiddenVehicleClasses if onClear else newForbiddenClasses
        classVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLASSES(self.__forbiddenVehicleClasses)).itervalues() if self.__forbiddenVehicleClasses is not None else []
        typeVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__forbiddenVehicleTypes)).itervalues() if self.__forbiddenVehicleTypes is not None else []
        return chain(classVehs, typeVehs)

    def _getForbiddenVehicleClasses(self):
        raise NotImplementedError

    def _getForbiddenVehicleTypes(self):
        raise NotImplementedError
