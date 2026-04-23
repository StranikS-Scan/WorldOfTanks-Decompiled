# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_carousel_helpers.py
import logging
from collections import OrderedDict, defaultdict, namedtuple
from itertools import chain
from typing import TYPE_CHECKING
from CurrentVehicle import g_currentVehicle
from cache import cached_property
from gui.customization.constants import CustomizationModes, INVALID_ID
from gui.customization.shared import C11N_ITEM_TYPE_MAP, createCustomizationBaseRequestCriteria, getAncestors, getBaseStyleItems, getGroupHelper, getInheritors
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.customization.filter_types import AvailabilityFilterState, CarouselFilterTypes, FILTER_ALIAS_MAPPING, FILTER_TYPES_MAPPING, FilterAliases, FilterTypes
from gui.impl.lobby.customization.settings_constants import CustomizationFilter, getCustomizationFilterDefaults
from gui.impl.lobby.customization.shared import CustomizationTabs, getTabByItem, getTabGroupId, isItemLimitReached, isItemUsedUp, vehicleHasSlot
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from gui.shared.utils.requesters.ItemsRequester import PredicateCondition
from helpers import dependency
from items import vehicles
from items.components.c11n_constants import EMPTY_ITEM_ID, ItemTags, ProjectionDecalFormTags, SeasonType
from shared_utils import getFullClassName
from skeletons.account_helpers.settings_repository import SettingsSerializable
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Set, Tuple
    from gui.shared.gui_items.customization.c11n_items import Customization
_logger = logging.getLogger(__name__)

def comparisonKey(item):
    isNationalEmblem = ItemTags.NATIONAL_EMBLEM in item.tags
    formfactorId = ProjectionDecalFormTags.ALL.index(item.formfactor) if hasattr(item, 'formfactor') and item.formfactor else 0
    tabId = getTabByItem(item)
    isProgressiveDecal = item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL and item.isProgressive
    return (tabId,
     not isProgressiveDecal,
     not isNationalEmblem,
     not item.isRare(),
     item.groupID,
     not item.markedAsFavorite,
     -item.orderingNumber,
     formfactorId,
     -item.id)


def comparisonKeyByDate(item):
    tabId = getTabByItem(item)
    isProgressiveDecal = item.itemTypeID == GUI_ITEM_TYPE.PROJECTION_DECAL and item.isProgressive
    return (tabId,
     not isProgressiveDecal,
     not item.markedAsFavorite,
     -item.orderingNumber,
     -item.id)


SelectedItem = namedtuple('SelectedItem', ('intCD', 'idx'))
SelectedItem.__new__.__defaults__ = (-1, -1)

class _CustomizationFiltersSettingsSerializable(SettingsSerializable):

    @classmethod
    def getSettingsID(cls):
        return getFullClassName(_CustomizationFiltersSettingsSerializable)


class ItemsData(object):

    def __init__(self, items=None, groups=None):
        self.items = items or []
        self.groups = groups or OrderedDict()

    @cached_property
    def hasUsedUpItems(self):
        return any((isItemUsedUp(item) for item in self.items))

    @cached_property
    def hasProgressiveItems(self):
        return any((item.isProgressive for item in self.items))

    @cached_property
    def hasQuestProgressItems(self):
        return any((item.isQuestsProgression for item in self.items))


class CarouselData(object):
    __slots__ = ('items', 'sizes', 'bookmarks', 'arrows', 'showSeparators')

    def __init__(self):
        self.items = []
        self.sizes = []
        self.bookmarks = []
        self.arrows = []
        self.showSeparators = False


