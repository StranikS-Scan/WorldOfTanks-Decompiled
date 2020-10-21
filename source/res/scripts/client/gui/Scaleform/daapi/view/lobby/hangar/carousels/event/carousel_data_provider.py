# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/event/carousel_data_provider.py
from account_helpers.AccountSettings import EVENT_CURRENT_VEHICLE, AccountSettings
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui import makeHtmlString
from shared_utils import findFirst
from helpers.time_utils import getTimeDeltaFromNow
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.formatters.time_formatters import getHWTimeLeftString
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from constants import HE19EnergyPurposes

class EventCarouselDataProvider(HangarCarouselDataProvider):
    gameEventController = dependency.descriptor(IGameEventController)
    _ORDER = []

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(EventCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self.__vehiclesController = self.gameEventController.getVehiclesController()
        self.__vehiclesWithoutEnergy = set()
        vehiclesForRent = self.__vehiclesController.getVehiclesForRent()
        self._baseCriteria = REQ_CRITERIA.VEHICLE.EVENT ^ REQ_CRITERIA.IN_CD_LIST(vehiclesForRent.keys())
        EventCarouselDataProvider._ORDER = self.__vehiclesController.getVehiclesOrder()

    def selectVehicle(self, filteredIdx):
        realIdx = self._filteredIndices[filteredIdx]
        vehicle = self._vehicles[realIdx]
        self._selectedIdx = filteredIdx
        self._currentVehicle.selectEventVehicle(vehicle.invID if vehicle.isInInventory else -vehicle.intCD)

    def applyFilter(self, forceApply=False):
        prevSelectedIdx = self._selectedIdx
        self._selectedIdx = -1
        vehInvIDOrCD = AccountSettings.getFavorites(EVENT_CURRENT_VEHICLE)
        if vehInvIDOrCD < 0:
            currentVehicle = self._itemsCache.items.getStockVehicle(-vehInvIDOrCD, useInventory=True)
        else:
            currentVehicle = self._itemsCache.items.getVehicle(vehInvIDOrCD)
        self._filteredIndices = self._getSortedIndices()
        self._selectedIdx = self.findVehicleFilteredIndex(currentVehicle)
        if prevSelectedIdx != self._selectedIdx:
            self._filterByIndices()

    def findVehicleFilteredIndex(self, vehicle):
        try:
            vehInvIDOrCD = AccountSettings.getFavorites(EVENT_CURRENT_VEHICLE)
            if vehInvIDOrCD < 0:
                vehicle = self._itemsCache.items.getStockVehicle(-vehInvIDOrCD, useInventory=True)
            vehicleIdx = self._vehicles.index(vehicle)
            filteredIdx = self._filteredIndices.index(vehicleIdx)
            return filteredIdx
        except ValueError:
            return -1

    def _populate(self):
        super(EventCarouselDataProvider, self)._populate()
        self.__vehiclesController.onTimeToRepairChanged += self.__vehiclesTimeChanged

    def _dispose(self):
        self.__vehiclesController.onTimeToRepairChanged -= self.__vehiclesTimeChanged
        super(EventCarouselDataProvider, self)._dispose()

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (cls._ORDER.index(vehicle.intCD),)

    def _buildVehicle(self, vehicle):
        vo = super(EventCarouselDataProvider, self)._buildVehicle(vehicle)
        isInInventory = vehicle.isInInventory
        vo['clickEnabled'] = True
        vo['eventLock'] = not isInInventory
        if not isInInventory:
            vo['infoText'] = ''
            vo['infoHoverText'] = ''
        isEventPremium = VEHICLE_TAGS.EVENT_PREMIUM_VEHICLE in vehicle.tags
        vo['xpImgSource'] = RES_ICONS.MAPS_ICONS_EVENT_CAROUSELEX2 if isEventPremium else ''
        timeToRecharge = self.__vehiclesController.getTimeToRecharge(HE19EnergyPurposes.healing.name, vo.get('intCD', 0))
        self.__updateVehicleTime(vo, getTimeDeltaFromNow(timeToRecharge))
        return vo

    def _buildRentPromitionVehicleItems(self):
        pass

    def _buildSupplyItems(self):
        self._supplyItems = []

    def _getSupplyIndices(self):
        return []

    def __updateVehicleTime(self, vo, timeLeft):
        intCD = vo.get('intCD', 0)
        vo['lockBackground'] = False
        if not self.__vehiclesController.hasEnergy(HE19EnergyPurposes.healing.name, intCD):
            timeStr = self.__getTimeLeftString(timeLeft)
            vo['infoText'] = timeStr
            vo['infoHoverText'] = timeStr
            self.__vehiclesWithoutEnergy.add(intCD)
            vo['lockBackground'] = True
        elif intCD in self.__vehiclesWithoutEnergy:
            vo['infoText'] = ''
            vo['infoHoverText'] = ''
            self.__vehiclesWithoutEnergy.discard(intCD)

    def __vehiclesTimeChanged(self, vehiclesTime):
        updateIndices = []
        updateVehicles = []
        for idx, vehicle in enumerate(self._getCurrentVehicles()):
            intCD = vehicle.intCD
            if intCD in self.__vehiclesWithoutEnergy or not self.__vehiclesController.hasEnergy(HE19EnergyPurposes.healing.name, intCD):
                vo = findFirst(lambda vo, cd=intCD: vo['intCD'] == cd, self._vehicleItems, None)
                if vo:
                    self.__updateVehicleTime(vo, vehiclesTime.get(intCD, 0))
                    updateVehicles.append(vo)
                    updateIndices.append(idx)

        if updateVehicles and updateIndices:
            self.flashObject.invalidateItems(updateIndices, updateVehicles)
        return

    def __getTimeLeftString(self, deltaTime):
        return makeHtmlString('html_templates:lobby/textStyle/', 'vehicleStatusInfoText', {'message': getHWTimeLeftString(deltaTime)})
