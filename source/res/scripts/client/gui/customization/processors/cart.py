# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/processors/cart.py
from collections import namedtuple
import logging
import typing
from CurrentVehicle import g_currentVehicle
from gui.customization.shared import AdditionalPurchaseGroups, PurchaseItem, PURCHASE_ITEMS_ORDER
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import SeasonType
from shared_utils import CONST_CONTAINER
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

class ItemsType(CONST_CONTAINER):
    DEFAULT = 1
    STYLE = 2
    EDITABLE_STYLE = 3


ProcessResult = namedtuple('ProcessResult', ('items', 'descriptors', 'itemsType'))

class ProcessorSelector(object):
    __slots__ = ('__processors',)

    def __init__(self, processors):
        super(ProcessorSelector, self).__init__()
        self.__processors = {}
        self.__processors.update(processors)

    def process(self, items):
        itemsType = self.__getItemsType(items)
        if itemsType not in self.__processors:
            _logger.error("Can't find processor by type %d", itemsType)
            return None
        else:
            processor = self.__processors[itemsType]
            descriptors = processor.process(items)
            return ProcessResult(items, descriptors, itemsType)

    def __getItemsType(self, items):
        if not items:
            _logger.error('Empty purchaseItems list')
            return
        if items[0].group == AdditionalPurchaseGroups.STYLES_GROUP_ID:
            if len(items) == 1:
                return ItemsType.STYLE
            return ItemsType.EDITABLE_STYLE
        return ItemsType.DEFAULT


class BasePurchaseDescription(object):
    __slots__ = ('intCD', 'identificator', 'selected', 'item', 'component', 'quantity', 'purchaseIndices', '_uiDataPacker')

    def __init__(self, item, purchaseIdx=0, quantity=1, component=None):
        self._uiDataPacker = None
        self.intCD = item.intCD
        self.identificator = self.intCD
        self.selected = False
        self.item = item
        self.component = component
        self.quantity = quantity
        self.purchaseIndices = [purchaseIdx]
        return

    def getUIData(self):
        return self._uiDataPacker(self) if self._uiDataPacker is not None else None

    def addPurchaseIndices(self, indices):
        self.quantity += 1
        self.purchaseIndices.extend(indices)

    def setPacker(self, packer):
        self._uiDataPacker = packer


class StubItemPurchaseDescription(BasePurchaseDescription):
    __slots__ = ('isFromInventory', 'isEdited')
    _StubItem = namedtuple('_StubItem', ('intCD',))

    def __init__(self):
        super(StubItemPurchaseDescription, self).__init__(self._StubItem(-1), quantity=0)
        self.isFromInventory = False
        self.isEdited = False


class SeparateItemPurchaseDescription(BasePurchaseDescription):
    __slots__ = ('intCD', 'identificator', 'selected', 'itemData', 'compoundPrice', 'quantity', 'isFromInventory', 'purchaseIndices', 'group', 'locked', 'isEdited')

    def __init__(self, purchaseItem, purchaseIdx):
        super(SeparateItemPurchaseDescription, self).__init__(purchaseItem.item, purchaseIdx, component=purchaseItem.component)
        self.selected = purchaseItem.selected
        self.compoundPrice = purchaseItem.price
        self.isFromInventory = purchaseItem.isFromInventory
        self.group = purchaseItem.group
        self.locked = purchaseItem.locked
        self.isEdited = purchaseItem.isEdited
        self.identificator = self.__generateID()

    def __generateID(self):
        if self.item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and self.component is not None:
            number = int(self.component.number) if self.component.number else -1
            return hash((self.intCD,
             self.group,
             self.isFromInventory,
             number,
             self.selected))
        else:
            return hash((self.intCD,
             self.group,
             self.isFromInventory,
             self.component.progressionLevel,
             self.selected)) if self.item.isProgressive and self.component is not None else hash((self.intCD,
             self.group,
             self.isFromInventory,
             -1,
             self.selected))


class ItemsProcessor(object):
    __slots__ = ('_stubItemDescriptionClass', '_itemDescriptionClass', '_itemUiDataPacker', '_stubUiDataPacker')

    def __init__(self, itemPacker, stubPacker):
        self._itemUiDataPacker = itemPacker
        self._stubUiDataPacker = stubPacker
        self._itemDescriptionClass = BasePurchaseDescription
        self._stubItemDescriptionClass = StubItemPurchaseDescription

    def process(self, items):
        items = self._preProcess(items)
        itemsInfo = self._process(items)
        return self._postProcess(itemsInfo)

    def _preProcess(self, items):
        return items

    def _process(self, items):
        raise NotImplementedError

    def _postProcess(self, itemsInfo):
        itemsDescriptors = {season:[] for season in SeasonType.COMMON_SEASONS}
        for season in SeasonType.COMMON_SEASONS:
            if season in itemsInfo:
                items = itemsInfo[season].flatten()
            else:
                items = [self._getStubItemDescription()]
            itemsDescriptors[season] = items

        return itemsDescriptors

    def _getStubItemDescription(self):
        desc = self._stubItemDescriptionClass()
        desc.setPacker(self._stubUiDataPacker)
        return desc

    def _getItemDescription(self, item, idx=0):
        desc = self._itemDescriptionClass(item, idx)
        desc.setPacker(self._itemUiDataPacker)
        return desc


