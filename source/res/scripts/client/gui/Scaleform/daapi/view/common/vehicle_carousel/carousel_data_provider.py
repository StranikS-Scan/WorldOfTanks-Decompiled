# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/vehicle_carousel/carousel_data_provider.py
import typing
from CurrentVehicle import g_currentVehicle
from constants import SEASON_NAME_BY_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD
from gui import GUI_NATIONS_ORDER_INDEX, makeHtmlString
from gui.Scaleform import getButtonsAssetPath
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.MENU import MENU
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES, getVehicleStateIcon, getVehicleStateAddIcon, getBattlesLeft, getSmallIconPath, getIconPath
from gui.shared.gui_items.dossier.achievements import isMarkOfMasteryAchieved
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.i18n import makeString as ms
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController, IBootcampController, IDebutBoxesController
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from skeletons.gui.shared import IItemsCache
_BONUS_ICONS_EXTRA_SMALL = {'xpFactor': backport.image(R.images.gui.maps.icons.newYear.vehicles.icons.icon_battle_exp_small()),
 'freeXPFactor': backport.image(R.images.gui.maps.icons.newYear.vehicles.icons.icon_free_exp_small()),
 'tankmenXPFactor': backport.image(R.images.gui.maps.icons.newYear.vehicles.icons.icon_crew_exp_small())}

def sortedIndices(seq, getter, reverse=False):
    return sorted(range(len(seq)), key=lambda idx: getter(seq[idx]), reverse=reverse)


def getStatusCountStyle(vStateLvl):
    if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
        return (text_styles.stats, text_styles.vehicleStatusCriticalText)
    return (text_styles.tutorial, text_styles.tutorial) if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.RENTABLE else (text_styles.stats, text_styles.vehicleStatusInfoText)


def _isLockedBackground(vState, vStateLvl):
    if vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
        result = True
    elif vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.WARNING:
        result = vState in (Vehicle.VEHICLE_STATE.BATTLE,
         Vehicle.VEHICLE_STATE.IN_PREBATTLE,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_UNIT,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         Vehicle.VEHICLE_STATE.NOT_PRESENT,
         Vehicle.VEHICLE_STATE.GROUP_IS_NOT_READY,
         Vehicle.VEHICLE_STATE.DISABLED)
    else:
        result = False
    return result


def getStatusStrings(vState, vStateLvl=Vehicle.VEHICLE_STATE_LEVEL.INFO, substitute='', style=None, styleLarge=None, ctx=None):
    ctx = ctx or {}
    state = MENU.tankcarousel_vehiclestates(vState)
    status = ms(state, **ctx)
    if style is None:
        smallStyle, largeStyle = getStatusCountStyle(vStateLvl)
    else:
        smallStyle = style
        if styleLarge is None:
            largeStyle = smallStyle
        else:
            largeStyle = styleLarge
    if status:
        return (smallStyle(status), largeStyle(status))
    else:
        return (text_styles.middleTitle(substitute), status) if substitute else (status, status)


@dependency.replace_none_kwargs(bootcampCtrl=IBootcampController, debutBoxCtrl=IDebutBoxesController, nyController=INewYearController)
def getVehicleDataVO(vehicle, bootcampCtrl=None, debutBoxCtrl=None, nyController=None):
    return _getVehicleDataVO(vehicle, bootcampCtrl, debutBoxCtrl, nyController)