class CarouselCache(_CustomizationFiltersSettingsSerializable):
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, createFilterCriteria, createSortCriteria):
        self.__itemsData = defaultdict(lambda : defaultdict(OrderedDict))
        self.__carouselData = {}
        self.__createFilterCriteria = createFilterCriteria
        self.__createSortCriteria = createSortCriteria
        self.__cachedEditableStyleId = 0
        self.__ctx = self.__service.getCtx()

    def fini(self):
        self.invalidateItemsData()
        self.invalidateCarouselData()
        self.__invalidateEditableStyleCache()
        self.__createFilterCriteria = None
        self.__createSortCriteria = None
        self.__ctx = None
        return

    def getVisibleTabs(self):
        season, modeId = self.__ctx.season, self.__ctx.modeId
        self.__invalidateEditableStyleCache()
        self.__initCache()
        if modeId == CustomizationModes.EDITABLE_STYLE:
            visibleTabs = self.__itemsData[modeId][season].keys()
        else:
            visibleTabs = self.__itemsData[CustomizationModes.STYLED_3D][season].keys()
            visibleTabs += self.__itemsData[CustomizationModes.STYLED_2D][season].keys()
            visibleTabs += self.__itemsData[CustomizationModes.CUSTOM][season].keys()
        visibleTabs.sort(key=getTabGroupId)
        return visibleTabs

    def getItemsData(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.tabId
        self.__invalidateEditableStyleCache()
        self.__initCache()
        itemsData = self.__itemsData[modeId][season].get(tabId, ItemsData())
        return itemsData

    def getCarouselData(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.tabId
        self.__invalidateEditableStyleCache()
        carouselData = self.__carouselData.get(modeId, {}).get(season, {}).get(tabId)
        if carouselData is None:
            carouselData = self.__getCarouselData(season, modeId, tabId)
            self.__carouselData.setdefault(modeId, {}).setdefault(season, {})[tabId] = carouselData
        return carouselData

    def getNonFilteredItemsData(self, season=None, modeId=None, tabId=None):
        itemsData = self.getItemsData(season, modeId, tabId).items
        filteredItems = filter(self.__createFilterCriteria(), itemsData)
        return list(set(itemsData) - set(filteredItems))

    def getCountersForCtx(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.tabId
        itemsData = self.getItemsData(season, modeId, tabId).items
        filteredItems = filter(self.__createFilterCriteria(), itemsData)
        filteredOutItemsData = list(set(itemsData) - set(filteredItems))
        newHiddenItemsCounter = sum([ g_currentVehicle.item.getC11nItemNoveltyCounter(g_currentVehicle.itemsCache.items, newItem) for newItem in filteredOutItemsData ])
        self.__ctx.filteredItemsCounter = len(filteredItems)
        self.__ctx.itemsDataCounter = len(itemsData)
        self.__ctx.newHiddenItemsCounter = newHiddenItemsCounter
        return (len(filteredItems), len(itemsData), newHiddenItemsCounter)

    def invalidateItemsData(self):
        self.__itemsData.clear()
        self.__cachedEditableStyleId = 0

    def invalidateCarouselData(self):
        self.__carouselData.clear()

    def __initCache(self):
        if not self.__itemsData:
            self.__initItemsData()
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE and not self.__cachedEditableStyleId:
            self.__initEditableStyleItemsData()

    def __getDisplayKey(self):
        self._loadSettings()
        return comparisonKey if self.getSetting(CustomizationFilter.DISPLAY_GROUP, 0) else comparisonKeyByDate

    def __getCarouselData(self, season=None, modeId=None, tabId=None):
        itemsData = self.getItemsData(season, modeId, tabId)
        filteredItems = filter(self.__createFilterCriteria(), itemsData.items)
        sortCriteria = self.__createSortCriteria()
        showBookmarks = True
        if sortCriteria:
            filteredItems.sort(key=sortCriteria)
            showBookmarks = False
        if self.__ctx.mode.modeId != CustomizationModes.EDITABLE_STYLE:
            filteredItems = sorted(filteredItems, key=self.__getDisplayKey())
        carouselData = CarouselData()
        lastGroupID = None
        carouselData.showSeparators = itemsData.hasQuestProgressItems and self.__ctx.mode.modeId == CustomizationModes.EDITABLE_STYLE
        for idx, item in enumerate(filteredItems):
            helper = getGroupHelper(item)
            groupID = helper.getGroupID()
            groupUserName = helper.getGroupName()
            if showBookmarks and groupID != lastGroupID:
                lastGroupID = groupID
                bookmark = {'bookmarkName': groupUserName,
                 'bookmarkIndex': len(carouselData.items),
                 'isProgressive': item.isProgressive}
                carouselData.bookmarks.append(bookmark)
            isLastItem = idx == len(filteredItems) - 1
            if item.isQuestsProgression and not isLastItem:
                nextItem = filteredItems[idx + 1]
                nextGroupID = getGroupHelper(nextItem).getGroupID()
                if nextItem and nextGroupID == groupID and item.descriptor.requiredTokenCount != nextItem.descriptor.requiredTokenCount:
                    arrow = {'index': idx,
                     'enabled': item.isUnlockedByToken()}
                    carouselData.arrows.append(arrow)
            carouselData.items.append(item.intCD)
            carouselData.sizes.append(item.isWide())

        return carouselData

    def __initItemsData(self):
        self.__itemsData.clear()
        requirement = createCustomizationBaseRequestCriteria(g_currentVehicle.item, self.__eventsCache.questsProgress, self.__ctx.mode.getAppliedItems())
        requirement |= REQ_CRITERIA.CUSTOM(lambda item: not item.isHiddenInUI())
        itemTypes = []
        for tabId, slotType in CustomizationTabs.SLOT_TYPES.iteritems():
            if vehicleHasSlot(slotType):
                itemTypes.extend(CustomizationTabs.ITEM_TYPES[tabId])

        allItems = []
        customizationCache = vehicles.g_cache.customization20().itemTypes
        cTypes = set((C11N_ITEM_TYPE_MAP[iType] for iType in itemTypes if iType in C11N_ITEM_TYPE_MAP))
        for cType in cTypes:
            for itemID in customizationCache[cType]:
                if itemID == EMPTY_ITEM_ID:
                    continue
                intCD = vehicles.makeIntCompactDescrByID('customizationItem', cType, itemID)
                item = self.__service.getItemByCD(intCD)
                if requirement(item):
                    allItems.append(item)

        sortedItems = sorted(allItems, key=self.__getDisplayKey())
        for item in sortedItems:
            tabId = getTabByItem(item)
            modeId = (CustomizationModes.STYLED_2D if tabId in CustomizationTabs.STYLES_2D else CustomizationModes.STYLED_3D) if tabId in CustomizationTabs.STYLES_ALL else CustomizationModes.CUSTOM
            for season in SeasonType.COMMON_SEASONS:
                if not item.season & season:
                    continue
                itemsDataStorage = self.__itemsData[modeId][season]
                if not itemsDataStorage or tabId != itemsDataStorage.keys()[-1]:
                    itemsDataStorage[tabId] = ItemsData()
                itemsData = itemsDataStorage.values()[-1]
                if not itemsData.groups or item.groupID != itemsData.groups.keys()[-1]:
                    itemsData.groups[item.groupID] = item.groupUserName
                itemsData.items.append(item)

    def __initEditableStyleItemsData(self):
        style = self.__ctx.mode.style
        if CustomizationModes.EDITABLE_STYLE in self.__itemsData:
            self.__itemsData[CustomizationModes.EDITABLE_STYLE].clear()
        vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
        itemsFilter = style.descriptor.isItemInstallable
        for season in SeasonType.COMMON_SEASONS:
            itemsDataStorage = self.__itemsData[CustomizationModes.CUSTOM][season]
            styleBaseOutfit = style.getOutfit(season, vehicleCD)
            styleBaseItems = [ self.__service.getItemByCD(intCD) for intCD in styleBaseOutfit.items() ]
            for tabId, itemsData in itemsDataStorage.iteritems():
                itemTypes = CustomizationTabs.ITEM_TYPES[tabId]
                questItems = []
                questItemsIDs = []
                if style.isQuestsProgression:
                    qProg = style.descriptor.questsProgression
                    for token in sorted(qProg.getGroupTokens()):
                        groupItems = qProg.getItemsForGroup(token)
                        for itemsForLevel in groupItems:
                            for itemType in itemTypes:
                                c11nType = C11N_ITEM_TYPE_MAP[itemType]
                                itemsIdsForType = itemsForLevel.get(c11nType, ())
                                buf = [ self.__service.getItemByID(itemType, itemId) for itemId in itemsIdsForType ]
                                for item in buf:
                                    if item.itemTypeID in itemTypes and item.season & season:
                                        questItems.append(item)
                                        questItemsIDs.append(item.id)

                filteredItems = [ item for item in itemsData.items if itemsFilter(item.descriptor) and item.id not in questItemsIDs ]
                alternateItems = []
                for itemType in itemTypes:
                    c11nType = C11N_ITEM_TYPE_MAP[itemType]
                    alternateItemIds = style.descriptor.alternateItems.get(c11nType, ())
                    buf = [ self.__service.getItemByID(itemType, itemId) for itemId in alternateItemIds if itemId not in questItemsIDs ]
                    alternateItems.extend([ i for i in buf if i.itemTypeID in itemTypes and i.season & season ])

                if not any((questItems, alternateItems, filteredItems)):
                    continue
                baseItems = [ item for item in styleBaseItems if item.itemTypeID in itemTypes and item.season & season and item.id not in questItemsIDs ]
                items = questItems + sorted(set(chain(alternateItems, filteredItems, baseItems)), key=self.__getDisplayKey())
                groups = OrderedDict()
                for item in items:
                    helper = getGroupHelper(item)
                    groupID = helper.getGroupID()
                    groupUserName = helper.getGroupName()
                    if not groups or groupID != groups.keys()[-1]:
                        groups[groupID] = groupUserName

                self.__itemsData[CustomizationModes.EDITABLE_STYLE][season][tabId] = ItemsData(items, groups)

        self.__cachedEditableStyleId = style.id

    def __invalidateEditableStyleCache(self):
        if self.__ctx.modeId != CustomizationModes.EDITABLE_STYLE:
            return
        if self.__cachedEditableStyleId == self.__ctx.mode.style.id:
            return
        self.__cachedEditableStyleId = 0
        if CustomizationModes.EDITABLE_STYLE in self.__itemsData:
            self.__itemsData[CustomizationModes.EDITABLE_STYLE].clear()
        self.__carouselData.get(self.__ctx.modeId, {}).clear()


class CustomizationCarouselDataProvider(_CustomizationFiltersSettingsSerializable):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(CustomizationCarouselDataProvider, self).__init__()
        self.__ctx = self.__service.getCtx()
        self.__selectedItem = SelectedItem()
        self.__selectedGroup = {}
        self.__carouselFilters = {}
        self.__appliedItems = set()
        self.__baseStyleItems = set()
        self.__dependentItems = tuple()
        self.__carouselData = CarouselData()
        self.__carouselCache = CarouselCache(createFilterCriteria=self.__createFilterCriteria, createSortCriteria=self.__createSortCriteria)
        self.__initFilters()

    def init(self):
        self._loadSettings()

    def fini(self):
        self.__carouselCache.fini()
        self.__carouselCache = None
        self.__ctx = None
        self.__carouselData = None
        self.__selectedGroup.clear()
        self.__appliedItems.clear()
        self.__baseStyleItems.clear()
        self.__carouselFilters.clear()
        self._dumpSettings()
        return

    @property
    def collection(self):
        return self.__carouselData.items

    @property
    def itemCount(self):
        return len(self.__carouselData.items)

    @property
    def totalItemCount(self):
        return len(self.__carouselCache.getItemsData().items)

    def pyGetSelectedIdx(self):
        return self.__selectedItem.idx

    def refresh(self):
        if not g_currentVehicle.isPresent():
            return
        self.__baseStyleItems = getBaseStyleItems()

    def buildList(self):
        self.__appliedItems = self.__ctx.mode.getAppliedItems(isOriginal=False)
        for camoIntCD, dependentItems in self.__ctx.mode.getDependenciesData().iteritems():
            if camoIntCD in self.__appliedItems:
                self.__dependentItems = dependentItems
                break
        else:
            self.__dependentItems = tuple()

        self.__updateCarouselData()

    def getVisibleTabs(self):
        return self.__carouselCache.getVisibleTabs()

    def getItemsData(self, season=None, modeId=None, tabId=None):
        return self.__carouselCache.getItemsData(season, modeId, tabId)

    def getCarouselData(self, season=None, modeId=None, tabId=None):
        return self.__carouselCache.getCarouselData(season, modeId, tabId)

    def getCountersForCtx(self, season=None, modeId=None, tabId=None):
        return self.__carouselCache.getCountersForCtx(season, modeId, tabId)

    def getAppliedItems(self):
        return self.__appliedItems

    def getBaseStyleItems(self):
        return self.__baseStyleItems

    def getItemSizeData(self):
        return self.__carouselData.sizes

    def getBookmarskData(self):
        return self.__carouselData.bookmarks

    def getArrowsData(self):
        return self.__carouselData.arrows

    def getShowSeparatorsData(self):
        return self.__carouselData.showSeparators

    def getDependentItems(self):
        return self.__dependentItems

    def processDependentParams(self, item):
        isMarkedAsDependent = False
        isUnsuitable = False
        styleDependencies = self.__ctx.mode.getDependenciesData()
        if styleDependencies:
            itemCD = item.intCD
            isApplied = itemCD in self.getAppliedItems()
            if item.itemTypeID == GUI_ITEM_TYPE.CAMOUFLAGE:
                if isApplied:
                    isMarkedAsDependent = bool(getInheritors(itemCD, styleDependencies))
            else:
                selectedDependentItems = self.getDependentItems()
                if selectedDependentItems:
                    if itemCD in selectedDependentItems:
                        isMarkedAsDependent = isApplied
                    elif getAncestors(itemCD, styleDependencies):
                        isUnsuitable = True
        return (isMarkedAsDependent, isUnsuitable)

    def modeChanged(self, modeId, prevModeId):
        visibleTabs = self.getVisibleTabs()
        if not visibleTabs:
            return
        if CustomizationModes.EDITABLE_STYLE in (modeId, prevModeId):
            tabId = visibleTabs[0]
            if modeId == CustomizationModes.EDITABLE_STYLE:
                if self.__ctx.mode.getDependenciesData():
                    if CustomizationTabs.CAMOUFLAGES in visibleTabs:
                        tabId = CustomizationTabs.CAMOUFLAGES
                    else:
                        _logger.warning('Style with dependencies have to open Camouflages tab, but this tab is not found!')
            else:
                styleItem = self.__ctx.mode.currentOutfit.style
                if styleItem:
                    tabId = getTabByItem(styleItem)
            self.__ctx.changeTab(tabId)

    def hasAppliedFilter(self):
        isGroupSelected = self.__getSelectedGroupIdx() is not None
        isAnyFilterApplied = any((carouselFilter.isApplied() for carouselFilter in self.__carouselFilters.itervalues()))
        return isAnyFilterApplied or isGroupSelected

    def hasNewNonFilteredItem(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.tabId
        return any([ item.isNew() for item in self.__carouselCache.getNonFilteredItemsData(season, modeId, tabId) ])

    def refreshNewHiddenElementsCount(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.tabId
        items = self.__carouselCache.getNonFilteredItemsData(season, modeId, tabId)
        newHiddenElementsCount = sum([ g_currentVehicle.item.getC11nItemNoveltyCounter(g_currentVehicle.itemsCache.items, i) for i in items ])
        self.__ctx.newHiddenElementsCount = newHiddenElementsCount
        return newHiddenElementsCount

    def selectItem(self, item=None):
        prevSelectedItem = self.__selectedItem
        intCD = item.intCD if item is not None else -1
        self.__updateSelection(intCD)
        if prevSelectedItem != self.__selectedItem:
            self.refresh()
        return

    def getNextItem(self, reverse):
        if self.__selectedItem.idx == INVALID_ID:
            return None
        else:
            outfits = self.__ctx.mode.getModifiedOutfits()
            shift = -1 if reverse else 1
            itemsCount = len(self.collection)
            idx = self.__selectedItem.idx + shift
            while 0 <= idx < itemsCount:
                intCD = self.collection[idx]
                item = self.__service.getItemByCD(intCD)
                if not isItemLimitReached(item, outfits) or item.isStyleOnly and not self.processDependentParams(item)[1]:
                    return item
                idx += shift

            return None

    def getDisplayGroupsData(self):
        return (backport.text(R.strings.vehicle_customization.filter.popover.displayBy.date()), backport.text(R.strings.vehicle_customization.filter.popover.displayBy.group()))

    def getFilterData(self):
        return {CarouselFilterTypes.INVENTORY: self.isFilterApplied(FilterTypes.INVENTORY),
         CarouselFilterTypes.SALE: self.isFilterApplied(FilterTypes.SALE),
         CarouselFilterTypes.HISTORIC: self.isFilterApplied(FilterTypes.HISTORIC, FilterAliases.HISTORIC),
         CarouselFilterTypes.NON_HISTORIC: self.isFilterApplied(FilterTypes.HISTORIC, FilterAliases.NON_HISTORIC),
         CarouselFilterTypes.FANTASTICAL: self.isFilterApplied(FilterTypes.HISTORIC, FilterAliases.FANTASTICAL),
         CarouselFilterTypes.APPLIED: self.isFilterApplied(FilterTypes.APPLIED),
         CarouselFilterTypes.FAVORITE: self.isFilterApplied(FilterTypes.FAVORITE),
         CarouselFilterTypes.GROUP: self.__getSelectedGroupIdx(),
         CarouselFilterTypes.DISPLAY_GROUP: self.getSetting(CustomizationFilter.DISPLAY_GROUP, 0),
         CarouselFilterTypes.FORMFACTOR_SQUARE: self.isFilterApplied(FilterTypes.FORMFACTORS, FilterAliases.FORMFACTOR_SQUARE),
         CarouselFilterTypes.FORMFACTOR_RECT1X2: self.isFilterApplied(FilterTypes.FORMFACTORS, FilterAliases.FORMFACTOR_RECT1X2),
         CarouselFilterTypes.FORMFACTOR_RECT1X3: self.isFilterApplied(FilterTypes.FORMFACTORS, FilterAliases.FORMFACTOR_RECT1X3),
         CarouselFilterTypes.FORMFACTOR_RECT1X4: self.isFilterApplied(FilterTypes.FORMFACTORS, FilterAliases.FORMFACTOR_RECT1X4),
         CarouselFilterTypes.FORMFACTOR_RECT1X6: self.isFilterApplied(FilterTypes.FORMFACTORS, FilterAliases.FORMFACTOR_RECT1X6),
         CarouselFilterTypes.ON_ANOTHER_VEH: self.isFilterApplied(FilterTypes.USED_UP),
         CarouselFilterTypes.ONLY_PROGRESSION_DECALS: self.isFilterApplied(FilterTypes.PROGRESSION),
         CarouselFilterTypes.ONLY_EDITABLE_STYLES: self.isFilterApplied(FilterTypes.EDITABLE_STYLES, FilterAliases.EDITABLE_STYLES),
         CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES: self.isFilterApplied(FilterTypes.EDITABLE_STYLES, FilterAliases.NON_EDITABLE_STYLES),
         CarouselFilterTypes.ONLY_PROGRESSION_STYLES: self.isFilterApplied(FilterTypes.PROGRESSION_STYLE)}

    def __transformAvailabilityFilter(self, kwargs):
        state = kwargs.pop(CarouselFilterTypes.AVAILABILITY)
        kwargs[CarouselFilterTypes.INVENTORY] = state == AvailabilityFilterState.INVENTORY
        kwargs[CarouselFilterTypes.SALE] = state == AvailabilityFilterState.SALE

    def getAvailabilityFilter(self):
        inventoryState = self.isFilterApplied(FilterTypes.INVENTORY)
        salesState = self.isFilterApplied(FilterTypes.SALE)
        if inventoryState and not salesState:
            return AvailabilityFilterState.INVENTORY
        return AvailabilityFilterState.SALE if not inventoryState and salesState else AvailabilityFilterState.ALL

    def updateFilterCarousel(self, kwargs):
        if CarouselFilterTypes.GROUP in kwargs:
            self.updateSelectedGroup(kwargs[CarouselFilterTypes.GROUP])
        if CarouselFilterTypes.AVAILABILITY in kwargs:
            self.__transformAvailabilityFilter(kwargs)
        self.__setFilterSettings(kwargs)
        self.updateCarouselDPData()
        self.__ctx.events.onCarouselFiltered()

    def __setFilterSettings(self, kwargs):
        currentFilterTab = CustomizationTabs.TAB_TO_GROUP.get(self.__ctx.tabId)
        for key, value in kwargs.iteritems():
            if key == CarouselFilterTypes.GROUP:
                self.setSetting(currentFilterTab, value)
                continue
            if key == CarouselFilterTypes.DISPLAY_GROUP:
                if value < 0 or value >= len(self.getDisplayGroupsData()):
                    value = 0
            self.setSetting(key, value)

        self._dumpSettings()

    def __applyCurrentFilter(self):
        carouselFilterData = self.getFilterData()
        for key, value in carouselFilterData.iteritems():
            if key == CarouselFilterTypes.GROUP:
                self.updateSelectedGroup(value)
                continue
            currentFilterValue = self.getSetting(key, getCustomizationFilterDefaults()[key])
            if value != currentFilterValue:
                self.__applyCarouselFilter({key: currentFilterValue})

    def __applyCarouselFilter(self, kwargs):
        for key, value in kwargs.iteritems():
            filterType = FILTER_TYPES_MAPPING.get(key)
            filterAlias = FILTER_ALIAS_MAPPING.get(key)
            if FILTER_TYPES_MAPPING.get(key):
                if FILTER_ALIAS_MAPPING.get(key):
                    self.updateCarouselFilter(filterType, value, filterAlias)
                else:
                    self.updateCarouselFilter(filterType, value)

    def resetFilter(self):
        self.__selectedGroup.clear()
        for key, value in getCustomizationFilterDefaults().iteritems():
            if key == CustomizationFilter.DISPLAY_GROUP:
                continue
            self.setSetting(key, value)

        self._dumpSettings()
        self.updateCarouselDPData()
        self.__ctx.events.onCarouselFiltered()

    def updateCarouselDPData(self):
        self.__applyCurrentFilter()
        self.invalidateFilteredItems()
        self.buildList()
        self.refresh()

    def invalidateItems(self):
        self.__carouselCache.invalidateItemsData()
        self.invalidateFilteredItems()

    def invalidateFilteredItems(self):
        self.__carouselCache.invalidateCarouselData()

    def updateSelectedGroup(self, index):
        self.__setSelectedGroupIdx(index)

    def updateCarouselFilter(self, filterType, value, *alias):
        if filterType not in self.__carouselFilters:
            _logger.error('Invalid filterType: %s', filterType)
        self.__carouselFilters[filterType].update(value, *alias)

    def isFilterApplied(self, filterType, *alias):
        if filterType not in self.__carouselFilters:
            _logger.error('Invalid filterType: %s', filterType)
            return False
        return self.__carouselFilters[filterType].isApplied(*alias)

    def __initFilters(self):
        self.__carouselFilters[FilterTypes.HISTORIC] = DisjunctionCarouselFilter(criteria={FilterAliases.HISTORIC: REQ_CRITERIA.CUSTOMIZATION.HISTORICAL,
         FilterAliases.NON_HISTORIC: REQ_CRITERIA.CUSTOMIZATION.NON_HISTORICAL,
         FilterAliases.FANTASTICAL: REQ_CRITERIA.CUSTOMIZATION.FANTASTICAL})
        self.__carouselFilters[FilterTypes.INVENTORY] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: (True if self.__ctx.mode.getItemInventoryCount(item) > 0 or self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE and self.__ctx.tabId == CustomizationTabs.CAMOUFLAGES else item.isInInventory) and item.isUnlockedByToken()))
        self.__carouselFilters[FilterTypes.SALE] = SimpleCarouselFilter(criteria=RequestCriteria(PredicateCondition(lambda item: 'notInShop' not in item.priceGroupTags and not self.__ctx.mode.getItemInventoryCount(item))))
        self.__carouselFilters[FilterTypes.APPLIED] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.intCD in self.__ctx.mode.getAppliedItems(isOriginal=False)))
        self.__carouselFilters[FilterTypes.FAVORITE] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.markedAsFavorite))
        self.__carouselFilters[FilterTypes.USED_UP] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: not isItemUsedUp(item)), requirements=lambda : self.__ctx.isItemsOnAnotherVeh, inverse=True)
        self.__carouselFilters[FilterTypes.EDITABLE_STYLES] = DisjunctionCarouselFilter(criteria={FilterAliases.EDITABLE_STYLES: REQ_CRITERIA.CUSTOM(lambda item: item.canBeEditedForVehicle(g_currentVehicle.item.intCD)),
         FilterAliases.NON_EDITABLE_STYLES: REQ_CRITERIA.CUSTOM(lambda item: not item.canBeEditedForVehicle(g_currentVehicle.item.intCD))}, requirements=lambda : self.__ctx.tabId in CustomizationTabs.STYLES_ALL)
        self.__carouselFilters[FilterTypes.PROGRESSION] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.isProgressive), requirements=lambda : self.__ctx.isProgressiveItemsExist and self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS)
        self.__carouselFilters[FilterTypes.FORMFACTORS] = DisjunctionCarouselFilter(criteria={FilterAliases.FORMFACTOR_SQUARE: REQ_CRITERIA.CUSTOM(lambda item: item.formfactor == CarouselFilterTypes.FORMFACTOR_SQUARE),
         FilterAliases.FORMFACTOR_RECT1X2: REQ_CRITERIA.CUSTOM(lambda item: item.formfactor == CarouselFilterTypes.FORMFACTOR_RECT1X2),
         FilterAliases.FORMFACTOR_RECT1X3: REQ_CRITERIA.CUSTOM(lambda item: item.formfactor == CarouselFilterTypes.FORMFACTOR_RECT1X3),
         FilterAliases.FORMFACTOR_RECT1X4: REQ_CRITERIA.CUSTOM(lambda item: item.formfactor == CarouselFilterTypes.FORMFACTOR_RECT1X4),
         FilterAliases.FORMFACTOR_RECT1X6: REQ_CRITERIA.CUSTOM(lambda item: item.formfactor == CarouselFilterTypes.FORMFACTOR_RECT1X6)}, requirements=lambda : self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS)
        self.__carouselFilters[FilterTypes.PROGRESSION_STYLE] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.isQuestsProgression or item.isProgressive), requirements=lambda : self.__ctx.tabId in CustomizationTabs.STYLES_ALL)

    def __getSelectedGroupIdx(self):
        tabId = self.__ctx.tabId
        selectedGroup = self.__selectedGroup.get(tabId)
        return selectedGroup

    def __setSelectedGroupIdx(self, index=None):
        tabId = self.__ctx.tabId
        itemsData = self.__carouselCache.getItemsData()
        if index is not None and (index >= len(itemsData.groups) or index < 0):
            index = None
        self.__selectedGroup[tabId] = index
        return

    def __createFilterCriteria(self):
        requirement = REQ_CRITERIA.EMPTY
        groupIdx = self.__getSelectedGroupIdx()
        if groupIdx is not None and groupIdx != -1:
            itemsData = self.__carouselCache.getItemsData()
            groupId = itemsData.groups.keys()[groupIdx]
            groupName = itemsData.groups[groupId]
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: getGroupHelper(item).getGroupName() == groupName)
        for carouselFilter in self.__carouselFilters.itervalues():
            if carouselFilter.isEnabled():
                requirement |= carouselFilter.criteria

        slotId = self.__ctx.mode.selectedSlot
        if slotId is not None and slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            slot = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: item.formfactor in slot.formfactors)
        if self.__dependentItems:
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: not (ItemTags.HIDE_IF_INCOMPATIBLE in item.tags and item.intCD not in self.__dependentItems))
        if self.__ctx.mode.modeId == CustomizationModes.CUSTOM:
            requirement |= REQ_CRITERIA.CUSTOM(lambda item: not item.isStyleOnly)
        if self.__ctx.mode.modeId == CustomizationModes.EDITABLE_STYLE and self.__ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
            baseOutfit = self.__ctx.mode.baseOutfits.get(self.__ctx.mode.season)
            if baseOutfit:
                baseComponent = baseOutfit.pack()
                taggedDecals = [ decal.id for decal in baseComponent.projection_decals if decal.matchingTag ]
                requirement |= REQ_CRITERIA.CUSTOM(lambda item: item.id not in taggedDecals)
        return requirement

    def __createSortCriteria(self):
        return (lambda item: self.processDependentParams(item)[1]) if self.__dependentItems else None

    def __updateCarouselData(self):
        itemsData = self.__carouselCache.getItemsData()
        self.__ctx.setIsItemsOnAnotherVeh(itemsData.hasUsedUpItems)
        self.__ctx.setIsProgressiveItemsExist(itemsData.hasProgressiveItems)
        self.__carouselData = self.__carouselCache.getCarouselData()
        self.__ctx.setCarouselItems(self.__carouselData.items)

    def __updateSwitchers(self):
        left = self.getNextItem(reverse=True) is not None
        right = self.getNextItem(reverse=False) is not None
        self.__ctx.events.onUpdateSwitchers(left, right)
        return

    def __updateSelection(self, intCD):
        idx = self.collection.index(intCD) if intCD in self.collection else -1
        self.__selectedItem = SelectedItem(intCD, idx)
        self.__updateSwitchers()


