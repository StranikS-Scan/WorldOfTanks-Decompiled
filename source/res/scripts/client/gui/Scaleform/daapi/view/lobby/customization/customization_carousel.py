# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_carousel.py
from gui.Scaleform.daapi.view.lobby.customization.shared import TABS_ITEM_MAPPING, TYPE_TO_TAB_IDX
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

def comparisonKey(item):
    """ Comparison key to sort the the customization carousel.
    """
    return (item.groupID, item.id)


class CustomizationBookmarkVO(object):
    __slots__ = ('bookmarkName', 'bookmarkIndex')

    def __init__(self, bookmarkName, bookmarkIndex):
        self.bookmarkName = bookmarkName
        self.bookmarkIndex = bookmarkIndex

    def asDict(self):
        """
        Creates a dictionary with the class' relevant data.
        :return: data object
        """
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
        self._selectIntCD = None
        self.setItemWrapper(carouselItemWrapper)
        self._proxy = proxy
        self._allSeasonAndTabFilterData = {}
        requirement = self._createBaseRequirements()
        allItems = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CUSTOMIZATIONS, requirement)
        for tabIndex, cType in TABS_ITEM_MAPPING.iteritems():
            self._allSeasonAndTabFilterData[tabIndex] = {}
            for season in SeasonType.COMMON_SEASONS:
                self._allSeasonAndTabFilterData[tabIndex][season] = CustomizationSeasonAndTypeFilterData()

        for item in sorted(allItems.itervalues(), key=comparisonKey):
            groupName = item.groupUserName
            tabIndex = TYPE_TO_TAB_IDX.get(item.itemTypeID)
            for seasonType in SeasonType.COMMON_SEASONS:
                if item.season & seasonType:
                    seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                    if groupName and groupName not in seasonAndTabData.allGroups:
                        seasonAndTabData.allGroups.append(groupName)
                    seasonAndTabData.itemCount += 1

        for tabIndex in TABS_ITEM_MAPPING.iterkeys():
            for seasonType in SeasonType.COMMON_SEASONS:
                seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                seasonAndTabData.allGroups.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_ALLGROUPS))
                seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1

        self._customizationItems = []
        self._itemSizeData = []
        self._customizationBookmarks = []
        self._selectedIdx = -1
        return

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
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1
        self.buildList(self._tabIndex, self._seasonID)

    def selectItem(self, item=None):
        """ Select a Customization Item by item itself.
        """
        if not item:
            self._selectIntCD = None
        else:
            self._selectIntCD = item.intCD
        return

    def selectItemIdx(self, itemIndex):
        """ Select a Customization Item by index.
        
        :param itemIndex: index in the carousel of the selected item
        """
        self._selectedIdx = itemIndex
        self.refresh()

    def getFilterData(self):
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        return {'purchasedEnabled': self._onlyOwnedAndFreeItems,
         'historicEnabled': self._historicOnlyItems,
         'groups': seasonAndTabData.allGroups,
         'selectedGroup': seasonAndTabData.selectedGroupIndex,
         'groupCount': len(seasonAndTabData.allGroups)}

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
        if self._historicOnlyItems != value:
            self._historicOnlyItems = value

    def setOwnedFilter(self, value):
        if self._onlyOwnedAndFreeItems != value:
            self._onlyOwnedAndFreeItems = value

    def _dispose(self):
        del self._customizationItems[:]
        del self._itemSizeData[:]
        del self._customizationBookmarks[:]
        super(CustomizationCarouselDataProvider, self)._dispose()

    def _createBaseRequirements(self, season=None, includeApplied=True):
        appliedItems = set()
        for seasonType in SeasonType.COMMON_SEASONS:
            outfit = self._proxy.getModifiedOutfit(seasonType)
            appliedItems.add((i.intCD for i in outfit.items()))

        vehicle = self._currentVehicle.item
        season = season or SeasonType.ALL
        progress = self.eventsCache.randomQuestsProgress
        criteria = REQ_CRITERIA.CUSTOM(lambda item: item.mayInstall(vehicle) and item.season & season and (not item.isHidden or item.fullInventoryCount(vehicle) > 0 or includeApplied and item.intCD in appliedItems) and (not item.requiredToken or progress.getTokenCount(item.requiredToken) > 0))
        return criteria

    def _buildCustomizationItems(self):
        season = self._seasonID
        requirement = self._createBaseRequirements(season, includeApplied=True)
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        allItemsGroup = len(seasonAndTabData.allGroups) - 1
        if seasonAndTabData.selectedGroupIndex != allItemsGroup:
            selectedGroup = seasonAndTabData.allGroups[seasonAndTabData.selectedGroupIndex]
            requirement |= REQ_CRITERIA.CUSTOMIZATION.ONLY_IN_GROUP(selectedGroup)
        if self._historicOnlyItems:
            requirement |= REQ_CRITERIA.CUSTOMIZATION.HISTORICAL
        if self._onlyOwnedAndFreeItems:
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: self._proxy.getItemInventoryCount(item) > 0)
        allItems = self.itemsCache.items.getItems(TABS_ITEM_MAPPING[self._tabIndex], requirement)
        self._customizationItems = []
        self._customizationBookmarks = []
        lastGroupID = None
        for idx, item in enumerate(sorted(allItems.itervalues(), key=comparisonKey)):
            groupID = item.groupID
            if item.intCD == self._selectIntCD:
                self._selectedIdx = len(self._customizationItems)
                self._selectIntCD = None
            if groupID != lastGroupID:
                lastGroupID = groupID
                self._customizationBookmarks.append(CustomizationBookmarkVO(item.groupUserName.upper(), idx).asDict())
            self._customizationItems.append(item.intCD)
            self._itemSizeData.append(item.isWide())

        return
