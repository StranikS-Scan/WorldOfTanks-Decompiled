# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/processors/cart.py
from collections import namedtuple
import logging
import typing
from gui.customization.shared import AdditionalPurchaseGroups, PurchaseItem
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import SeasonType
from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)

class ItemsType(CONST_CONTAINER):
    DEFAULT = 1
    STYLE = 2


ProcessResult = namedtuple('ProcessResult', ('items', 'descriptors', 'itemsType'))

class ProcessorSelector(object):
    __slots__ = ('__processors',)

    def __init__(self, processors):
        super(ProcessorSelector, self).__init__()
        self.__processors = {}
        self.__processors.update(processors)

    def process(self, items):
        itemsToProcess = self.__preprocess(items)
        itemsType = self.__getItemsType(itemsToProcess)
        if itemsType not in self.__processors:
            _logger.error("Can't find processor by type %d", itemsType)
            return None
        else:
            processor = self.__processors[itemsType]
            descriptors = processor.process(itemsToProcess)
            return ProcessResult(itemsToProcess, descriptors, itemsType)

    def __getItemsType(self, items):
        return ItemsType.STYLE if len(items) == 1 and items[0].group == AdditionalPurchaseGroups.STYLES_GROUP_ID else ItemsType.DEFAULT

    def __preprocess(self, items):
        return [ item for item in items if not item.isDismantling ]


class BasePurchaseDescription(object):
    __slots__ = ('intCD', 'identificator', 'item', 'component', 'quantity', 'purchaseIndices', '__uiDataPacker')

    def __init__(self, item, purchaseIdx=0, quantity=1, component=None):
        self.__uiDataPacker = None
        self.intCD = item.intCD
        self.identificator = self.intCD
        self.item = item
        self.component = component
        self.quantity = quantity
        self.purchaseIndices = [purchaseIdx]
        return

    def getUIData(self):
        return self.__uiDataPacker(self) if self.__uiDataPacker is not None else None

    def addPurchaseIndices(self, indices):
        self.quantity += 1
        self.purchaseIndices.extend(indices)

    def setPacker(self, packer):
        self.__uiDataPacker = packer


class StubItemPurchaseDescription(BasePurchaseDescription):
    __slots__ = ('isFromInventory',)
    _StubItem = namedtuple('_StubItem', ('intCD',))

    def __init__(self):
        super(StubItemPurchaseDescription, self).__init__(self._StubItem(-1), quantity=0)
        self.isFromInventory = False


class SeparateItemPurchaseDescription(BasePurchaseDescription):
    __slots__ = ('intCD', 'identificator', 'selected', 'itemData', 'compoundPrice', 'quantity', 'isFromInventory', 'purchaseIndices')

    def __init__(self, purchaseItem, purchaseIdx):
        super(SeparateItemPurchaseDescription, self).__init__(purchaseItem.item, purchaseIdx, component=purchaseItem.component)
        self.identificator = self.__generateID(purchaseItem)
        self.selected = purchaseItem.selected
        self.compoundPrice = purchaseItem.price
        self.isFromInventory = purchaseItem.isFromInventory

    def __generateID(self, item):
        return hash((self.intCD, item.group, item.isFromInventory))


class ItemsProcessor(object):
    __slots__ = ('__stubItemDescriptionClass', '__itemDescriptionClass', '__itemUiDataPacker', '__stubUiDataPacker')

    def __init__(self, itemPacker, stubPacker, itemDescClass=BasePurchaseDescription, stubDescClass=StubItemPurchaseDescription):
        self.__itemUiDataPacker = itemPacker
        self.__stubUiDataPacker = stubPacker
        self.__itemDescriptionClass = itemDescClass
        self.__stubItemDescriptionClass = stubDescClass
        if self.__itemDescriptionClass is None:
            _logger.error('Item description class must be set')
        if self.__stubItemDescriptionClass is None:
            _logger.error('Stub description class must be set')
        return

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
        desc = self.__stubItemDescriptionClass()
        desc.setPacker(self.__stubUiDataPacker)
        return desc

    def _getItemDescription(self, item, idx=0):
        desc = self.__itemDescriptionClass(item, idx)
        desc.setPacker(self.__itemUiDataPacker)
        return desc


