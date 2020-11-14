# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/array_providers/base.py
from functools import partial
from frameworks.wulf import Array
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BaseVehSectionContext(object):
    __slots__ = ('__slotID',)

    def __init__(self, slotID):
        self.__slotID = slotID

    @property
    def slotID(self):
        return self.__slotID


class BaseArrayProvider(object):
    __slots__ = ('__items',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__items = None
        self.updateItems()
        return

    def getItemsList(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getCriteria()).values()
        return items

    def updateItems(self):
        self.__items = self.getItemsList()

    def createArray(self, itemFilter=None):
        array = Array()
        self.fillArray(array, itemFilter)
        return array

    def getItemViewModel(self):
        raise NotImplementedError

    def _sortItems(self, items, ctx):
        items.sort(key=partial(self._getItemSortKey, ctx=ctx))

    def fillArray(self, array, ctx, itemFilter=None):
        self._sortItems(self.__items, ctx)
        items = self.__items
        if itemFilter is not None:
            items = itemFilter(items)
        array.clear()
        for item in items:
            itemModel = self.createSlot(item, ctx)
            self.updateSlot(itemModel, item, ctx)
            array.addViewModel(itemModel)

        array.invalidate()
        return

    def updateArray(self, array, ctx):
        for arrayModel in array:
            item = self._itemsCache.items.getItemByCD(arrayModel.getIntCD())
            self.updateSlot(arrayModel, item, ctx)

    def createSlot(self, item, ctx):
        return self.getItemViewModel()

    def updateSlot(self, model, item, ctx):
        raise NotImplementedError

    def _getCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getItemTypeID(self):
        raise NotImplementedError

    def _getItemSortKey(self, item, ctx):
        return None


class VehicleBaseArrayProvider(BaseArrayProvider):
    __slots__ = ('_interactor',)

    def __init__(self, interactor):
        self._interactor = interactor
        super(VehicleBaseArrayProvider, self).__init__()

    def createSlot(self, item, ctx):
        model = super(VehicleBaseArrayProvider, self).createSlot(item, ctx)
        model.setName(item.userName)
        model.setIntCD(item.intCD)
        model.setItemTypeID(item.itemTypeID)
        return model

    def updateSlot(self, model, item, ctx):
        model.setIsDisabled(False)
        model.setIsLocked(False)
        model.setItemsInStorage(item.inventoryCount)
        model.setIsMounted(item in self._getInstalledLayout())
        if item in self._getCurrentLayout():
            model.setInstalledSlotId(self._getCurrentLayout().index(item))
        else:
            model.setInstalledSlotId(NONE_ID)

    def _fillStatus(self, model, item, slotID, isInstalledOrMounted):
        isFit, reason = self._mayInstall(item, slotID)
        if not isFit and reason != 'already installed':
            model.setIsDisabled(True)
            model.setIsLocked(True)

    def _fillBuyPrice(self, model, item):
        if not item.isHidden:
            BuyPriceModelBuilder.clearPriceModel(model.price)
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.price, item.getBuyPrice())

    def _fillBuyStatus(self, model, item, isInstalledOrMounted):
        if not item.isInInventory:
            money, exchangeRate = self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate
            isEnough = item.mayPurchaseWithExchange(money, exchangeRate)
            if not (isInstalledOrMounted or isEnough):
                model.setIsDisabled(True)

    def _mayInstall(self, item, slotID=None):
        return item.mayInstall(self._getVehicle(), slotID)

    def _getCriteria(self):
        return REQ_CRITERIA.VEHICLE.SUITABLE([self._getVehicle()], self._getItemTypeID()) | self._getItemCriteria()

    def _getItemCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getVehicle(self):
        return self._interactor.getItem()

    def _getCurrentLayout(self):
        return self._interactor.getCurrentLayout()

    def _getInstalledLayout(self):
        return self._interactor.getInstalledLayout()
