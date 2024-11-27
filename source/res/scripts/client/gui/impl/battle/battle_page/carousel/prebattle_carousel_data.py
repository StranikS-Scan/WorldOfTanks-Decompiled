# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/carousel/prebattle_carousel_data.py
from collections import namedtuple
from account_helpers.AccountSettings import COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2, COMP7_CAROUSEL_FILTER_CLIENT_1, AccountSettings
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import RoleCriteriesGroup, CarouselFilter
from gui.battle_control.gui_vehicle_builder import VehicleBuilder
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.vehicles import getVehicleType
from skeletons.gui.shared.gui_items import IGuiItemsFactory

def getComp7CarouselVehicleDataVO(vehicle):
    return {'vehicleName': vehicle.shortUserName,
     'favorite': vehicle.isFavorite,
     'enabled': True,
     'roleName': vehicle.roleLabel if vehicle.roleLabel != 'role_SPG' else ''}


class _InBattleRentedCriteriesGroup(RoleCriteriesGroup):

    def __init__(self, rentedList):
        super(_InBattleRentedCriteriesGroup, self).__init__()
        self.__rentedList = rentedList

    def update(self, filters):
        self._criteria = REQ_CRITERIA.EMPTY
        self._setNationsCriteria(filters)
        self._setClassesCriteria(filters)
        self._setRentedCriteria(filters)
        self._setFavoriteVehicleCriteria(filters)
        self._setVehicleNameCriteria(filters)
        self._setRolesCriteria(filters)

    def _setRentedCriteria(self, filters):
        if not filters['rented']:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__rentedList)


class PrebattleCarouselFilter(CarouselFilter):

    def __init__(self):
        self.__rentedList = []
        super(PrebattleCarouselFilter, self).__init__()
        self._serverSections = (COMP7_CAROUSEL_FILTER_1, COMP7_CAROUSEL_FILTER_2)
        self._clientSections = (COMP7_CAROUSEL_FILTER_CLIENT_1,)

    def save(self):
        pass

    def load(self):
        filters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            filters.update(AccountSettings.getFilterDefault(section))

        self._filters = filters
        self.update(filters, save=False)

    def setRentedList(self, rentedList):
        self.__rentedList = rentedList
        self._setCriteriaGroups()
        self._updateCriteriesGroups()

    def _setCriteriaGroups(self):
        self._criteriesGroups = (_InBattleRentedCriteriesGroup(self.__rentedList), RoleCriteriesGroup())


class PrebattleCarouselDataProvider(CarouselDataProvider):
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _RawVehicleData = namedtuple('_RawVehicleData', ('strCD', 'settings', 'isElite', 'isRented'))

    def __init__(self, carouselFilter, itemsCache):
        super(PrebattleCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self.__vehiclesData = {}
        self.__selectedCD = None
        return

    def getSelectedCD(self):
        return self.__selectedCD

    def applyFilter(self, forceApply=False):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        for idx in self._getSortedIndices():
            if idx >= len(self._vehicles):
                continue
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                self._filteredIndices.append(idx)
                if self.__selectedCD == vehicle.intCD:
                    self._selectedIdx = len(self._filteredIndices) - 1

        needUpdate = forceApply or prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

    def getVehicleCDByIdx(self, filteredIdx):
        realIdx = self._filteredIndices[filteredIdx]
        vehicle = self._vehicles[realIdx]
        return vehicle.intCD

    def setVehicles(self, vehiclesList):
        self.__vehiclesData = {}
        rentedList = []
        for v in vehiclesList:
            vehData = self._RawVehicleData(v['compDescr'], v['settings'], bool(v['isElite']), bool(v['isRent']))
            intCD = getVehicleType(vehData.strCD).compactDescr
            self.__vehiclesData[intCD] = vehData
            if vehData.isRented:
                rentedList.append(intCD)

        self._filter.setRentedList(rentedList)
        self.buildList()

    def setCurrentVehicle(self, vehicleCD):
        if vehicleCD is None:
            return
        else:
            for vehicle in self._vehicles:
                if vehicle.compactDescr == vehicleCD:
                    self.__selectedCD = vehicleCD
                    self.applyFilter()
                    self.refresh()
                    break

            return

    def _buildVehicleItems(self):
        self._vehicles = []
        self._vehicleItems = []
        for vehicleData in self.__vehiclesData.itervalues():
            vehicle = self.__makeGuiVehicle(vehicleData)
            self._vehicles.append(vehicle)

    def getGetFilteredVehiclesCDs(self):
        return {self._vehicles[idx].compactDescr for idx in self._filteredIndices if idx < len(self._vehicles)}

    def getSortedVehicles(self):
        return [ self._vehicles[idx] for idx in self._getSortedIndices() if idx < len(self._vehicles) ]

    @property
    def collection(self):
        return self._vehicles

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.userName)

    @staticmethod
    def __makeGuiVehicle(vehicleData):
        builder = VehicleBuilder()
        builder.setStrCD(vehicleData.strCD)
        builder.setSettings(vehicleData.settings)
        return builder.getResult()
