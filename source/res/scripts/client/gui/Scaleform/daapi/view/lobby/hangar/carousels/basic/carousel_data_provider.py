# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/carousel_data_provider.py
import typing
import BigWorld
from account_helpers.renewable_subscription import RenewableSubscription
from account_helpers.telecom_rentals import TelecomRentals
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import getStatusStrings
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from telecom_rentals_common import ROSTER_EXPIRATION_TOKEN_NAME, PARTNERSHIP_TOKEN_NAME
if typing.TYPE_CHECKING:
    from typing import Set

class _FRONT_SUPPLY_ITEMS(object):
    RENT_TANK = 0
    ALL = (RENT_TANK,)


class _SUPPLY_ITEMS(object):
    BUY_TANK = 0
    RESTORE_TANK = 1
    BUY_SLOT = 2
    ALL = (BUY_TANK, RESTORE_TANK, BUY_SLOT)


class HangarCarouselDataProvider(CarouselDataProvider):
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(HangarCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._serverSettings = self._lobbyContext.getServerSettings()
        self._setBaseCriteria()
        self._frontSupplyItems = []
        self._wotPlusVehicles = []
        self._telecomRentalsVehicles = []
        self._supplyItems = []
        self._emptySlotsCount = 0
        self._restorableVehiclesCount = 0
        self._wotPlusInfo = None
        self._telecomRentals = None
        return

    def _populate(self):
        self._wotPlusInfo = BigWorld.player().renewableSubscription
        self._wotPlusInfo.onRenewableSubscriptionDataChanged += self._onWotPlusDataChanged
        self._wotPlusInfo.onPendingRentChanged += self._onWotPlusPendingRentChanged
        self._telecomRentals = BigWorld.player().telecomRentals
        self._telecomRentals.onPendingRentChanged += self._onTelecomPendingRentChanged
        g_clientUpdateManager.addCallback('tokens', self._onTelecomRentalsChanged)
        super(HangarCarouselDataProvider, self)._populate()

    def _dispose(self):
        self._wotPlusInfo.onRenewableSubscriptionDataChanged -= self._onWotPlusDataChanged
        self._wotPlusInfo.onPendingRentChanged -= self._onWotPlusPendingRentChanged
        self._telecomRentals.onPendingRentChanged -= self._onTelecomPendingRentChanged
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(HangarCarouselDataProvider, self)._dispose()

    def _onWotPlusDataChanged(self, diff):
        if 'isEnabled' in diff:
            self.buildList()

    def _onWotPlusPendingRentChanged(self, vehCD):
        if vehCD is not None:
            self.buildList()
        return

    def _onTelecomRentalsChanged(self, diff):
        if PARTNERSHIP_TOKEN_NAME in diff or ROSTER_EXPIRATION_TOKEN_NAME in diff:
            self.buildList()

    def _onTelecomPendingRentChanged(self, vehCD):
        if vehCD is not None:
            self.buildList()
        return

    @property
    def collection(self):
        return self._vehicleItems + self._supplyItems + self._frontSupplyItems

    def getCurrentVehiclesCount(self):
        frontItems = len(self._getFrontAdditionalItemsIndexes())
        backItems = len(self._getAdditionalItemsIndexes())
        return len(self._filteredIndices) - backItems - frontItems

    def updateVehicles(self, vehiclesCDs=None, filterCriteria=None, forceUpdate=False):
        rentalVehicles = self._wotPlusVehicles + self._telecomRentalsVehicles
        changeInRentals = set(vehiclesCDs or ()).issubset(rentalVehicles)
        filterCriteria = filterCriteria or REQ_CRITERIA.EMPTY
        if vehiclesCDs:
            filterCriteria |= REQ_CRITERIA.IN_CD_LIST(vehiclesCDs)
        criteria = self._baseCriteria | filterCriteria | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP | REQ_CRITERIA.VEHICLE.WOTPLUS_RENT ^ REQ_CRITERIA.VEHICLE.TELECOM_RENT
        newRentalsVehicles = self._itemsCache.items.getVehicles(criteria).viewkeys()
        isVehicleRemoved = not set(vehiclesCDs or ()).issubset(newRentalsVehicles)
        isVehicleAdded = not set(vehiclesCDs or ()).issubset(rentalVehicles)
        if changeInRentals or isVehicleRemoved or isVehicleAdded:
            rentPendingVehCD = self._wotPlusInfo.getRentPending()
            if isVehicleAdded and rentPendingVehCD in newRentalsVehicles:
                self._wotPlusInfo.resetRentPending()
            rentPendingVehCD = self._telecomRentals.getRentsPending()
            rentPendingVehCD = rentPendingVehCD.intersection(newRentalsVehicles)
            if isVehicleAdded and rentPendingVehCD:
                self._telecomRentals.resetRentsPending(rentPendingVehCD)
            self.buildList()
            return
        super(HangarCarouselDataProvider, self).updateVehicles(vehiclesCDs, filterCriteria, forceUpdate)

    def updateSupplies(self):
        self._supplyItems = []
        self._buildSupplyItems()
        self.flashObject.invalidateItems(self._getSupplyIndices(), self._supplyItems)
        self.applyFilter()

    def clear(self):
        super(HangarCarouselDataProvider, self).clear()
        self._supplyItems = []
        self._frontSupplyItems = []

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY
        self._baseCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        self._baseCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE

    def _buildTelecomRentalVehicleItems(self):
        self._telecomRentalsVehicles = []
        rentPromotionCriteria = REQ_CRITERIA.VEHICLE.TELECOM_RENT | self._baseCriteria
        oldVehLen = len(self._vehicles)
        self._addVehicleItemsByCriteria(rentPromotionCriteria)
        totalRentVehicles = len(self._vehicles) - oldVehLen
        if totalRentVehicles > 0:
            self._telecomRentalsVehicles = [ veh.intCD for veh in self._vehicles[-totalRentVehicles:] ]

    def _buildWotPlusVehicleItems(self):
        self._wotPlusVehicles = []
        if self._wotPlusInfo.isEnabled():
            rentPromotionCriteria = REQ_CRITERIA.VEHICLE.WOTPLUS_RENT | self._baseCriteria
            oldVehLen = len(self._vehicles)
            self._addVehicleItemsByCriteria(rentPromotionCriteria)
            totalWotPlusVehicles = len(self._vehicles) - oldVehLen
            if totalWotPlusVehicles > 0:
                self._wotPlusVehicles = [ veh.intCD for veh in self._vehicles[-totalWotPlusVehicles:] ]

    def _buildRentPromitionVehicleItems(self):
        rentPromotionCriteria = REQ_CRITERIA.VEHICLE.RENT_PROMOTION | ~self._baseCriteria
        self._addVehicleItemsByCriteria(rentPromotionCriteria)

    def _buildVehicleItems(self):
        super(HangarCarouselDataProvider, self)._buildVehicleItems()
        self._buildTelecomRentalVehicleItems()
        self._buildWotPlusVehicleItems()
        self._buildRentPromitionVehicleItems()
        self._buildSupplyItems()
        self._buildFrontSupplyItems()

    def _getFrontAdditionalItemsIndexes(self):
        frontIndices = self._getFrontIndices()
        pruneIndices = set()
        if (not self._isWotPlusRentEnabled() or self._wotPlusVehicles) and (not self._isTelecomRentalsEnabled() or self._telecomRentals.getAvailableRentCount() == 0):
            pruneIndices.add(_FRONT_SUPPLY_ITEMS.RENT_TANK)
        return [ suppIdx for suppIdx in frontIndices if frontIndices.index(suppIdx) not in pruneIndices ]

    def _getAdditionalItemsIndexes(self):
        supplyIndices = self._getSupplyIndices()
        restoreEnabled = self._serverSettings.isVehicleRestoreEnabled()
        storageEnabled = self._serverSettings.isStorageEnabled()
        pruneIndices = set()
        if not self._emptySlotsCount:
            pruneIndices.add(_SUPPLY_ITEMS.BUY_TANK)
        if self._restorableVehiclesCount == 0 or not restoreEnabled or not storageEnabled:
            pruneIndices.add(_SUPPLY_ITEMS.RESTORE_TANK)
        return [ suppIdx for suppIdx in supplyIndices if supplyIndices.index(suppIdx) not in pruneIndices ]

    def _buildSupplyItems(self):
        self._supplyItems = []
        items = self._itemsCache.items
        inventory = self._itemsCache.items.inventory
        slots = items.stats.vehicleSlots
        slotPrice = items.shop.getVehicleSlotsPrice(slots)
        defaultSlotPrice = items.shop.defaults.getVehicleSlotsPrice(slots)
        self._emptySlotsCount = inventory.getFreeSlots(slots)
        criteria = REQ_CRITERIA.IN_CD_LIST(items.recycleBin.getVehiclesIntCDs()) | REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE
        self._restorableVehiclesCount = len(items.getVehicles(criteria))
        if slotPrice != defaultSlotPrice:
            discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'slotsPrices', True, Money(gold=slotPrice), Money(gold=defaultSlotPrice))
        else:
            discount = None
        smallBuySlotString, buySlotString = getStatusStrings('buySlot')
        smallBuyTankString, buyTankString = getStatusStrings('buyTank')
        smallRestoreTankString, restoreTankString = getStatusStrings('restoreTank')
        smallRestoreTankCountString, restoreTankCountString = getStatusStrings('restoreTankCount', style=text_styles.main, ctx={'count': self._restorableVehiclesCount})
        smallEmptySlotsString, emptySlotsString = getStatusStrings('buyTankEmptyCount', style=text_styles.main, ctx={'count': self._emptySlotsCount})
        self._supplyItems.append({'buyTank': True,
         'smallInfoText': text_styles.concatStylesToMultiLine(smallBuyTankString, smallEmptySlotsString),
         'infoText': text_styles.concatStylesToMultiLine(buyTankString, emptySlotsString),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK,
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_BUY_VEHICLE_NEW})
        self._supplyItems.append({'restoreTank': True,
         'smallInfoText': text_styles.concatStylesToMultiLine(smallRestoreTankString, smallRestoreTankCountString),
         'infoText': text_styles.concatStylesToMultiLine(restoreTankString, restoreTankCountString),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK,
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_RESTORE_VEHICLE})
        buySlotVO = {'buySlot': True,
         'slotPrice': slotPrice,
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_SLOT,
         'infoText': buySlotString,
         'smallInfoText': smallBuySlotString,
         'hasSale': discount is not None,
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_BUY_SLOT}
        if discount is not None:
            buySlotVO.update({'slotPriceActionData': discount})
        self._supplyItems.append(buySlotVO)
        return

    def _buildFrontSupplyItems(self):
        self._frontSupplyItems = []
        if not self._wotPlusVehicles and self._isWotPlusRentEnabled() or self._isTelecomRentalsEnabled() and not self._telecomRentals.getAvailableRentCount() == 0:
            text = MENU.TANKCAROUSEL_WOTPLUSSELECTIONAVAILABLE
            if self._telecomRentals.getRentsPending():
                text = MENU.TANKCAROUSEL_WOTPLUSSELECTIONPENDING
            self._frontSupplyItems.append({'isWotPlusSlot': True,
             'infoText': text_styles.vehicleStatusInfoText(text),
             'infoHoverText': text_styles.vehicleStatusInfoText(text),
             'smallInfoText': text_styles.vehicleStatusSimpleText(text),
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK,
             'extraImage': RES_ICONS.MAPS_ICONS_LIBRARY_RENT_ICO_BIG,
             'tooltip': TOOLTIPS.TANKS_CAROUSEL_WOT_PLUS_SLOT})

    @staticmethod
    def _isSuitableForQueue(vehicle):
        return vehicle.getCustomState() != Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE

    def _getFrontIndices(self):
        previousItemsCount = len(self._vehicles) + len(_SUPPLY_ITEMS.ALL)
        return [ previousItemsCount + idx for idx in _FRONT_SUPPLY_ITEMS.ALL ]

    def _getSupplyIndices(self):
        return [ len(self._vehicles) + idx for idx in _SUPPLY_ITEMS.ALL ]

    def _isWotPlusRentEnabled(self):
        hasWotPlusActive = self._wotPlusInfo.isEnabled()
        isRentalEnabled = self._serverSettings.isWotPlusTankRentalEnabled()
        isNotRentPending = self._wotPlusInfo.getRentPending() is None
        return hasWotPlusActive and isRentalEnabled and isNotRentPending

    def _isTelecomRentalsEnabled(self):
        hasTelecomRentalsActive = self._telecomRentals.isActive()
        isRentalEnabled = self._serverSettings.isTelecomRentalsEnabled()
        return hasTelecomRentalsActive and isRentalEnabled


class BCCarouselDataProvider(CarouselDataProvider):

    @property
    def collection(self):
        return self._vehicleItems

    def updateSupplies(self):
        pass

    def _buildVehicleItems(self):
        super(BCCarouselDataProvider, self)._buildVehicleItems()
        for vehicleItem in self._vehicleItems:
            vehicleItem['infoText'] = ''
            vehicleItem['smallInfoText'] = ''

    def setShowStats(self, showVehicleStats):
        pass

    def selectVehicle(self, idx):
        realIdx = self._filteredIndices[idx]
        self._selectedIdx = idx
        self._currentVehicle.selectVehicle(self._vehicles[realIdx].invID)

    def _buildVehicle(self, vehicle):
        vehicle.dailyXPFactor = 1
        return super(BCCarouselDataProvider, self)._buildVehicle(vehicle)
