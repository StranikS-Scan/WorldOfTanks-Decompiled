# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/vehicle_carousel/carousel_data_provider.py
import BigWorld
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from gui import GUI_NATIONS_ORDER_INDEX, makeHtmlString
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES, getVehicleStateIcon, getBattlesLeft, getSmallIconPath, getIconPath
from gui.shared.gui_items.dossier.achievements.MarkOfMasteryAchievement import isMarkOfMasteryAchieved
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.i18n import makeString as ms

def sortedIndices(seq, getter, reverse=False):
    return sorted(range(len(seq)), key=lambda idx: getter(seq[idx]), reverse=reverse)


def getStatusCountStyle(vStateLvl):
    return (text_styles.stats, text_styles.vehicleStatusCriticalText) if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL else (text_styles.stats, text_styles.vehicleStatusInfoText)


def _isLockedBackground(vState, vStateLvl):
    if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
        result = True
    elif vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.WARNING:
        result = vState in (Vehicle.VEHICLE_STATE.BATTLE,
         Vehicle.VEHICLE_STATE.IN_PREBATTLE,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         Vehicle.VEHICLE_STATE.NOT_PRESENT,
         Vehicle.VEHICLE_STATE.GROUP_IS_NOT_READY)
    else:
        result = False
    return result


def getStatusStrings(vState, vStateLvl=Vehicle.VEHICLE_STATE_LEVEL.INFO, substitute='', style=None, ctx=None):
    ctx = ctx or {}
    state = MENU.tankcarousel_vehiclestates(vState)
    status = ms(state, **ctx)
    if style is None:
        smallStyle, largeStyle = getStatusCountStyle(vStateLvl)
    else:
        smallStyle = largeStyle = style
    if status:
        return (smallStyle(status), largeStyle(status))
    else:
        return (text_styles.middleTitle(substitute), status) if substitute else (status, status)


def getVehicleDataVO(vehicle):
    rentInfoText = RentLeftFormatter(vehicle.rentInfo, vehicle.isPremiumIGR).getRentLeftStr()
    vState, vStateLvl = vehicle.getState()
    if vehicle.isRotationApplied():
        if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.LOCKED):
            vState = Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
    smallStatus, largeStatus = getStatusStrings(vState, vStateLvl, substitute=rentInfoText, ctx={'icon': icons.premiumIgrSmall(),
     'battlesLeft': getBattlesLeft(vehicle)})
    if vehicle.dailyXPFactor > 1:
        bonusImage = getButtonsAssetPath('bonus_x{}'.format(vehicle.dailyXPFactor))
    else:
        bonusImage = ''
    label = vehicle.shortUserName if vehicle.isPremiumIGR else vehicle.userName
    labelStyle = text_styles.premiumVehicleName if vehicle.isPremium else text_styles.vehicleName
    return {'id': vehicle.invID,
     'intCD': vehicle.intCD,
     'infoText': largeStatus,
     'smallInfoText': smallStatus,
     'clanLock': vehicle.clanLock,
     'lockBackground': _isLockedBackground(vState, vStateLvl),
     'icon': vehicle.icon,
     'iconAlt': getIconPath('noImage'),
     'iconSmall': vehicle.iconSmall,
     'iconSmallAlt': getSmallIconPath('noImage'),
     'label': labelStyle(label),
     'level': vehicle.level,
     'premium': vehicle.isPremium,
     'favorite': vehicle.isFavorite,
     'nation': vehicle.nationID,
     'xpImgSource': bonusImage,
     'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
     'rentLeft': rentInfoText,
     'clickEnabled': vehicle.isInInventory,
     'alpha': 1,
     'infoImgSrc': getVehicleStateIcon(vState),
     'isCritInfo': vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL}


