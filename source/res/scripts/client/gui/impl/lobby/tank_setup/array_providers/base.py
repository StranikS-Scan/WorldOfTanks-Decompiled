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

    def hasUnfitItems(self):
        return False

    def getItemsList(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getCriteria()).values()
        return items

    def updateItems(self):
        self.__items = self.getItemsList()

    def getItems(self):
        return self.__items

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
    __slots__ = ('_interactor', '__hasUnfitItems')

    def __init__(self, interactor):
        self._interactor = interactor
        self.__hasUnfitItems = False
        super(VehicleBaseArrayProvider, self).__init__()

    def hasUnfitItems(self):
        return self.__hasUnfitItems

    def createSlot(self, item, ctx):
        model = super(VehicleBaseArrayProvider, self).createSlot(item, ctx)
        model.setName(item.userName)
        model.setIntCD(item.intCD)
        model.setItemTypeID(item.itemTypeID)
        return model

    def getItemsList(self):
        items = self._itemsCache.items.getItems(self._getItemTypeID(), self._getItemCriteria()).values()
        criteria = self._getCriteria()
        suitableItems = filter(criteria, items)
        self.__hasUnfitItems = len(items) != len(suitableItems)
        return suitableItems

    def updateSlot(self, model, item, ctx):
        model.setIsDisabled(False)
        model.setIsLocked(False)
        model.setLockReason('')
        model.setItemsInStorage(item.inventoryCount)
        model.setIsMounted(item in self._getInstalledLayout())
        model.setIsMountedInOtherSetup(self._getSetupLayout().isInOtherLayout(item))
        if self._getVehicle().isPostProgressionExists:
            installedCount = self._getSetupLayout().getIntCDs().count(item.intCD)
        else:
            installedCount = self._getInstalledLayout().getIntCDs().count(item.intCD)
        model.setIsMountedMoreThanOne(installedCount > 1)
        setupLayoutIdx = NONE_ID
        setupSlotIdx = NONE_ID
        if item in self._getCurrentLayout():
            itemIdx = self._getCurrentLayout().index(item)
            model.setInstalledSlotId(itemIdx)
            setupSlotIdx = itemIdx
            setupLayoutIdx = self._getSetupLayout().layoutIndex
        else:
            model.setInstalledSlotId(NONE_ID)
            for layoutIndex, setup in self._getSetupLayout().setups.iteritems():
                if item in setup:
                    setupLayoutIdx = layoutIndex
                    setupSlotIdx = setup.index(item)
                    break

        model.setItemInstalledSetupIdx(setupLayoutIdx)
        model.setItemInstalledSetupSlotIdx(setupSlotIdx)

    def _fillStatus(self, model, item, slotID):
        isFit, reason = self._mayInstall(item, slotID)
        if not isFit and reason != 'already installed':
            model.setIsDisabled(True)
            model.setIsLocked(True)
            model.setLockReason(reason.replace(' ', '_'))

    def _fillBuyPrice(self, model, item):
        if not item.isHidden:
            BuyPriceModelBuilder.clearPriceModel(model.price)
            BuyPriceModelBuilder.fillPriceModelByItemPrice(model.price, item.getBuyPrice())

    def _fillBuyStatus(self, model, item, isInstalledOrMounted):
        if not item.isInInventory:
            money, exchangeRate = self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate
            isEnough = item.mayPurchaseWithExchange(money, exchangeRate)
            if not (isInstalledOrMounted or isEnough or self._isInstallAllowed(item)):
                model.setIsDisabled(True)

    def _mayInstall(self, item, slotID=None):
        return item.mayInstall(self._getVehicle(), slotID)

    def _isInstallAllowed(self, item):
        return False

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

    def _getSetupLayout(self):
        return self._interactor.getSetupLayout()
