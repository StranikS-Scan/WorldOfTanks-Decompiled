# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization_2_0/carousel.py
from collections import defaultdict
from itertools import chain
from Event import Event
from data_aggregator import CUSTOMIZATION_TYPE
from slots import Slots
from filter import Filter, FILTER_TYPE, PURCHASE_TYPE
from shared import CAMOUFLAGE_GROUP_MAPPING
_RENDERER_WIDTH = {CUSTOMIZATION_TYPE.EMBLEM: 100,
 CUSTOMIZATION_TYPE.INSCRIPTION: 176,
 CUSTOMIZATION_TYPE.CAMOUFLAGE: 100}

class Carousel(object):

    def __init__(self, aggregatedData):
        self.__aData = aggregatedData
        self.__currentType = CUSTOMIZATION_TYPE.CAMOUFLAGE
        self.__currentSlotIdx = 0
        self.__currentDuration = 0
        self.__carouselItems = []
        self.filter = Filter(self.__aData.availableGroupNames)
        self.filter.changed += self.__updateCarouselData
        self.slots = Slots(self.__aData)
        self.slots.selected += self.__onSlotSelected
        self.slots.updated += self.__onSlotUpdated
        self.updated = Event()

    def fini(self):
        self.slots.selected -= self.__onSlotSelected
        self.slots.updated -= self.__onSlotUpdated
        self.filter.changed -= self.__updateCarouselData
        self.__carouselItems = None
        self.__aData = None
        self.slots.fini()
        self.filter.fini()
        return

    @property
    def items(self):
        return self.__carouselItems

    @property
    def currentType(self):
        return self.__currentType

    @property
    def currentSlotIdx(self):
        return self.__currentSlotIdx

    def applyItem(self, carouselItemIdx):
        carouselItem = self.__carouselItems[carouselItemIdx]
        self.slots.applyItem(carouselItem, duration=self.__currentDuration)

    def changeDuration(self, duration):
        self.__currentDuration = duration
        self.__updateCarouselData()

    def __onSlotSelected(self, newType, newSlotIdx):
        self.__currentType = newType
        self.__currentSlotIdx = newSlotIdx
        self.filter.setTypeAndIdx(newType, newSlotIdx)
        if newType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self.filter.set(FILTER_TYPE.GROUP, CAMOUFLAGE_GROUP_MAPPING[newSlotIdx])
        self.filter.apply()

    def __onSlotUpdated(self, newSlotData):
        if self.__currentType == newSlotData['type'] and self.__currentSlotIdx == newSlotData['idx']:
            self.filter.setTypeAndIdx(newSlotData['type'], newSlotData['idx'])
            self.__updateCarouselData()

    def __updateCarouselData(self):
        oldItemsCount = len(self.__carouselItems)
        del self.__carouselItems[:]
        appliedItems = defaultdict(list)
        purchasedItems = defaultdict(list)
        otherItems = defaultdict(list)
        allItems = [appliedItems, purchasedItems, otherItems]
        currentSlotItem = None
        installedItemID = self.slots.getInstalledItem(self.__currentSlotIdx, self.__currentType).getID()
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            displayedItems = {}
            for itemID, item in self.__aData.displayed[self.__currentType].iteritems():
                if item.getGroup() == CAMOUFLAGE_GROUP_MAPPING[self.__currentSlotIdx]:
                    displayedItems[itemID] = item

        else:
            displayedItems = self.__aData.displayed[self.__currentType]
        filterExceptions = {FILTER_TYPE.SHOW_IN_DOSSIER: self.__aData.installed[self.__currentType]}
        for itemID, item in displayedItems.iteritems():
            if self.filter.check(item, filterExceptions):
                appliedToCurrentSlot = itemID == self.slots.getSelectedSlotItemID()
                installedInSlot = itemID == installedItemID
                isInQuests = item.isInQuests and not item.isInDossier and self.filter.purchaseType == PURCHASE_TYPE.QUEST
                carouselItem = {'id': itemID,
                 'object': item,
                 'appliedToCurrentSlot': appliedToCurrentSlot,
                 'price': item.getPrice(self.__currentDuration),
                 'priceIsGold': item.priceIsGold(self.__currentDuration),
                 'isInDossier': item.isInDossier,
                 'isInQuests': isInQuests,
                 'duration': self.__currentDuration,
                 'installedInSlot': installedInSlot}
                if appliedToCurrentSlot:
                    currentSlotItem = carouselItem
                if installedInSlot:
                    group = appliedItems[item.getGroup()]
                elif item.isInDossier:
                    group = purchasedItems[item.getGroup()]
                else:
                    group = otherItems[item.getGroup()]
                if item.isFeatured:
                    group.insert(0, carouselItem)
                else:
                    group.append(carouselItem)

        for groupedItems in allItems:
            self.__carouselItems += chain(*groupedItems.values())

        if currentSlotItem is not None:
            goToIndex = currentSlotCarouselItemIdx = self.__carouselItems.index(currentSlotItem)
        else:
            currentSlotCarouselItemIdx = -1
            goToIndex = -1 if oldItemsCount == len(self.__carouselItems) else 0
        self.updated({'items': self.__carouselItems,
         'rendererWidth': _RENDERER_WIDTH[self.__currentType],
         'selectedIndex': currentSlotCarouselItemIdx,
         'goToIndex': goToIndex,
         'unfilteredLength': len(displayedItems)})
        return