class CarouselDataProvider(SortableDAAPIDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(CarouselDataProvider, self).__init__()
        self._baseCriteria = REQ_CRITERIA.INVENTORY
        self._filter = carouselFilter
        self._itemsCache = itemsCache
        self._currentVehicle = currentVehicle
        self._vehicles = []
        self._vehicleItems = []
        self._filteredIndices = []
        self._selectedIdx = -1
        self._showVehicleStats = False
        self._randomStats = None
        self._filter.load()
        self.__sortedIndices = []
        return

    def hasRentedVehicles(self):
        return bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.RENT))

    def hasEventVehicles(self):
        return bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.EVENT))

    def getTotalVehiclesCount(self):
        return len(self._vehicles)

    def getCurrentVehiclesCount(self):
        return len(self._filteredIndices)

    @property
    def filter(self):
        return self._filter

    @property
    def collection(self):
        return self._vehicleItems

    def pyGetSelectedIdx(self):
        return self._selectedIdx

    def emptyItem(self):
        return None

    def clear(self):
        self._vehicles = []
        self._vehicleItems = []
        self._filteredIndices = []
        self._selectedIdx = -1

    def fini(self):
        self.clear()
        self.destroy()

    def selectVehicle(self, filteredIdx):
        realIdx = self._filteredIndices[filteredIdx]
        vehicle = self._vehicles[realIdx]
        self._selectedIdx = filteredIdx
        self._currentVehicle.selectVehicle(vehicle.invID)

    def updateVehicles(self, vehiclesCDs=None, filterCriteria=None):
        isFullResync = vehiclesCDs is None and filterCriteria is None
        filterCriteria = filterCriteria or REQ_CRITERIA.EMPTY
        if vehiclesCDs:
            filterCriteria |= REQ_CRITERIA.IN_CD_LIST(vehiclesCDs)
        newVehiclesCollection = self._itemsCache.items.getVehicles(self._baseCriteria | filterCriteria)
        oldVehiclesCDs = [ vehicle.intCD for vehicle in self._vehicles ]
        isVehicleRemoved = not set(vehiclesCDs or ()).issubset(newVehiclesCollection.viewkeys())
        isVehicleAdded = not set(vehiclesCDs or ()).issubset(oldVehiclesCDs)
        if isFullResync or isVehicleAdded or isVehicleRemoved:
            self.buildList()
        else:
            self._updateVehicleItems(newVehiclesCollection.values())
        return

    def setShowStats(self, showVehicleStats):
        self._showVehicleStats = showVehicleStats

    def findVehicleFilteredIndex(self, vehicle):
        try:
            vehicleIdx = self._vehicles.index(vehicle)
            filteredIdx = self._filteredIndices.index(vehicleIdx)
            return filteredIdx
        except ValueError:
            return -1

    def buildList(self):
        self.clear()
        self._buildVehicleItems()
        self.refresh()
        self.applyFilter()

    def applyFilter(self):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        currentVehicleInvID = self._currentVehicle.invID
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        sortedVehicleIndices = self._getSortedIndices()
        for idx in sortedVehicleIndices:
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                self._filteredIndices.append(idx)
                if currentVehicleInvID == vehicle.invID:
                    self._selectedIdx = len(self._filteredIndices) - 1

        self._filteredIndices += self._getAdditionalItemsIndexes()
        needUpdate = prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

    def _filterByIndices(self):
        self.flashObject.as_setFilter(self._filteredIndices)

    def _getSortedIndices(self):
        return self._getCachedSortedIndices(False)

    def _getCachedSortedIndices(self, reverse=False):
        if not self.__sortedIndices:
            self.__sortedIndices = sortedIndices(self._vehicles, self._vehicleComparisonKey, reverse)
        return self.__sortedIndices

    def _dispose(self):
        self._filter = None
        self._itemsCache = None
        self._currentVehicle = None
        self._randomStats = None
        super(CarouselDataProvider, self)._dispose()
        return

    def _getAdditionalItemsIndexes(self):
        return []

    def _syncRandomStats(self):
        self._randomStats = self._itemsCache.items.getAccountDossier().getRandomStats()

    def _buildVehicleItems(self):
        self._vehicles = []
        self.__resetSortedIndices()
        self._vehicleItems = []
        self._syncRandomStats()
        vehicleIcons = []
        for vehicle in self._itemsCache.items.getVehicles(self._baseCriteria).itervalues():
            vehicleIcons.append(vehicle.icon)
            self._vehicles.append(vehicle)
            vehicleDataVO = self._buildVehicle(vehicle)
            vehicleDataVO.update(self._getVehicleStats(vehicle))
            self._vehicleItems.append(vehicleDataVO)

        self.app.imageManager.loadImages(vehicleIcons)

    def _buildVehicle(self, vehicle):
        vo = getVehicleDataVO(vehicle)
        return vo

    def _getVehicleStats(self, vehicle):
        intCD = vehicle.intCD
        vehicleRandomStats = self._randomStats.getVehicles() if self._randomStats is not None else {}
        if intCD in vehicleRandomStats:
            battlesCount, wins, _ = vehicleRandomStats.get(intCD)
            markOfMastery = self._randomStats.getMarkOfMasteryForVehicle(intCD)
            if isMarkOfMasteryAchieved(markOfMastery):
                markOfMasteryText = makeHtmlString('html_templates:lobby/tank_carousel/statistic', 'markOfMastery', ctx={'markOfMastery': markOfMastery})
            else:
                markOfMasteryText = ''
            winsEfficiency = 100.0 * wins / battlesCount if battlesCount else 0
            winsEfficiencyStr = BigWorld.wg_getIntegralFormat(round(winsEfficiency)) + '%'
            winsText = makeHtmlString('html_templates:lobby/tank_carousel/statistic', 'wins', ctx={'wins': winsEfficiencyStr})
            vehDossier = self._itemsCache.items.getVehicleDossier(intCD)
            vehStats = vehDossier.getTotalStats()
            marksOnGun = vehStats.getAchievement(MARK_ON_GUN_RECORD)
            marksOnGunText = ''
            if marksOnGun.getValue() > 0:
                marksOnGunText = makeHtmlString('html_templates:lobby/tank_carousel/statistic', 'marksOnGun', ctx={'count': marksOnGun.getValue()})
            statsText = '{}   {}     {}'.format(markOfMasteryText, winsText, marksOnGunText)
        else:
            statsText = '#menu:tankCarousel/statsStatus/unavailable'
        return {'statsText': text_styles.stats(statsText),
         'visibleStats': self._showVehicleStats}

    def _updateVehicleItems(self, vehiclesCollection):
        updateIndices = []
        updateVehicles = []
        self._syncRandomStats()
        for newVehicle in vehiclesCollection:
            for idx, oldVehicle in enumerate(self._vehicles):
                if oldVehicle.intCD == newVehicle.intCD:
                    vehicleDataVO = self._buildVehicle(newVehicle)
                    vehicleDataVO.update(self._getVehicleStats(newVehicle))
                    self._vehicleItems[idx] = vehicleDataVO
                    self._vehicles[idx] = newVehicle
                    updateIndices.append(idx)
                    updateVehicles.append(self._vehicleItems[idx])

        if updateVehicles:
            self.__resetSortedIndices()
        self.flashObject.invalidateItems(updateIndices, updateVehicles)
        self.applyFilter()

    def _getCurrentVehicles(self):
        return self._getFilteredVehicles(self._filter.apply)

    def _getFilteredVehicles(self, criteria):
        return [ vehicle for vehicle in self._vehicles if criteria(vehicle) ]

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def __resetSortedIndices(self):
        self.__sortedIndices = []
