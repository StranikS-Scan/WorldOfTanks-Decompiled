# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_carousel.py
from collections import defaultdict
from gui.Scaleform.daapi.view.lobby.customization.shared import TABS_ITEM_MAPPING, TYPE_TO_TAB_IDX, TYPES_ORDER, C11nTabs
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import createCustomizationBaseRequestCriteria

def comparisonKey(item):
    return (TYPES_ORDER.index(item.itemTypeID),
     not item.isRare(),
     item.groupID,
     item.id)


class CustomizationBookmarkVO(object):
    __slots__ = ('bookmarkName', 'bookmarkIndex')

    def __init__(self, bookmarkName, bookmarkIndex):
        self.bookmarkName = bookmarkName
        self.bookmarkIndex = bookmarkIndex

    def asDict(self):
        return {'bookmarkName': self.bookmarkName,
         'bookmarkIndex': self.bookmarkIndex}


class CustomizationSeasonAndTypeFilterData(object):
    __slots__ = ('allGroups', 'selectedGroupIndex', 'itemCount')

    def __init__(self):
        self.allGroups = []
        self.selectedGroupIndex = -1
        self.itemCount = 0


class CustomizationCarouselDataProvider(SortableDAAPIDataProvider):
    service = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, currentVehicle, carouselItemWrapper, proxy):
        super(CustomizationCarouselDataProvider, self).__init__()
        self._currentVehicle = currentVehicle
        self._tabIndex = 0
        self._seasonID = SeasonType.SUMMER
        self._onlyOwnedAndFreeItems = False
        self._historicOnlyItems = False
        self._onlyAppliedItems = False
        self._selectIntCD = None
        self.setItemWrapper(carouselItemWrapper)
        self._proxy = proxy
        self._currentlyApplied = set()
        self._allSeasonAndTabFilterData = {}
        self.updateTabGroups()
        return

    def updateTabGroups(self):
        self._allSeasonAndTabFilterData.clear()
        visibleTabs = defaultdict(set)
        c11nContext = self.service.getCtx()
        anchorsData = c11nContext.hangarSpace.getSlotPositions()
        requirement = createCustomizationBaseRequestCriteria(self._currentVehicle.item, self.eventsCache.questsProgress, self._proxy.getAppliedItems())
        allItems = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CUSTOMIZATIONS, requirement)
        for tabIndex in TABS_ITEM_MAPPING.iterkeys():
            self._allSeasonAndTabFilterData[tabIndex] = {}
            for season in SeasonType.COMMON_SEASONS:
                self._allSeasonAndTabFilterData[tabIndex][season] = CustomizationSeasonAndTypeFilterData()

        for item in sorted(allItems.itervalues(), key=comparisonKey):
            if item.isHiddenInUI():
                continue
            groupName = item.groupUserName
            tabIndex = TYPE_TO_TAB_IDX.get(item.itemTypeID)
            for seasonType in SeasonType.COMMON_SEASONS:
                if item.season & seasonType:
                    seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                    if groupName and groupName not in seasonAndTabData.allGroups:
                        seasonAndTabData.allGroups.append(groupName)
                    seasonAndTabData.itemCount += 1
                    if tabIndex not in C11nTabs.VISIBLE:
                        continue
                    if item.itemTypeID in (GUI_ITEM_TYPE.INSCRIPTION, GUI_ITEM_TYPE.EMBLEM):
                        for areaData in anchorsData.itervalues():
                            if areaData.get(item.itemTypeID):
                                hasSlots = True
                                break
                        else:
                            hasSlots = False

                        if not hasSlots:
                            continue
                    visibleTabs[seasonType].add(tabIndex)

        c11nContext.updateVisibleTabsList(visibleTabs)
        for tabIndex in TABS_ITEM_MAPPING.iterkeys():
            for seasonType in SeasonType.COMMON_SEASONS:
                seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                seasonAndTabData.allGroups.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_ALLGROUPS))
                seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1

        self._customizationItems = []
        self._itemSizeData = []
        self._customizationBookmarks = []
        self._selectedIdx = -1

    def clear(self):
        del self._customizationItems[:]
        del self._itemSizeData[:]
        del self._customizationBookmarks[:]
        self._selectedIdx = -1

    def fini(self):
        self.clear()
        self.destroy()

    def pyGetSelectedIdx(self):
        return self._selectedIdx

    @property
    def collection(self):
        return self._customizationItems

    def emptyItem(self):
        return None

    def getItemSizeData(self):
        return self._itemSizeData

    def getSeasonAndTabData(self, tabIndex, seasonType):
        return self._allSeasonAndTabFilterData[tabIndex][seasonType]

    def getBookmarkData(self):
        return self._customizationBookmarks

    @property
    def itemCount(self):
        return len(self._customizationItems)

    @property
    def totalItemCount(self):
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        return seasonAndTabData.itemCount

    def clearFilter(self):
        self._onlyOwnedAndFreeItems = False
        self._historicOnlyItems = False
        self._onlyAppliedItems = False
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1
        self.buildList(self._tabIndex, self._seasonID)

    def selectItem(self, item=None):
        if not item:
            self._selectIntCD = None
        else:
            self._selectIntCD = item.intCD
        return

    def selectItemIdx(self, itemIndex):
        self._selectedIdx = itemIndex
        self.refresh()

    def refresh(self):
        self._currentlyApplied = self._proxy.getAppliedItems(isOriginal=False)
        super(CustomizationCarouselDataProvider, self).refresh()

    def getFilterData(self):
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        return {'purchasedEnabled': self._onlyOwnedAndFreeItems,
         'historicEnabled': self._historicOnlyItems,
         'appliedEnabled': self._onlyAppliedItems,
         'groups': seasonAndTabData.allGroups,
         'selectedGroup': seasonAndTabData.selectedGroupIndex,
         'groupCount': len(seasonAndTabData.allGroups)}

    def getCurrentlyApplied(self):
        return self._currentlyApplied

    def buildList(self, tabIndex, season, refresh=True):
        self._tabIndex = tabIndex
        self._seasonID = season
        self.clear()
        self._buildCustomizationItems()
        if refresh:
            self.refresh()

    def setActiveGroupIndex(self, index):
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        seasonAndTabData.selectedGroupIndex = index

    def setHistoricalFilter(self, value):
        self._historicOnlyItems = value

    def setOwnedFilter(self, value):
        self._onlyOwnedAndFreeItems = value

    def setAppliedFilter(self, value):
        self._onlyAppliedItems = value

    def getOwnedFilter(self):
        return self._onlyOwnedAndFreeItems

    def getAppliedFilter(self):
        return self._onlyAppliedItems

    def _dispose(self):
        del self._customizationItems[:]
        del self._itemSizeData[:]
        del self._customizationBookmarks[:]
        super(CustomizationCarouselDataProvider, self)._dispose()

    def _buildCustomizationItems(self):
        season = self._seasonID
        requirement = createCustomizationBaseRequestCriteria(self._currentVehicle.item, self.eventsCache.questsProgress, self._proxy.getAppliedItems(), season)
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][season]
        allItemsGroup = len(seasonAndTabData.allGroups) - 1
        if seasonAndTabData.selectedGroupIndex != allItemsGroup:
            selectedGroup = seasonAndTabData.allGroups[seasonAndTabData.selectedGroupIndex]
            requirement |= REQ_CRITERIA.CUSTOMIZATION.ONLY_IN_GROUP(selectedGroup)
        if self._historicOnlyItems:
            requirement |= ~REQ_CRITERIA.CUSTOMIZATION.HISTORICAL
        if self._onlyOwnedAndFreeItems:
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: self._proxy.getItemInventoryCount(item) > 0)
        if self._onlyAppliedItems:
            appliedItems = self._proxy.getAppliedItems(isOriginal=False)
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: item.intCD in appliedItems)
        allItems = self.itemsCache.items.getItems(TABS_ITEM_MAPPING[self._tabIndex], requirement)
        self._customizationItems = []
        self._customizationBookmarks = []
        lastGroupID = None
        for idx, item in enumerate(sorted(allItems.itervalues(), key=comparisonKey)):
            if item.isHiddenInUI():
                continue
            groupID = item.groupID
            if item.intCD == self._selectIntCD:
                self._selectedIdx = len(self._customizationItems)
                self._selectIntCD = None
            if groupID != lastGroupID:
                lastGroupID = groupID
                self._customizationBookmarks.append(CustomizationBookmarkVO(item.groupUserName, idx).asDict())
            self._customizationItems.append(item.intCD)
            self._itemSizeData.append(item.isWide())

        c11nContext = self.service.getCtx()
        c11nContext.setCarouselItems(self.collection)
        return