class SimpleCarouselFilter(object):

    def __init__(self, criteria, requirements=None, inverse=False):
        self.__applied = False
        self.__criteria = criteria
        self.__inverse = inverse
        self.__requirements = requirements

    @property
    def isAvailable(self):
        return self.__requirements is None or self.__requirements()

    @property
    def isInverse(self):
        return self.__inverse

    @property
    def criteria(self):
        return self.__criteria

    def isApplied(self):
        return self.isAvailable and self.__applied

    def isEnabled(self):
        return self.isApplied() ^ self.isInverse

    def update(self, value):
        self.__applied = value

    def clear(self):
        self.__applied = False


class DisjunctionCarouselFilter(object):

    def __init__(self, criteria, requirements=None):
        self.__applied = set()
        self.__criteria = criteria
        self.__requirements = requirements

    @property
    def isAvailable(self):
        return self.__requirements is None or self.__requirements()

    @property
    def criteria(self):
        return reduce(RequestCriteria.__xor__, (self.__criteria[alias] for alias in self.__applied), REQ_CRITERIA.NONE)

    def isApplied(self, alias=None):
        if not self.isAvailable:
            return False
        else:
            return alias in self.__applied if alias is not None else bool(self.__applied)

    def isEnabled(self, alias=None):
        return self.isApplied(alias)

    def update(self, value, alias):
        if value:
            self.__applied.add(alias)
        else:
            self.__applied.discard(alias)

    def clear(self):
        self.__applied.clear()
