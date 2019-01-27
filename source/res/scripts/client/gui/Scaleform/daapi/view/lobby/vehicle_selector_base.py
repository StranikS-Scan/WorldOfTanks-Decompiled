# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_selector_base.py
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.Scaleform.genConsts.VEHICLE_SELECTOR_CONSTANTS import VEHICLE_SELECTOR_CONSTANTS
from gui.shared.formatters.vehicle_filters import packVehicleTypesFilter, packVehicleLevelsFilter, packNationsFilter
from gui.shared.utils.requesters import REQ_CRITERIA

class VehicleSelectorBase(object):

    def __init__(self):
        self.__filters = None
        self._levelsRange = range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)
        self.showNotReadyVehicles = True
        self._filterVisibility = VEHICLE_SELECTOR_CONSTANTS.VISIBLE_ALL
        self._compatibleOnlyLabel = ''
        return

    def getFilters(self):
        return self.__filters

    def _updateFilter(self, nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False):
        self.__filters = {'nation': nation,
         'vehicleType': vehicleType,
         'isMain': isMain,
         'level': level,
         'compatibleOnly': compatibleOnly}

    def _updateData(self, allVehicles, compatiblePredicate=lambda vo: vo.get('enabled')):
        criteria = REQ_CRITERIA.EMPTY
        criteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_IGR_RENT
        criteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        if not self.showNotReadyVehicles:
            criteria |= REQ_CRITERIA.VEHICLE.READY
        if self.__filters:
            nations, levels, classes = self._parseFilters()
            if nations:
                criteria |= REQ_CRITERIA.NATIONS(nations)
            if classes:
                criteria |= REQ_CRITERIA.VEHICLE.CLASSES(classes)
            if self.__filters['isMain']:
                criteria |= REQ_CRITERIA.VEHICLE.FAVORITE
            if levels:
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS(levels)
        filteredVehicles = allVehicles.filter(criteria)
        if self.__filters.get('compatibleOnly', True):
            predicate = compatiblePredicate
        else:
            predicate = lambda vo: True
        result = []
        for v in filteredVehicles.itervalues():
            vo = self._makeVehicleVOAction(v)
            if predicate(vo):
                result.append(vo)

        return result

    def _parseFilters(self):
        nations, levels, classes = (None, None, None)
        if 'nation' in self.__filters and self.__filters['nation'] != -1:
            nations = [self.__filters['nation']]
        if 'level' in self.__filters and self.__filters['level'] != -1:
            levels = [self.__filters['level']]
        if 'vehicleType' in self.__filters and self.__filters['vehicleType'] != 'none':
            classes = [self.__filters['vehicleType']]
        return (nations, levels, classes)

    def _initFilter(self, nation=-1, vehicleType='none', isMain=False, level=-1, compatibleOnly=False):
        levelsDP = packVehicleLevelsFilter(self._levelsRange)
        if len(levelsDP) <= 2:
            self._filterVisibility ^= VEHICLE_SELECTOR_CONSTANTS.VISIBLE_LEVEL
        filtersData = {'vehicleTypesDP': packVehicleTypesFilter(defaultVehType='none'),
         'levelsDP': levelsDP,
         'nation': nation,
         'nationDP': packNationsFilter(),
         'vehicleType': vehicleType,
         'isMain': isMain,
         'level': level,
         'compatibleOnly': compatibleOnly,
         'visibility': self._filterVisibility,
         'compatibleOnlyLabel': self._compatibleOnlyLabel}
        return filtersData

    def _makeVehicleVOAction(self, vehicle):
        raise NotImplementedError
