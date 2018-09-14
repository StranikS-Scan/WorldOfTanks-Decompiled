# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/carousel.py
from collections import defaultdict
from itertools import chain
from account_helpers.AccountSettings import AccountSettings
from gui.customization.shared import checkInQuest, CAMOUFLAGE_GROUP_MAPPING, CUSTOMIZATION_TYPE, FILTER_TYPE
_RENDERER_WIDTH = {CUSTOMIZATION_TYPE.EMBLEM: 100,
 CUSTOMIZATION_TYPE.INSCRIPTION: 176,
 CUSTOMIZATION_TYPE.CAMOUFLAGE: 100}

class Carousel(object):

    def __init__(self, events, filter_, slots, dependencies):
        self.__currentVehicle = dependencies.g_currentVehicle
        self.__filter = filter_
        self.__slots = slots
        self.__events = events
        self.__currentType = CUSTOMIZATION_TYPE.CAMOUFLAGE
        self.__currentSlotIdx = 0
        self.__currentDuration = 0
        self.__carouselItems = []
        self.__displayedElements = None
        self.__goToIndex = 0
        self.__hasAppliedItem = False
        return

    def init(self):
        self.__filter.init()
        self.__events.onFilterUpdated += self.__update
        self.__events.onSlotSelected += self.__onSlotSelected
        self.__events.onSlotUpdated += self.__onSlotUpdated
        self.__events.onDisplayedElementsAndGroupsUpdated += self.__saveDisplayedElements
        self.__slots.init()

    def fini(self):
        self.__slots.fini()
        self.__events.onDisplayedElementsAndGroupsUpdated -= self.__saveDisplayedElements
        self.__events.onFilterUpdated -= self.__update
        self.__events.onSlotSelected -= self.__onSlotSelected
        self.__events.onSlotUpdated -= self.__onSlotUpdated
        self.__filter.fini()
        self.__displayedElements = None
        self.__goToIndex = 0
        self.__hasAppliedItem = False
        return

    @property
    def items(self):
        return self.__carouselItems

    def pickElement(self, carouselElementIdx):
        element = self.__carouselItems[carouselElementIdx]['element']
        self.__events.onCarouselElementPicked(element, self.__currentDuration, checkInQuest(element, self.__filter.purchaseType))

    def changeDuration(self, duration):
        self.__currentDuration = duration
        for item in self.__carouselItems:
            item['duration'] = self.__currentDuration

        self.__events.onCarouselUpdated({'items': self.__carouselItems,
         'rendererWidth': _RENDERER_WIDTH[self.__currentType],
         'goToIndex': self.__goToIndex,
         'unfilteredLength': len(self.__displayedElements[self.__currentType]),
         'hasAppliedItem': self.__hasAppliedItem})

    def __saveDisplayedElements(self, displayedElements, displayedGroups):
        self.__displayedElements = displayedElements

    def __onSlotSelected(self, newType, newSlotIdx, slotData):
        if self.__currentType != newType:
            self.__currentType = newType
            self.__goToIndex = 0
            self.__hasAppliedItem = False
        self.__currentSlotIdx = newSlotIdx
        if newType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            self.__filter.set(FILTER_TYPE.GROUP, CAMOUFLAGE_GROUP_MAPPING[newSlotIdx])
        else:
            self.__update()

    def __onSlotUpdated(self, newSlotData, cType, slotIdx):
        if self.__currentType == cType and self.__currentSlotIdx == slotIdx:
            self.__update()

    def __update(self):
        newElements = AccountSettings.getSettings('customization')
        newElementsSubset = newElements[self.__currentType].get(self.__currentVehicle.item.intCD, {})
        topItems = defaultdict(list)
        installedItems = defaultdict(list)
        purchasedItems = defaultdict(list)
        otherItems = defaultdict(list)
        allItems = [topItems,
         installedItems,
         purchasedItems,
         otherItems]
        currentSlotElement = self.__slots.getCurrentSlotData()['element']
        installedSlotElement = self.__slots.getInstalledSlotData()['element']
        currentCarouselItem = None
        self.__hasAppliedItem = False
        for elementID, element in self.__displayedElements[self.__currentType].iteritems():
            installedInCurrentSlot = False
            if installedSlotElement is not None:
                installedInCurrentSlot = elementID == installedSlotElement.getID()
            if self.__filter.check(element, installedInCurrentSlot) or element.isDisplayedFirst:
                appliedToCurrentSlot = False
                if currentSlotElement is not None:
                    appliedToCurrentSlot = elementID == currentSlotElement.getID() and not installedInCurrentSlot
                if not self.__hasAppliedItem and appliedToCurrentSlot:
                    self.__hasAppliedItem = True
                if element.isDisplayedFirst:
                    isEventElement = True
                else:
                    isEventElement = False
                if elementID in newElementsSubset:
                    isNewElement = newElementsSubset[elementID]
                    newElementsSubset[elementID] = False
                else:
                    isNewElement = False
                carouselItem = {'element': element,
                 'appliedToCurrentSlot': appliedToCurrentSlot,
                 'duration': self.__currentDuration,
                 'isNewElement': isNewElement,
                 'isEventElement': isEventElement,
                 'installedInCurrentSlot': installedInCurrentSlot}
                if element.isDisplayedFirst:
                    group = topItems[element.getGroup()]
                elif installedInCurrentSlot:
                    group = installedItems[element.getGroup()]
                elif element.isInDossier:
                    group = purchasedItems[element.getGroup()]
                else:
                    group = otherItems[element.getGroup()]
                if element.isFeatured:
                    group.insert(0, carouselItem)
                else:
                    group.append(carouselItem)
                if appliedToCurrentSlot:
                    currentCarouselItem = carouselItem

        AccountSettings.setSettings('customization', newElements)
        previousItemsCount = len(self.__carouselItems)
        del self.__carouselItems[:]
        for groupedItems in allItems:
            self.__carouselItems += chain(*groupedItems.values())

        currentItemsCount = len(self.__carouselItems)
        if currentCarouselItem is not None:
            self.__goToIndex = self.__carouselItems.index(currentCarouselItem)
        else:
            self.__goToIndex = -1 if previousItemsCount == currentItemsCount else 0
        if self.__currentType == CUSTOMIZATION_TYPE.CAMOUFLAGE:
            unfilteredLength = len(self.__carouselItems)
        else:
            unfilteredLength = len(self.__displayedElements[self.__currentType])
        self.__events.onCarouselUpdated({'items': self.__carouselItems,
         'rendererWidth': _RENDERER_WIDTH[self.__currentType],
         'goToIndex': self.__goToIndex,
         'unfilteredLength': unfilteredLength,
         'hasAppliedItem': self.__hasAppliedItem})
        return
