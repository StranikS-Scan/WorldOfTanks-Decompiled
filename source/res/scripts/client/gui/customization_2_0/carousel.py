# Embedded file name: scripts/client/gui/customization_2_0/carousel.py
import copy
import time
from collections import defaultdict
from itertools import chain
from Event import Event
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.functions import makeTooltip
from data_aggregator import CUSTOMIZATION_TYPE
from slots import Slots
from filter import Filter, FILTER_TYPE
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
        self.slots.updateSlot(self.__carouselItems[carouselItemIdx], duration=self.__currentDuration)

    def previewItem(self, carouselItemIdx):
        previewItemID = self.__carouselItems[carouselItemIdx]['id']
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            g_hangarSpace.space.updateVehicleCamouflage(camouflageID=previewItemID)
        else:
            self.__updateItemOnTank3DModel(previewItemID)

    def changeDuration(self, duration):
        self.__currentDuration = duration
        self.__updateCarouselData()

    def __updateItemOnTank3DModel(self, previewItemID):
        cType = self.__currentType
        slotIdx = self.__currentSlotIdx
        slotItem = self.slots.getData()['data'][cType]['data'][slotIdx]
        changedPreviewModel = copy.deepcopy(self.__aData.viewModel[1:3])
        rawInstalledItem = [previewItemID, time.time(), 0]
        if cType == CUSTOMIZATION_TYPE.INSCRIPTION:
            rawInstalledItem.append(0)
        changedPreviewModel[cType - 1][slotItem['spot'] + self.slots.calculateVehicleIndex(slotIdx, cType)] = rawInstalledItem
        g_hangarSpace.space.updateVehicleSticker(changedPreviewModel)

    def __onSlotSelected(self, newType, newSlotIdx):
        self.__currentType = newType
        self.__currentSlotIdx = newSlotIdx
        self.filter.setTypeAndIdx(newType, newSlotIdx, self.slots.getSelectedSlotItemID(), self.slots.getInstalledItem(self.__currentSlotIdx, self.__currentType).getID())
        if newType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self.filter.set(FILTER_TYPE.GROUP, CAMOUFLAGE_GROUP_MAPPING[newSlotIdx])
        self.filter.apply()

    def __getBtnTooltip(self, installedInSlot):
        if installedInSlot:
            params = (TOOLTIPS.CUSTOMIZATION_CAROUSEL_SLOT_REMOVE_HEADER, TOOLTIPS.CUSTOMIZATION_CAROUSEL_SLOT_REMOVE_BODY)
        else:
            params = (TOOLTIPS.CUSTOMIZATION_CAROUSEL_SLOT_SELECT_HEADER, TOOLTIPS.CUSTOMIZATION_CAROUSEL_SLOT_SELECT_BODY)
        return makeTooltip(*params)

    def __onSlotUpdated(self, newSlotData):
        if self.__currentType == newSlotData['type'] and self.__currentSlotIdx == newSlotData['idx']:
            self.filter.setTypeAndIdx(newSlotData['type'], newSlotData['idx'], newSlotData['data']['itemID'], self.slots.getInstalledItem(self.__currentSlotIdx, self.__currentType).getID())
            self.__updateCarouselData()

    def __updateCarouselData(self):
        oldItemsCount = len(self.__carouselItems)
        del self.__carouselItems[:]
        appliedItems = defaultdict(list)
        featuredItems = defaultdict(list)
        purchasedItems = defaultdict(list)
        otherItems = defaultdict(list)
        allItems = [appliedItems,
         purchasedItems,
         featuredItems,
         otherItems]
        currentSlotItem = None
        installedItemID = self.slots.getInstalledItem(self.__currentSlotIdx, self.__currentType).getID()
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            displayedItems = {}
            for itemID, item in self.__aData.displayed[self.__currentType].iteritems():
                if item.getGroup() == CAMOUFLAGE_GROUP_MAPPING[self.__currentSlotIdx]:
                    displayedItems[itemID] = item

        else:
            displayedItems = self.__aData.displayed[self.__currentType]
        for itemID, item in displayedItems.iteritems():
            if not self.filter.check(item):
                continue
            appliedToCurrentSlot = itemID == self.slots.getSelectedSlotItemID()
            installedInSlot = itemID == installedItemID
            carouselItem = {'id': itemID,
             'object': item,
             'appliedToCurrentSlot': appliedToCurrentSlot,
             'price': item.getPrice(self.__currentDuration),
             'priceIsGold': item.priceIsGold(self.__currentDuration),
             'isInDossier': item.isInDossier,
             'buttonTooltip': self.__getBtnTooltip(installedInSlot),
             'duration': self.__currentDuration,
             'installedInSlot': installedInSlot}
            if appliedToCurrentSlot:
                currentSlotItem = carouselItem
            if installedInSlot:
                appliedItems[item.getGroup()].append(carouselItem)
            elif item.isInDossier:
                purchasedItems[item.getGroup()].append(carouselItem)
            elif self.__currentType == CUSTOMIZATION_TYPE.INSCRIPTION and item.isFeatured():
                featuredItems[item.getGroup()].append(carouselItem)
            else:
                otherItems[item.getGroup()].append(carouselItem)

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
