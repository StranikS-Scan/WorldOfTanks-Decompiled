# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/carousel_data_provider.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import getStatusStrings
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.new_year.views.new_year_vehicles_view import VehicleCooldownNotifier
from gui.shared.formatters import text_styles
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearController

class _SUPPLY_ITEMS(object):
    BUY_TANK = 0
    RESTORE_TANK = 1
    BUY_SLOT = 2
    ALL = (BUY_TANK, RESTORE_TANK, BUY_SLOT)


class _BEFORE_SUPPLY_ITEMS(object):
    NY_SLOT = 0
    ALL = (NY_SLOT,)


class HangarCarouselDataProvider(CarouselDataProvider):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(HangarCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.INVENTORY
        self._vehicleBranch = []
        self._supplyItems = []
        self._emptySlotsCount = 0
        self._restorableVehiclesCount = 0
        self.vehicleCooldownNotifier = None
        return

    @property
    def collection(self):
        return self._vehicleItems + self._supplyItems + self._vehicleBranch

    def getCurrentVehiclesCount(self):
        return len(self._filteredIndices) - len(self._getAdditionalItemsIndexes()) - len(self._getBeforeAdditionalItemsIndexes())

    def updateSupplies(self):
        self._supplyItems = []
        self._buildSupplyItems()
        self.flashObject.invalidateItems(self.__getSupplyIndices(), self._supplyItems)
        self.applyFilter()

    def updateVehicleBranch(self):
        self._vehicleBranch = []
        self._buildVehicleBranch()
        self.flashObject.invalidateItems(self.__getVehicleBranchIndices(), self._vehicleBranch)
        self.applyFilter()

    def clear(self):
        super(HangarCarouselDataProvider, self).clear()
        self._supplyItems = []
        self._verifySlotNotifier()

    def _buildRentPromitionVehicleItems(self):
        rentPromotionCriteria = REQ_CRITERIA.VEHICLE.RENT_PROMOTION | ~self._baseCriteria
        self._addVehicleItemsByCriteria(rentPromotionCriteria)

    def _buildVehicleItems(self):
        super(HangarCarouselDataProvider, self)._buildVehicleItems()
        self._buildRentPromitionVehicleItems()
        self._buildSupplyItems()
        self._buildVehicleBranch()

    def _getAdditionalItemsIndexes(self):
        supplyIndices = self.__getSupplyIndices()
        serverSettings = dependency.instance(ILobbyContext).getServerSettings()
        restoreEnabled = serverSettings.isVehicleRestoreEnabled()
        storageEnabled = serverSettings.isIngameStorageEnabled()
        pruneIndices = set()
        if not self._emptySlotsCount:
            pruneIndices.add(_SUPPLY_ITEMS.BUY_TANK)
        if self._restorableVehiclesCount == 0 or not restoreEnabled or not storageEnabled and isIngameShopEnabled():
            pruneIndices.add(_SUPPLY_ITEMS.RESTORE_TANK)
        return [ suppIdx for suppIdx in supplyIndices if supplyIndices.index(suppIdx) not in pruneIndices ]

    def _getBeforeAdditionalItemsIndexes(self):
        return [] if not self._nyController.isVehicleBranchEnabled() else self.__getVehicleBranchIndices()

    def _buildSupplyItems(self):
        self._supplyItems = []
        items = self._itemsCache.items
        slots = items.stats.vehicleSlots
        vehicles = self.getTotalVehiclesCount()
        rentPromotion = self.getRentPromotionVehiclesCount()
        slotPrice = items.shop.getVehicleSlotsPrice(slots)
        defaultSlotPrice = items.shop.defaults.getVehicleSlotsPrice(slots)
        self._emptySlotsCount = slots - (vehicles - rentPromotion)
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
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_BUY_VEHICLE_NEW if isIngameShopEnabled() else TOOLTIPS.TANKS_CAROUSEL_BUY_VEHICLE})
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

    def _buildVehicleBranch(self):
        self._verifySlotNotifier()
        self._startSlotNotifier()
        self._vehicleBranch = []
        freeSlotsCount = len(self._nyController.getVehicleBranch().getFreeVehicleSlots())
        tankTreeAvailable = self._nyController.getVehicleBranch().hasAvailableSlots()
        smallNyTankString, nyTankString = getStatusStrings('nyTank', style=text_styles.middleTitleNY)
        if freeSlotsCount == 0 and tankTreeAvailable:
            smallNyStatusSlotsString, nyStatusSlotsString = getStatusStrings('nyTankSlotsFull', style=text_styles.mainNY)
        else:
            smallNyStatusSlotsString, nyStatusSlotsString = getStatusStrings('nyTankEmptyCount', style=text_styles.mainNY, ctx={'count': freeSlotsCount})
        self._vehicleBranch.append({'nySlot': True,
         'smallInfoText': text_styles.concatStylesToMultiLine(smallNyTankString, smallNyStatusSlotsString),
         'infoText': text_styles.concatStylesToMultiLine(nyTankString, nyStatusSlotsString),
         'icon': RES_ICONS.MAPS_ICONS_NEW_YEAR_VEHICLES_VIEW_NY_SLOT,
         'iconSmall': RES_ICONS.MAPS_ICONS_NEW_YEAR_VEHICLES_VIEW_NY_SLOT_SMALL,
         'tooltip': makeTooltip(header=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.header()), body=backport.text(R.strings.tooltips.tankCarusel.newYearSlot.body())),
         'nyBlinkEnabled': freeSlotsCount > 0 or not tankTreeAvailable})

    def _startSlotNotifier(self):
        if self._nyController.isVehicleBranchEnabled():
            self.vehicleCooldownNotifier = VehicleCooldownNotifier(self.updateVehicleBranch, self._nyController.getVehicleBranch().getVehicleSlots())
            self.vehicleCooldownNotifier.startNotification()

    def _verifySlotNotifier(self):
        if self.vehicleCooldownNotifier is not None:
            self.vehicleCooldownNotifier.stopNotification()
            self.vehicleCooldownNotifier.clear()
            self.vehicleCooldownNotifier = None
        return

    def __getSupplyIndices(self):
        return [ len(self._vehicles) + idx for idx in _SUPPLY_ITEMS.ALL ]

    def __getVehicleBranchIndices(self):
        return [ len(self._vehicles) + len(_SUPPLY_ITEMS.ALL) + idx for idx in _BEFORE_SUPPLY_ITEMS.ALL ]


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
        self._selectedIdx = idx
        self._currentVehicle.selectVehicle(self._vehicles[idx].invID)