def _getVehicleDataVO(vehicle, bootcampCtrl, debutBoxCtrl, nyController):
    rentInfoText = ''
    if not vehicle.isTelecomRent:
        rentInfoText = RentLeftFormatter(vehicle.rentInfo, vehicle.isPremiumIGR).getRentLeftStr()
    vState, vStateLvl = vehicle.getState()
    if vState == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL and bootcampCtrl.isInBootcamp():
        vState = Vehicle.VEHICLE_STATE.UNDAMAGED
        vStateLvl = Vehicle.VEHICLE_STATE_LEVEL.INFO
    if vehicle.isRotationApplied():
        if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.LOCKED):
            vState = Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
    if not vehicle.activeInNationGroup:
        vState = Vehicle.VEHICLE_STATE.NOT_PRESENT
    customStateExt = ''
    if vState in (Vehicle.VEHICLE_STATE.RENTABLE, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN):
        rentPackagesInfo = vehicle.getRentPackagesInfo
        if rentPackagesInfo.seasonType:
            customStateExt = '/' + SEASON_NAME_BY_TYPE.get(rentPackagesInfo.seasonType)
    smallStatus, largeStatus = getStatusStrings(vState + customStateExt, vStateLvl, substitute=rentInfoText, ctx={'icon': icons.premiumIgrSmall(),
     'battlesLeft': getBattlesLeft(vehicle)})
    smallHoverStatus, largeHoverStatus = smallStatus, largeStatus
    if vState == Vehicle.VEHICLE_STATE.RENTABLE:
        smallHoverStatus, largeHoverStatus = getStatusStrings(vState + '/hover', vStateLvl, substitute=rentInfoText, ctx={'icon': icons.premiumIgrSmall(),
         'battlesLeft': getBattlesLeft(vehicle)})
    if vehicle.dailyXPFactor > 1:
        bonusImage = getButtonsAssetPath('bonus_x{}'.format(vehicle.dailyXPFactor))
    else:
        bonusImage = ''
    if debutBoxCtrl.isEnabled() and Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE not in vState and debutBoxCtrl.isQuestsAvailableOnVehicle(vehicle):
        debutBoxesImage = getButtonsAssetPath('debut_boxes')
    else:
        debutBoxesImage = ''
    if bootcampCtrl.isInBootcamp():
        userName = backport.text(R.strings.bootcamp.award.options.tankTitle()).format(title=vehicle.shortUserName)
    else:
        userName = vehicle.shortUserName if vehicle.isPremiumIGR else vehicle.userName
    label = userName
    labelStyle = text_styles.premiumVehicleName if vehicle.isPremium else text_styles.vehicleName
    tankType = '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type
    current, maximum = vehicle.getCrystalsEarnedInfo()
    isCrystalsLimitReached = current == maximum
    showIcon = vehicle.isTelecomRent and not vehicle.rentExpiryState
    extraImage = RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG if showIcon else ''
    return {'id': vehicle.invID,
     'intCD': vehicle.intCD,
     'infoText': largeStatus,
     'infoHoverText': largeHoverStatus,
     'smallInfoText': smallStatus,
     'smallInfoHoverText': smallHoverStatus,
     'clanLock': vehicle.clanLock,
     'lockBackground': _isLockedBackground(vState, vStateLvl),
     'unlockedInBattle': False,
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
     'debutBoxesImgSource': debutBoxesImage,
     'tankType': tankType,
     'rentLeft': rentInfoText,
     'clickEnabled': vehicle.isInInventory and vehicle.activeInNationGroup or vehicle.isRentPromotion,
     'alpha': 1,
     'infoImgSrc': getVehicleStateIcon(vState),
     'additionalImgSrc': getVehicleStateAddIcon(vState),
     'isCritInfo': vStateLvl == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL,
     'isRentPromotion': vehicle.isRentPromotion and not vehicle.isRented,
     'isNationChangeAvailable': vehicle.hasNationGroup,
     'isEarnCrystals': vehicle.isEarnCrystals,
     'isCrystalsLimitReached': isCrystalsLimitReached,
     'isUseRightBtn': True,
     'tooltip': TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE,
     'isWotPlusSlot': vehicle.isWotPlus,
     'extraImage': extraImage}


