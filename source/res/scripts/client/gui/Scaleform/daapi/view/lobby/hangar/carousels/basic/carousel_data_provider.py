# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/carousel_data_provider.py
import typing
import BigWorld
from account_helpers.telecom_rentals import TelecomRentals
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as _CAPS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import getStatusStrings
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import FILTER_KEYS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
from telecom_rentals_common import ROSTER_EXPIRATION_TOKEN_NAME, PARTNERSHIP_TOKEN_NAME

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
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

    def __init__(self, carouselFilter, itemsCache):
        super(HangarCarouselDataProvider, self).__init__(carouselFilter, itemsCache)
        self._serverSettings = self._lobbyContext.getServerSettings()
        self._frontSupplyItems = []
        self._telecomRentalsVehicles = []
        self._supplyItems = []
        self._emptySlotsCount = 0
        self._restorableVehiclesCount = 0
        self._telecomRentals = None
        self._dynamicFiltersState = {}
        self._setBaseCriteria()
        self.updateDynamicFilters()
        return

    @property
    def collection(self):
        return self._vehicleItems + self._supplyItems + self._frontSupplyItems

    def getCurrentVehiclesCount(self):
        frontItems = len(self._getFrontAdditionalItemsIndexes())
        backItems = len(self._getAdditionalItemsIndexes())
        return len(self._filteredIndices) - backItems - frontItems

    def getHiddenDynamicFilters(self):
        return sorted((key for key, state in self._dynamicFiltersState.iteritems() if not state))

    def clear(self):
        super(HangarCarouselDataProvider, self).clear()
        self._supplyItems = []
        self._frontSupplyItems = []

    def updateDynamicFilters(self):
        prevHiddenDynamicFilters = self.getHiddenDynamicFilters()
        self._updateDynamicFilters()
        newHiddenDynamicFilters = self.getHiddenDynamicFilters()
        self.filter.reset(keys=newHiddenDynamicFilters, save=prevHiddenDynamicFilters != newHiddenDynamicFilters)

    def updateSupplies(self):
        self._supplyItems = []
        self._buildSupplyItems()
        self.flashObject.invalidateItems(self._getSupplyIndices(), self._supplyItems)
        self.applyFilter()

    @staticmethod
    def _isSuitableForQueue(vehicle):
        return vehicle.getCustomState() != Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE

    def _populate(self):
        self._telecomRentals = BigWorld.player().telecomRentals
        self._telecomRentals.onPendingRentChanged += self._onTelecomPendingRentChanged
        g_clientUpdateManager.addCallback('tokens', self._onTelecomRentalsChanged)
        super(HangarCarouselDataProvider, self)._populate()

    def _dispose(self):
        self._telecomRentals.onPendingRentChanged -= self._onTelecomPendingRentChanged
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(HangarCarouselDataProvider, self)._dispose()

    def _isTelecomRentalsEnabled(self):
        hasTelecomRentalsActive = self._telecomRentals.isActive()
        isRentalEnabled = self._serverSettings.isTelecomRentalsEnabled()
        return hasTelecomRentalsActive and isRentalEnabled

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

    def _getFrontIndices(self):
        previousItemsCount = len(self._vehicles) + len(_SUPPLY_ITEMS.ALL)
        return [ previousItemsCount + idx for idx in _FRONT_SUPPLY_ITEMS.ALL ]

    def _getFrontAdditionalItemsIndexes(self):
        frontIndices = self._getFrontIndices()
        pruneIndices = set()
        if not self._isTelecomRentalsEnabled() or self._telecomRentals.getAvailableRentCount() == 0:
            pruneIndices.add(_FRONT_SUPPLY_ITEMS.RENT_TANK)
        return [ suppIdx for suppIdx in frontIndices if frontIndices.index(suppIdx) not in pruneIndices ]

    def _getSupplyIndices(self):
        return [ len(self._vehicles) + idx for idx in _SUPPLY_ITEMS.ALL ]

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY
        self._baseCriteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
        self._baseCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        self._baseCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE

    def _onTelecomRentalsChanged(self, diff):
        if PARTNERSHIP_TOKEN_NAME in diff or ROSTER_EXPIRATION_TOKEN_NAME in diff:
            self.buildList()

    def _onTelecomPendingRentChanged(self, vehCD):
        if vehCD is not None:
            self.buildList()
        return

    def _buildTelecomRentalVehicleItems(self):
        self._telecomRentalsVehicles = []
        rentPromotionCriteria = REQ_CRITERIA.VEHICLE.TELECOM_RENT | self._baseCriteria
        oldVehLen = len(self._vehicles)
        self._addVehicleItemsByCriteria(rentPromotionCriteria)
        totalRentVehicles = len(self._vehicles) - oldVehLen
        if totalRentVehicles > 0:
            self._telecomRentalsVehicles = [ veh.intCD for veh in self._vehicles[-totalRentVehicles:] ]

    def _buildRentPromitionVehicleItems(self):
        rentPromotionCriteria = REQ_CRITERIA.VEHICLE.RENT_PROMOTION | ~self._baseCriteria
        self._addVehicleItemsByCriteria(rentPromotionCriteria)

    def _buildFrontSupplyItems(self):
        self._frontSupplyItems = []
        if self._isTelecomRentalsEnabled() and not self._telecomRentals.getAvailableRentCount() == 0:
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

    def _buildVehicle(self, vehicle):
        vo = super(HangarCarouselDataProvider, self)._buildVehicle(vehicle)
        vo['isEarnCrystals'] = vo['isEarnCrystals'] and self._dynamicFiltersState[FILTER_KEYS.CRYSTALS]
        vo['xpImgSource'] = vo['xpImgSource'] if self._dynamicFiltersState[FILTER_KEYS.BONUS] else ''
        vo['tooltip'] = TOOLTIPS_CONSTANTS.HANGAR_CAROUSEL_VEHICLE
        return vo

    def _buildVehicleItems(self):
        super(HangarCarouselDataProvider, self)._buildVehicleItems()
        self._buildTelecomRentalVehicleItems()
        self._buildRentPromitionVehicleItems()
        self._buildSupplyItems()
        self._buildFrontSupplyItems()

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
            discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'slotsPrices', True, slotPrice, defaultSlotPrice)
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
        slotPriceCurrency = slotPrice.getCurrency()
        buySlotVO = {'buySlot': True,
         'slotPrice': slotPrice.get(slotPriceCurrency, 0),
         'slotPriceCurrency': slotPriceCurrency,
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_SLOT,
         'infoText': buySlotString,
         'smallInfoText': smallBuySlotString,
         'hasSale': discount is not None,
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_BUY_SLOT}
        if discount is not None:
            buySlotVO.update({'slotPriceActionData': discount})
        self._supplyItems.append(buySlotVO)
        return

    def _updateDynamicFilters(self):
        state, hangarGuiCtrl = self._dynamicFiltersState, self.__hangarGuiCtrl
        state[FILTER_KEYS.CRYSTALS] = hangarGuiCtrl.checkCurrentCrystalRewards(default=True)
        state[FILTER_KEYS.BONUS] = hangarGuiCtrl.checkCurrentBonusCaps(_CAPS.DAILY_MULTIPLIED_XP, default=True)