class SeparateItemsProcessor(ItemsProcessor):
    __slots__ = ()

    def __init__(self, itemPacker, stubPacker):
        super(SeparateItemsProcessor, self).__init__(itemPacker, stubPacker)
        self._itemDescriptionClass = SeparateItemPurchaseDescription

    def _process(self, items):
        itemsInfo = {}
        for idx, item in enumerate(items):
            itemDescription = self._getItemDescription(item, idx)
            seasonInfo = itemsInfo.setdefault(item.group, _SeasonPurchaseInfo(self._getKey))
            seasonInfo.add(itemDescription, item.item.itemTypeID)

        return itemsInfo

    @staticmethod
    def _getKey(purchaseItem):
        if purchaseItem.item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and purchaseItem.component is not None:
            number = int(purchaseItem.component.number) if purchaseItem.component.number else -1
            return (purchaseItem.locked,
             not purchaseItem.isFromInventory,
             purchaseItem.intCD,
             number,
             purchaseItem.selected)
        else:
            return (purchaseItem.isEdited,
             not purchaseItem.isFromInventory,
             purchaseItem.intCD,
             purchaseItem.component.progressionLevel,
             purchaseItem.selected) if purchaseItem.item.isProgressive and purchaseItem.component is not None else (not purchaseItem.isEdited,
             purchaseItem.isFromInventory,
             purchaseItem.intCD,
             -1,
             purchaseItem.selected)


class StyleItemsProcessor(ItemsProcessor):
    __slots__ = ()
    __service = dependency.descriptor(ICustomizationService)

    def _preProcess(self, items):
        return items[0]

    def _process(self, style):
        itemsInfo = {}
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        nationalEmblemItem = self.__service.getItemByID(GUI_ITEM_TYPE.EMBLEM, g_currentVehicle.item.descriptor.type.defaultPlayerEmblemID)
        showStyleInsteadItems = True
        for season in SeasonType.COMMON_SEASONS:
            outfit = style.item.getOutfit(season, vehicleCD=vehicleCD)
            seasonInfo = itemsInfo.setdefault(season, _SeasonPurchaseInfo())
            for intCD in outfit.items():
                item = self.__service.getItemByCD(intCD)
                if not item.isHiddenInUI():
                    if item.intCD != nationalEmblemItem.intCD:
                        showStyleInsteadItems = False
                    itemDescription = self._getItemDescription(item)
                    seasonInfo.add(itemDescription, item.itemTypeID)

            if showStyleInsteadItems:
                styleDescription = self._getItemDescription(style.item)
                seasonInfo.add(styleDescription, GUI_ITEM_TYPE.STYLE)
                seasonInfo.delete(nationalEmblemItem.intCD, GUI_ITEM_TYPE.EMBLEM)

        return itemsInfo


class EditableStyleItemsProcessor(SeparateItemsProcessor):
    __slots__ = ()
    __service = dependency.descriptor(ICustomizationService)

    def _process(self, items):
        itemsInfo = {}
        nationalEmblemItem = self.__service.getItemByID(GUI_ITEM_TYPE.EMBLEM, g_currentVehicle.item.descriptor.type.defaultPlayerEmblemID)
        showStyleInsteadItems = True
        styleDescription = None
        for idx, pItem in enumerate(items):
            if pItem.item.isHiddenInUI():
                continue
            if pItem.group == AdditionalPurchaseGroups.STYLES_GROUP_ID:
                styleDescription = self._getItemDescription(pItem)
                continue
            if not pItem.isEdited and pItem.item.intCD != nationalEmblemItem.intCD:
                showStyleInsteadItems = False
            seasonInfo = itemsInfo.setdefault(pItem.group, _SeasonPurchaseInfo(self._getKey))
            itemDescription = self._getItemDescription(pItem, idx)
            orderKey = pItem.getOrderKey()
            seasonInfo.add(itemDescription, orderKey)

        if showStyleInsteadItems and styleDescription is not None:
            for season in SeasonType.COMMON_SEASONS:
                seasonInfo = itemsInfo.setdefault(season, _SeasonPurchaseInfo())
                seasonInfo.add(styleDescription, GUI_ITEM_TYPE.STYLE)
                seasonInfo.delete(nationalEmblemItem.intCD, GUI_ITEM_TYPE.EMBLEM)

        return itemsInfo

    def _getItemDescription(self, item, idx=0, descriptionClass=None, descriptionPacker=None):
        desc = descriptionClass(item, idx) if descriptionClass is not None else self._itemDescriptionClass(item, idx)
        packer = descriptionPacker if descriptionPacker is not None else self._itemUiDataPacker
        desc.setPacker(packer)
        return desc


class _SeasonPurchaseInfo(object):
    __slots__ = ('__buckets', '__keyFunc')

    def __init__(self, keyFunc=None):
        self.__buckets = {key:{} for key in PURCHASE_ITEMS_ORDER}
        self.__keyFunc = keyFunc or self.__defaultKeyFunc

    def add(self, purchaseItemInfo, orderKey):
        if orderKey in PURCHASE_ITEMS_ORDER:
            bucket = self.__buckets[orderKey]
            key = self.__keyFunc(purchaseItemInfo)
            if key in bucket:
                bucket[key].addPurchaseIndices(purchaseItemInfo.purchaseIndices)
            else:
                bucket[key] = purchaseItemInfo

    def delete(self, intCD, orderKey):
        bucket = self.__buckets[orderKey]
        delKey = None
        for key, itemPurchaseDesc in bucket.iteritems():
            if itemPurchaseDesc.intCD == intCD:
                delKey = key
                break

        if delKey:
            del bucket[delKey]
        return

    def flatten(self):
        items = []
        for key in PURCHASE_ITEMS_ORDER:
            bucket = self.__buckets[key].values()
            bucket.sort(key=self.__keyFunc)
            items.extend(bucket)

        return items

    @staticmethod
    def __defaultKeyFunc(item):
        return item.intCD
