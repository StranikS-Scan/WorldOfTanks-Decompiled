# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_carousel.py
from collections import defaultdict
from gui.Scaleform.daapi.view.lobby.customization.shared import TABS_ITEM_TYPE_MAPPING, TYPE_TO_TAB_IDX, TABS_SLOT_TYPE_MAPPING, TYPES_ORDER, C11nTabs, getAllParentProjectionSlots
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, ProjectionDecalFormTags
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import createCustomizationBaseRequestCriteria

def comparisonKey(item):
    formfactorId = 0 if not hasattr(item, 'formfactor') else ProjectionDecalFormTags.ALL_FACTORS.index(item.formfactor)
    return (TYPES_ORDER.index(item.itemTypeID),
     not item.isRare(),
     item.groupID,
     formfactorId,
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
        self._formfactorGroupsFilterByTabIndex = defaultdict(dict)
        self._selectIntCD = None
        self.setItemWrapper(carouselItemWrapper)
        self._proxy = proxy
        self._currentlyApplied = set()
        self._customizationItems = []
        self._allCustomizationItems = None
        self._customizationBookmarks = []
        self._itemSizeData = []
        self._allSeasonAndTabFilterData = {}
        self.updateTabGroups()
        return

    def updateTabGroups(self):
        self._allSeasonAndTabFilterData.clear()
        self._formfactorGroupsFilterByTabIndex.clear()
        availableTabs = set()
        visibleTabs = defaultdict(set)
        stylesTabEnabled = {s:False for s in SeasonType.COMMON_SEASONS}
        c11nContext = self.service.getCtx()
        requirement = createCustomizationBaseRequestCriteria(self._currentVehicle.item, self.eventsCache.questsProgress, self._proxy.getAppliedItems())
        allItems = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CUSTOMIZATIONS, requirement)
        for tabIndex in C11nTabs.ALL:
            self._allSeasonAndTabFilterData[tabIndex] = {}
            if tabIndex == C11nTabs.PROJECTION_DECAL:
                self._formfactorGroupsFilterByTabIndex[tabIndex] = dict.fromkeys(ProjectionDecalFormTags.ALL_FACTORS, False)
            else:
                self._formfactorGroupsFilterByTabIndex[tabIndex] = {}
            for season in SeasonType.COMMON_SEASONS:
                self._allSeasonAndTabFilterData[tabIndex][season] = CustomizationSeasonAndTypeFilterData()

            slotType = TABS_SLOT_TYPE_MAPPING[tabIndex]
            if self.__hasSlots(slotType):
                availableTabs.add(tabIndex)

        for item in sorted(allItems.itervalues(), key=comparisonKey):
            if item.isHiddenInUI():
                continue
            groupName = item.groupUserName
            tabIndex = TYPE_TO_TAB_IDX.get(item.itemTypeID)
            if tabIndex not in availableTabs:
                continue
            for seasonType in SeasonType.COMMON_SEASONS:
                if item.season & seasonType:
                    seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                    if groupName and groupName not in seasonAndTabData.allGroups:
                        seasonAndTabData.allGroups.append(groupName)
                    seasonAndTabData.itemCount += 1
                    if tabIndex == C11nTabs.STYLE:
                        stylesTabEnabled[seasonType] = True
                    if tabIndex not in C11nTabs.VISIBLE:
                        continue
                    visibleTabs[seasonType].add(tabIndex)

        c11nContext.updateVisibleTabsList(visibleTabs, stylesTabEnabled)
        for tabIndex in C11nTabs.ALL:
            for seasonType in SeasonType.COMMON_SEASONS:
                seasonAndTabData = self._allSeasonAndTabFilterData[tabIndex][seasonType]
                seasonAndTabData.allGroups.append(_ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_FILTER_ALLGROUPS))
                seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1

        del self._customizationItems[:]
        del self._itemSizeData[:]
        del self._customizationBookmarks[:]
        self._selectedIdx = -1

    def __hasSlots(self, slotType):
        for areaId in Area.ALL:
            for _ in self._currentVehicle.item.getAnchors(slotType, areaId):
                return True

        return False

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
        self._formfactorGroupsFilterByTabIndex[self._tabIndex] = dict.fromkeys(self._formfactorGroupsFilterByTabIndex[self._tabIndex], False)
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        seasonAndTabData.selectedGroupIndex = len(seasonAndTabData.allGroups) - 1
        self.buildList(self._tabIndex, self._seasonID)

    def hasAppliedFilter(self):
        seasonAndTabData = self._allSeasonAndTabFilterData[self._tabIndex][self._seasonID]
        return self._onlyOwnedAndFreeItems or self._historicOnlyItems or self._onlyAppliedItems or seasonAndTabData.selectedGroupIndex != len(seasonAndTabData.allGroups) - 1 or any(self._formfactorGroupsFilterByTabIndex[self._tabIndex].itervalues())

    def selectItem(self, item=None):
        if not item:
            self._selectIntCD = None
        else:
            self._selectIntCD = item.intCD
        return

    def selectItemIdx(self, itemIndex):
        self._selectedIdx = itemIndex
        if self.service.getCtx().isAnyAnchorSelected() or self.service.getCtx().isCaruselItemSelected():
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
         'groupCount': len(seasonAndTabData.allGroups),
         'formfactorGroups': self._formfactorGroupsFilterByTabIndex[self._tabIndex].values()}

    def getCurrentlyApplied(self):
        return self._currentlyApplied

    def buildList(self, tabIndex, season, refresh=True):
        self._tabIndex = tabIndex
        self._seasonID = season
        self.clear()
        self._buildCustomizationItems()
        if refresh:
            self.refresh()

    def updateList(self, refresh=True):
        self._updateCustomizationItems()
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

    def setFormfactorGroupsFilter(self, value):
        self._formfactorGroupsFilterByTabIndex[self._tabIndex] = value

    def getOwnedFilter(self):
        return self._onlyOwnedAndFreeItems

    def getAppliedFilter(self):
        return self._onlyAppliedItems

    def getFormfactorGroupsFilter(self):
        return any(self._formfactorGroupsFilterByTabIndex[self._tabIndex].itervalues())

    def _dispose(self):
        del self._customizationItems[:]
        del self._itemSizeData[:]
        del self._customizationBookmarks[:]
        super(CustomizationCarouselDataProvider, self)._dispose()

    def _applyFilter(self, items, season):
        requirement = REQ_CRITERIA.EMPTY
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
        if any(self._formfactorGroupsFilterByTabIndex[self._tabIndex].itervalues()):
            formfactors = [ formfactorGroup for formfactorGroup, value in self._formfactorGroupsFilterByTabIndex[self._tabIndex].iteritems() if value ]
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: not hasattr(item, 'formfactor') or item.formfactor in formfactors)
        if self.service.getCtx().currentTab == C11nTabs.PROJECTION_DECAL:
            allFormsSet = set(ProjectionDecalFormTags.ALL_FACTORS)
            denyForms = [ slot.getUnsupportedForms(self._currentVehicle.item) for slot in getAllParentProjectionSlots(self._currentVehicle) ]
            for form in denyForms:
                allFormsSet.intersection_update(form)

            requirement |= REQ_CRITERIA.CUSTOM(lambda item: not hasattr(item, 'formfactor') or item.formfactor not in allFormsSet)
        filterdItems = {k:v for k, v in items.iteritems() if requirement(v)}
        return filterdItems

    def _buildCustomizationItems(self):
        requirement = self._createBaseRequestCriteriaBySeason(self._seasonID)
        if self._allCustomizationItems is None:
            self._allCustomizationItems = {}
        else:
            self._allCustomizationItems.clear()
        for itemTypeId in TABS_ITEM_TYPE_MAPPING[self._tabIndex]:
            self._allCustomizationItems.update(self.itemsCache.items.getItems(itemTypeId, requirement))

        self._updateCustomizationItems()
        return

    def _updateCustomizationItems(self):
        if self._allCustomizationItems is None:
            self._buildCustomizationItems()
            return
        else:
            filterdItems = self._applyFilter(self._allCustomizationItems, self._seasonID)
            del self._customizationItems[:]
            del self._customizationBookmarks[:]
            del self._itemSizeData[:]
            lastGroupID = None
            for item in sorted(filterdItems.itervalues(), key=comparisonKey):
                if item.isHiddenInUI():
                    continue
                groupID = item.groupID
                if item.intCD == self._selectIntCD:
                    self._selectedIdx = self.itemCount
                    self._selectIntCD = None
                if groupID != lastGroupID:
                    lastGroupID = groupID
                    self._customizationBookmarks.append(CustomizationBookmarkVO(item.groupUserName, self.itemCount).asDict())
                self._customizationItems.append(item.intCD)
                self._itemSizeData.append(item.isWide())

            self.service.getCtx().setCarouselItems(self.collection)
            return

    def _createBaseRequestCriteriaBySeason(self, season):
        return createCustomizationBaseRequestCriteria(self._currentVehicle.item, self.eventsCache.questsProgress, self._proxy.getAppliedItems(), season)
