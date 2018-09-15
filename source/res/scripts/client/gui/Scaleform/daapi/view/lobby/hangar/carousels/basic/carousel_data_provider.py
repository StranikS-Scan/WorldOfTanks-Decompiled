# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/basic/carousel_data_provider.py
from gui.Scaleform.daapi.view.lobby.vehicle_carousel.carousel_data_provider import CarouselDataProvider, getStatusStrings
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.requesters import REQ_CRITERIA

class _SUPPLY_ITEMS(object):
    BUY_TANK = 0
    BUY_SLOT = 1
    ALL = (BUY_TANK, BUY_SLOT)


class HangarCarouselDataProvider(CarouselDataProvider):
    """ Vehicle data provider specific to hangar's carousel (has special supply slots)
    """

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(HangarCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.ONLY_FOR_FALLOUT
        self._supplyItems = []
        self._emptySlotsCount = 0

    @property
    def collection(self):
        return self._vehicleItems + self._supplyItems

    def getCurrentVehiclesCount(self):
        return len(self._filteredIndices) - len(self._getAdditionalItemsIndexes())

    def updateSupplies(self):
        """ Update the supply slots: 'buy tank' and 'buy slot'.
        """
        self._supplyItems = []
        self._buildSupplyItems()
        self.flashObject.invalidateItems(self.__getSupplyIndices(), self._supplyItems)
        self.applyFilter()

    def clear(self):
        super(HangarCarouselDataProvider, self).clear()
        self._supplyItems = []

    def _buildVehicleItems(self):
        super(HangarCarouselDataProvider, self)._buildVehicleItems()
        self._buildSupplyItems()

    def _getAdditionalItemsIndexes(self):
        supplyIndices = self.__getSupplyIndices()
        if not self._emptySlotsCount:
            supplyIndices.pop(_SUPPLY_ITEMS.BUY_TANK)
        return supplyIndices

    def _buildSupplyItems(self):
        self._supplyItems = []
        items = self._itemsCache.items
        slots = items.stats.vehicleSlots
        vehicles = self.getTotalVehiclesCount()
        slotPrice = items.shop.getVehicleSlotsPrice(slots)
        defaultSlotPrice = items.shop.defaults.getVehicleSlotsPrice(slots)
        if slotPrice != defaultSlotPrice:
            discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'slotsPrices', True, Money(gold=slotPrice), Money(gold=defaultSlotPrice))
        else:
            discount = None
        self._emptySlotsCount = slots - vehicles
        smallBuySlotString, buySlotString = getStatusStrings('buySlot')
        smallBuyTankString, buyTankString = getStatusStrings('buyTank')
        smallEmptySlotsString, emptySlotsString = getStatusStrings('buyTankEmptyCount', style=text_styles.main, ctx={'count': self._emptySlotsCount})
        self._supplyItems.append({'buyTank': True,
         'smallInfoText': text_styles.concatStylesToMultiLine(smallBuyTankString, smallEmptySlotsString),
         'infoText': text_styles.concatStylesToMultiLine(buyTankString, emptySlotsString),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK,
         'tooltip': TOOLTIPS.TANKS_CAROUSEL_BUY_VEHICLE})
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

    def __getSupplyIndices(self):
        """ Get the indices of supply items relatively to the vehicles list.
        Supply items go after the vehicles, but they're in separate list.
        
        :return: list of supply items indices
        """
        return [ len(self._vehicles) + idx for idx in _SUPPLY_ITEMS.ALL ]


class BCCarouselDataProvider(CarouselDataProvider):

    @property
    def collection(self):
        return self._vehicleItems

    def updateSupplies(self):
        """ Update the supply slots: 'buy tank' and 'buy slot'.
        """
        pass

    def _buildVehicleItems(self):
        super(BCCarouselDataProvider, self)._buildVehicleItems()
        for vehicleItem in self._vehicleItems:
            vehicleItem['infoText'] = ''
            vehicleItem['smallInfoText'] = ''
            vehicleItem['tankType'] = vehicleItem['tankType'].replace('_elite', '')

    def setShowStats(self, showVehicleStats):
        pass

    def selectVehicle(self, idx):
        self._selectedIdx = idx
        self._currentVehicle.selectVehicle(self._vehicles[idx].invID)