class SeparateItemsProcessor(ItemsProcessor):
    __slots__ = ()

    def __init__(self, itemPacker, stubPacker, itemDescClass=SeparateItemPurchaseDescription, stubDescClass=StubItemPurchaseDescription):
        super(SeparateItemsProcessor, self).__init__(itemPacker, stubPacker, itemDescClass, stubDescClass)

    def _process(self, items):
        itemsInfo = {}
        for idx, item in enumerate(items):
            itemDescription = self._getItemDescription(item, idx)
            seasonInfo = itemsInfo.setdefault(item.group, _SeasonPurchaseInfo(self._getKey))
            seasonInfo.add(itemDescription, item.item.itemTypeID)

        return itemsInfo

    @staticmethod
    def _getKey(item):
        return (not item.isFromInventory, item.intCD)


class StyleItemsProcessor(ItemsProcessor):
    __slots__ = ()

    def __init__(self, itemPacker, stubPacker, itemDescClass=BasePurchaseDescription, stubDescClass=StubItemPurchaseDescription):
        super(StyleItemsProcessor, self).__init__(itemPacker, stubPacker, itemDescClass, stubDescClass)

    def _preProcess(self, items):
        return items[0]

    def _process(self, style):
        itemsInfo = {}
        for season in SeasonType.COMMON_SEASONS:
            showStyleInsteadItems = True
            outfit = style.item.getOutfit(season)
            seasonInfo = itemsInfo.setdefault(season, _SeasonPurchaseInfo())
            for item in outfit.items():
                if not item.isHiddenInUI():
                    showStyleInsteadItems = False
                    itemDescription = self._getItemDescription(item)
                    seasonInfo.add(itemDescription, item.itemTypeID)

            if showStyleInsteadItems:
                styleDescription = self._getItemDescription(style.item)
                seasonInfo.add(styleDescription, GUI_ITEM_TYPE.STYLE)

        return itemsInfo


class _SeasonPurchaseInfo(object):
    __slots__ = ('__buckets', '__keyFunc')
    _ORDERED_KEYS = (GUI_ITEM_TYPE.ATTACHMENT,
     GUI_ITEM_TYPE.SEQUENCE,
     GUI_ITEM_TYPE.PROJECTION_DECAL,
     GUI_ITEM_TYPE.INSCRIPTION,
     GUI_ITEM_TYPE.PERSONAL_NUMBER,
     GUI_ITEM_TYPE.MODIFICATION,
     GUI_ITEM_TYPE.PAINT,
     GUI_ITEM_TYPE.CAMOUFLAGE,
     GUI_ITEM_TYPE.EMBLEM,
     GUI_ITEM_TYPE.STYLE)

    def __init__(self, keyFunc=None):
        self.__buckets = {key:{} for key in self._ORDERED_KEYS}
        self.__keyFunc = keyFunc or self.__defaultKeyFunc

    def add(self, purchaseItemInfo, typeID):
        if typeID in self._ORDERED_KEYS:
            bucket = self.__buckets[typeID]
            key = self.__keyFunc(purchaseItemInfo)
            if key in bucket:
                bucket[key].addPurchaseIndices(purchaseItemInfo.purchaseIndices)
            else:
                bucket[key] = purchaseItemInfo

    def flatten(self):
        items = []
        for key in self._ORDERED_KEYS:
            bucket = self.__buckets[key].values()
            bucket.sort(key=self.__keyFunc)
            items.extend(bucket)

        return items

    @staticmethod
    def __defaultKeyFunc(item):
        return item.intCD
