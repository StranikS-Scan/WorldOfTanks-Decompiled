# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_carousel/carousel_data_provider.py
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

def _sortedIndices(seq, getter):
    """ Sort the sequence by value fetched by getter func and return the
    list with indices of items in the original list
    
    For example, original list is: a = [3, 2, 1, 4].
    Output will be [2, 1, 0, 3], like a[2] is first, then a[1], etc.
    
    :param seq: original list
    :param getter: function that fetches values from the original list
    :return: indices in the original list
    """
    return sorted(range(len(seq)), key=lambda idx: getter(seq[idx]))


def _getStatusStyles(vStateLvl):
    """ Get text styles for small and large slots according to vehicle's state.
    """
    if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
        return (text_styles.stats, text_styles.vehicleStatusCriticalText)
    else:
        return (text_styles.stats, text_styles.vehicleStatusInfoText)


def _isLockedBackground(vState, vStateLvl):
    """
    Gets 'locked' background state for Vehicle Data VO, depending on vehicle state and state level
    :param vState: vState: one of VEHICLE_STATE
    :param vStateLvl: vStateLvl: one of VEHICLE_STATE_LEVEL
    :return: boolean result
    """
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
    """ Get status string for small and large slots.
    
    :param vState: one of VEHICLE_STATE
    :param vStateLvl: one of VEHICLE_STATE_LEVEL
    :param substitute: is provided, substitutes status string for small slot
                       (since it's too small to hold multiple strings)
    :param style: if provided, forces usage of this style
    :param ctx: keyword arguments for status text
    
    :return: tuple (status for small slot, status for large slot)
    """
    ctx = ctx or {}
    state = MENU.tankcarousel_vehiclestates(vState)
    status = ms(state, **ctx)
    if style is None:
        smallStyle, largeStyle = _getStatusStyles(vStateLvl)
    else:
        smallStyle = largeStyle = style
    if status:
        return (smallStyle(status), largeStyle(status))
    elif substitute:
        return (text_styles.middleTitle(substitute), status)
    else:
        return (status, status)
        return


def getVehicleDataVO(vehicle):
    """ Get vehicle carousel VO for the given vehicle.
    """
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
    isVehicleAvailable = vState not in Vehicle.VEHICLE_STATE.CUSTOM
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
     'clickEnabled': vehicle.isInInventory and isVehicleAvailable,
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
        return

    def hasRentedVehicles(self):
        """ Returns True if there is at least one rented vehicle, False otherwise
        """
        return bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.RENT))

    def hasEventVehicles(self):
        """ Returns True if there is at least one event vehicle, False otherwise
        """
        return bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.EVENT))

    def getTotalVehiclesCount(self):
        """ Get number of vehicles without applied filter.
        """
        return len(self._vehicles)

    def getCurrentVehiclesCount(self):
        """ Get number of vehicles with applied filter.
        """
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
        self._dispose()

    def selectVehicle(self, filteredIdx):
        """ Select one of vehicles.
        
        :param filteredIdx: index in the carousel with applied filter (i.e. what user sees)
        """
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
            self._updateVehicleItems(newVehiclesCollection)
        return

    def buildList(self):
        self.clear()
        self._buildVehicleItems()
        self.refresh()
        self.applyFilter()

    def applyFilter(self):
        """ Apply filters and sort items in the carousel.
        """
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = []
        self._selectedIdx = -1
        currentVehicleInvID = self._currentVehicle.invID
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        sortedVehicleIndices = _sortedIndices(self._vehicles, self._vehicleComparisonKey)
        for idx in sortedVehicleIndices:
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                self._filteredIndices.append(idx)
                if currentVehicleInvID == vehicle.invID:
                    self._selectedIdx = len(self._filteredIndices) - 1

        self._filteredIndices += self._getAdditionalItemsIndexes()
        needUpdate = prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self.flashObject.as_setFilter(self._filteredIndices)

    def setShowStats(self, showVehicleStats):
        self._showVehicleStats = showVehicleStats

    def _dispose(self):
        self._filter = None
        self._itemsCache = None
        self._currentVehicle = None
        self._randomStats = None
        super(CarouselDataProvider, self)._dispose()
        return

    def _getAdditionalItemsIndexes(self):
        """
        Gets any additional items indexes
        :return: list of indexes
        """
        return []

    def _buildVehicleItems(self):
        self._vehicles = []
        self._vehicleItems = []
        self._randomStats = self._itemsCache.items.getAccountDossier().getRandomStats()
        vehicleIcons = []
        vehiclesCollection = self._itemsCache.items.getVehicles(self._baseCriteria)
        for intCD, vehicle in vehiclesCollection.iteritems():
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
            battlesCount, wins, xp = vehicleRandomStats.get(intCD)
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
        """ Selectively update provided vehicles.
        
        :param vehiclesCollection: instance of ItemsCollection with vehicles to update.
        """
        updateIndices = []
        updateVehicles = []
        self._randomStats = self._itemsCache.items.getAccountDossier().getRandomStats()
        for intCD, newVehicle in vehiclesCollection.iteritems():
            for idx, oldVehicle in enumerate(self._vehicles):
                if oldVehicle.intCD == newVehicle.intCD:
                    vehicleDataVO = self._buildVehicle(newVehicle)
                    vehicleDataVO.update(self._getVehicleStats(newVehicle))
                    self._vehicleItems[idx] = vehicleDataVO
                    self._vehicles[idx] = newVehicle
                    updateIndices.append(idx)
                    updateVehicles.append(self._vehicleItems[idx])

        self.flashObject.invalidateItems(updateIndices, updateVehicles)
        self.applyFilter()

    def _getCurrentVehicles(self):
        """ Get the vehicles that left with applied filter.
        """
        return self._getFilteredVehicles(self._filter.apply)

    def _getFilteredVehicles(self, criteria):
        """ Get the vehicles that left with applied filter criteria.
        """
        return [ vehicle for vehicle in self._vehicles if criteria(vehicle) ]

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        """ Get comparison key for a vehicle.
        
        :param vehicle: instance of gui_items.Vehicle
        :return: tuple with comparison keys
        """
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)