class CarouselDataProvider(SortableDAAPIDataProvider):
    _battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, carouselFilter, itemsCache):
        super(CarouselDataProvider, self).__init__()
        self._setBaseCriteria()
        self._filter = carouselFilter
        self._itemsCache = itemsCache
        self._currentVehicleInvID = g_currentVehicle.invID
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
        criteria = REQ_CRITERIA.VEHICLE.RENT
        criteria |= ~REQ_CRITERIA.VEHICLE.CLAN_WARS
        criteria |= ~REQ_CRITERIA.VEHICLE.WOT_PLUS_VEHICLE
        return bool(self._getFilteredVehicles(criteria))

    def hasEventVehicles(self):
        return bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.EVENT))

    def hasBattleRoyaleVehicles(self):
        return False if not self._battleRoyaleController.isEnabled() else bool(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.BATTLE_ROYALE))

    def getTotalVehiclesCount(self):
        return len(self._vehicles)

    def getRentPromotionVehiclesCount(self):
        return len(self._getFilteredVehicles(REQ_CRITERIA.VEHICLE.RENT_PROMOTION))

    def getCurrentVehiclesCount(self):
        return len(self._filteredIndices)

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, newFilter):
        self.clear()
        self._filter = newFilter
        self._filter.load()

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
        if vehicle.isInInventory:
            self._selectedIdx = filteredIdx
            self._currentVehicleInvID = vehicle.invID
        return self._currentVehicleInvID

    def selectFilteredVehicle(self, vehicle):
        if vehicle is not None and vehicle.isInInventory:
            self._selectedIdx = -1
            self._currentVehicleInvID = vehicle.invID
        return

    def updateVehicles(self, vehiclesCDs=None, filterCriteria=None, forceUpdate=False):
        if self._itemsCache is None:
            return
        else:
            isFullResync = vehiclesCDs is None and filterCriteria is None
            filterCriteria = filterCriteria or REQ_CRITERIA.EMPTY
            if vehiclesCDs:
                filterCriteria |= REQ_CRITERIA.IN_CD_LIST(vehiclesCDs)
            criteria = self._baseCriteria | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
            newVehiclesCollection = self._itemsCache.items.getVehicles(criteria | filterCriteria)
            oldVehiclesCDs = [ vehicle.intCD for vehicle in self._vehicles ]
            isVehicleRemoved = not set(vehiclesCDs or ()).issubset(newVehiclesCollection.viewkeys())
            isVehicleAdded = not set(vehiclesCDs or ()).issubset(oldVehiclesCDs)
            if isFullResync or isVehicleAdded or isVehicleRemoved:
                self.buildList()
            else:
                self._updateVehicleItems(newVehiclesCollection.values(), forceUpdate)
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

    def applyFilter(self, forceApply=False):
        prevFilteredIndices = self._filteredIndices[:]
        prevSelectedIdx = self._selectedIdx
        self._filteredIndices = self._getFrontAdditionalItemsIndexes()
        self._selectedIdx = -1
        visibleVehiclesIntCDs = [ vehicle.intCD for vehicle in self._getCurrentVehicles() ]
        sortedVehicleIndices = self._getSortedIndices()
        self._filteredIndices += self._getBeforeAdditionalItemsIndexes()
        for idx in sortedVehicleIndices:
            vehicle = self._vehicles[idx]
            if vehicle.intCD in visibleVehiclesIntCDs:
                self._filteredIndices.append(idx)
                if self._currentVehicleInvID == vehicle.invID:
                    self._selectedIdx = len(self._filteredIndices) - 1

        self._filteredIndices += self._getAdditionalItemsIndexes()
        needUpdate = forceApply or prevFilteredIndices != self._filteredIndices or prevSelectedIdx != self._selectedIdx
        if needUpdate:
            self._filterByIndices()

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY

    def _filterByIndices(self):
        if self.flashObject is not None:
            self.flashObject.as_setFilter(self._filteredIndices)
        return

    def _getSortedIndices(self):
        return self._getCachedSortedIndices(False)

    def _getCachedSortedIndices(self, reverse=False):
        if not self.__sortedIndices:
            self.__sortedIndices = sortedIndices(self._vehicles, self._vehicleComparisonKey, reverse)
        return self.__sortedIndices

    def _dispose(self):
        self._filter = None
        self._itemsCache = None
        self._randomStats = None
        super(CarouselDataProvider, self)._dispose()
        return

    def _getFrontAdditionalItemsIndexes(self):
        return []

    def _getAdditionalItemsIndexes(self):
        return []

    def _getBeforeAdditionalItemsIndexes(self):
        return []

    def _syncRandomStats(self):
        self._randomStats = self._itemsCache.items.getAccountDossier().getRandomStats()

    def _addVehicleItemsByCriteria(self, criteria):
        if not self._itemsCache.isSynced():
            return
        vehiclesDict = self._itemsCache.items.getVehicles(criteria)
        vehicleIcons = []
        for vehicle in vehiclesDict.itervalues():
            vehicleIcons.append(vehicle.icon)
            self._vehicles.append(vehicle)
            vehicleDataVO = self._buildVehicle(vehicle)
            vehicleDataVO.update(self._getVehicleStats(vehicle))
            self._vehicleItems.append(vehicleDataVO)

        self.app.imageManager.loadImages(vehicleIcons)

    def _buildVehicleItems(self):
        self._vehicles = []
        self.__resetSortedIndices()
        self._vehicleItems = []
        self._syncRandomStats()
        self._addCriteria()

    def _addCriteria(self):
        self._addVehicleItemsByCriteria(self._baseCriteria | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP | ~REQ_CRITERIA.VEHICLE.TELECOM_RENT)

    def _buildVehicle(self, vehicle):
        vo = getVehicleDataVO(vehicle)
        return vo

    def _getVehicleStats(self, vehicle):
        if vehicle.isOnlyForBattleRoyaleBattles:
            return {'statsText': '',
             'visibleStats': False}
        else:
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
                winsEfficiencyStr = backport.getIntegralFormat(round(winsEfficiency)) + '%'
                winsText = makeHtmlString('html_templates:lobby/tank_carousel/statistic', 'wins', ctx={'wins': winsEfficiencyStr})
                vehDossier = self._itemsCache.items.getVehicleDossier(intCD)
                vehStats = vehDossier.getTotalStats()
                marksOnGun = vehStats.getAchievement(MARK_ON_GUN_RECORD)
                marksOnGunText = ''
                if marksOnGun.getValue() > 0:
                    marksOnGunText = makeHtmlString('html_templates:lobby/tank_carousel/statistic', 'marksOnGun', ctx={'count': marksOnGun.getValue()})
                template = '{}    {}  {}' if vehicle.isEarnCrystals else '{}   {}     {}'
                statsText = template.format(markOfMasteryText, winsText, marksOnGunText)
            else:
                statsText = '#menu:tankCarousel/statsStatus/unavailable'
            return {'statsText': text_styles.stats(statsText),
             'visibleStats': self._showVehicleStats}

    def _updateVehicleItems(self, vehiclesCollection, forceUpdate=False):
        updateIndices = []
        updateVehicles = []
        self._syncRandomStats()
        oldVehs = {veh.intCD:(idx, veh) for idx, veh in enumerate(self._vehicles)}
        for newVehicle in vehiclesCollection:
            intCD = newVehicle.intCD
            if intCD in oldVehs:
                idx, _ = oldVehs[intCD]
                vehicleDataVO = self._buildVehicle(newVehicle)
                vehicleDataVO.update(self._getVehicleStats(newVehicle))
                self._vehicleItems[idx] = vehicleDataVO
                self._vehicles[idx] = newVehicle
                updateIndices.append(idx)
                updateVehicles.append(self._vehicleItems[idx])

        if updateVehicles:
            self.__resetSortedIndices()
        if self.flashObject is not None:
            self.flashObject.invalidateItems(updateIndices, updateVehicles)
        self.applyFilter(forceApply=forceUpdate)
        return

    def _getCurrentVehicles(self):
        return self._getFilteredVehicles(self._filter.apply)

    def _getFilteredVehicles(self, criteria):
        return [ vehicle for vehicle in self._vehicles if criteria(vehicle) ]

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isInInventory,
         vehicle.isOnlyForClanWarsBattles,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def __resetSortedIndices(self):
        self.__sortedIndices = []
