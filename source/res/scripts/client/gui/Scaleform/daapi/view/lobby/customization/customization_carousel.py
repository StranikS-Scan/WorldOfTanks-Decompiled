# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/customization_carousel.py
import logging
from collections import defaultdict, namedtuple, OrderedDict
import typing
from CurrentVehicle import g_currentVehicle
from cache import cached_property
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, TYPES_ORDER, isItemLimitReached, isItemUsedUp, vehicleHasSlot, ITEM_TYPE_TO_TAB
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.customization.constants import CustomizationModes
from gui.customization.shared import getBaseStyleItems, createCustomizationBaseRequestCriteria, C11N_ITEM_TYPE_MAP, getInheritors, getAncestors
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers import dependency
from items.components.c11n_constants import SeasonType, ProjectionDecalFormTags, ItemTags, EMPTY_ITEM_ID
from items import vehicles
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.customization.c11n_items import Customization
_logger = logging.getLogger(__name__)

def comparisonKey(item):
    typeOrder = TYPES_ORDER.index(item.itemTypeID)
    isNationalEmblem = ItemTags.NATIONAL_EMBLEM in item.tags
    formfactorId = 0 if not hasattr(item, 'formfactor') else ProjectionDecalFormTags.ALL.index(item.formfactor)
    return (typeOrder,
     not isNationalEmblem,
     not item.isRare(),
     item.groupID,
     formfactorId,
     item.id)


CustomizationBookmarkVO = namedtuple('CustomizationBookmarkVO', ('bookmarkName', 'bookmarkIndex'))
SelectedItem = namedtuple('SelectedItem', ('intCD', 'idx'))
SelectedItem.__new__.__defaults__ = (-1, -1)

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


class CarouselData(object):
    __slots__ = ('items', 'sizes', 'bookmarks')

    def __init__(self):
        self.items = []
        self.sizes = []
        self.bookmarks = []


class CarouselCache(object):
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
        self.__createFilterCriteria = None
        self.__createSortCriteria = None
        self.__cachedEditableStyleId = 0
        self.__ctx = None
        return

    def getVisibleTabs(self):
        season, modeId = self.__ctx.season, self.__ctx.modeId
        self.__invalidateEditableStyleCache()
        self.__initCache()
        visibleTabs = self.__itemsData[modeId][season].keys()
        return visibleTabs

    def getItemsData(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.mode.tabId
        self.__invalidateEditableStyleCache()
        self.__initCache()
        itemsData = self.__itemsData[modeId][season].get(tabId, ItemsData())
        return itemsData

    def getCarouselData(self, season=None, modeId=None, tabId=None):
        season = season or self.__ctx.season
        modeId = modeId or self.__ctx.modeId
        tabId = tabId or self.__ctx.mode.tabId
        self.__invalidateEditableStyleCache()
        carouselData = self.__carouselData.get(modeId, {}).get(season, {}).get(tabId)
        if carouselData is None:
            carouselData = self.__getCarouselData(season, modeId, tabId)
            self.__carouselData.setdefault(modeId, {}).setdefault(season, {})[tabId] = carouselData
        return carouselData

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

    def __getCarouselData(self, season=None, modeId=None, tabId=None):
        itemsData = self.getItemsData(season, modeId, tabId)
        filteredItems = filter(self.__createFilterCriteria(), itemsData.items)
        sortCriteria = self.__createSortCriteria()
        showBookmarks = True
        if sortCriteria:
            filteredItems.sort(key=sortCriteria)
            showBookmarks = False
        carouselData = CarouselData()
        lastGroupID = None
        for item in filteredItems:
            if showBookmarks and item.groupID != lastGroupID:
                lastGroupID = item.groupID
                bookmarkVO = CustomizationBookmarkVO(item.groupUserName, len(carouselData.items))
                carouselData.bookmarks.append(bookmarkVO._asdict())
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

        sortedItems = sorted(allItems, key=comparisonKey)
        customModeTabs = CustomizationTabs.MODES[CustomizationModes.CUSTOM]
        for item in sortedItems:
            tabId = ITEM_TYPE_TO_TAB[item.itemTypeID]
            modeId = CustomizationModes.CUSTOM if tabId in customModeTabs else CustomizationModes.STYLED
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
                filteredItems = [ item for item in itemsData.items if itemsFilter(item.descriptor) ]
                alternateItems = []
                for itemType in itemTypes:
                    c11nType = C11N_ITEM_TYPE_MAP[itemType]
                    alternateItemIds = style.descriptor.alternateItems.get(c11nType, ())
                    buf = [ self.__service.getItemByID(itemType, itemId) for itemId in alternateItemIds ]
                    alternateItems.extend([ i for i in buf if i.itemTypeID in itemTypes ])

                allItems = [ item for item in filteredItems + alternateItems if item.season & season ]
                if not allItems:
                    continue
                baseItems = [ item for item in styleBaseItems if item.itemTypeID in itemTypes and item.season & season ]
                allItems += baseItems
                items = sorted(set(allItems), key=comparisonKey)
                groups = OrderedDict()
                for item in items:
                    if not groups or item.groupID != groups.keys()[-1]:
                        groups[item.groupID] = item.groupUserName

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


class CustomizationCarouselDataProvider(SortableDAAPIDataProvider):
    __service = dependency.descriptor(ICustomizationService)

    def __init__(self, carouselItemWrapper):
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
        self.setItemWrapper(carouselItemWrapper)
        self.__initFilters()

    @property
    def collection(self):
        return self.__carouselData.items

    @property
    def itemCount(self):
        return len(self.__carouselData.items)

    @property
    def totalItemCount(self):
        itemsData = self.__carouselCache.getItemsData()
        return len(itemsData.items)

    def pyGetSelectedIdx(self):
        return self.__selectedItem.idx

    def emptyItem(self):
        return None

    def refresh(self):
        if not g_currentVehicle.isPresent():
            return
        super(CustomizationCarouselDataProvider, self).refresh()
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
        return self.__carouselCache.getItemsData(season, modeId, tabId).items

    def getCarouselData(self, season=None, modeId=None, tabId=None):
        return self.__carouselCache.getCarouselData(season, modeId, tabId).items

    def getAppliedItems(self):
        return self.__appliedItems

    def getBaseStyleItems(self):
        return self.__baseStyleItems

    def getItemSizeData(self):
        return self.__carouselData.sizes

    def getBookmarskData(self):
        return self.__carouselData.bookmarks

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

    def onModeChanged(self, modeId, prevModeId):
        visibleTabs = self.getVisibleTabs()
        tabId = visibleTabs[0]
        if CustomizationModes.EDITABLE_STYLE in (modeId, prevModeId):
            self.clearFilter()
            self.__selectedGroup.clear()
            self.invalidateFilteredItems()
            if self.__ctx.mode.getDependenciesData():
                if CustomizationTabs.CAMOUFLAGES in visibleTabs:
                    tabId = CustomizationTabs.CAMOUFLAGES
                else:
                    _logger.warning('Style with dependencies have to open Camouflages tab, but this tab is not found!')
        if visibleTabs:
            self.__ctx.mode.changeTab(tabId)

    def hasAppliedFilter(self):
        isGroupSelected = self.__getSelectedGroupIdx() is not None
        isAnyFilterApplied = any((carouselFilter.isApplied() for carouselFilter in self.__carouselFilters.itervalues()))
        return isAnyFilterApplied or isGroupSelected

    def selectItem(self, item=None):
        prevSelectedItem = self.__selectedItem
        intCD = item.intCD if item is not None else -1
        self.__updateSelection(intCD)
        if prevSelectedItem != self.__selectedItem:
            self.refresh()
        return

    def getNextItem(self, reverse):
        if self.__selectedItem.idx == -1:
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

    def getFilterData(self):
        itemsData = self.__carouselCache.getItemsData()
        groups = itemsData.groups.values()
        if len(groups) > 1:
            groups.append(backport.text(R.strings.vehicle_customization.customization.filter.allGroups()))
            groupCount = len(groups)
            selectedGroup = self.__getSelectedGroupIdx()
            if selectedGroup is None:
                selectedGroup = groupCount - 1
        else:
            groups = []
            groupCount = 0
            selectedGroup = 0
        formfactors = []
        if self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
            formfactorsFilter = self.__carouselFilters[FilterTypes.FORMFACTORS]
            formfactors = [ formfactor in formfactorsFilter.formfactors for formfactor in ProjectionDecalFormTags.ALL ]
        return {'purchasedEnabled': self.isFilterApplied(FilterTypes.INVENTORY),
         'historicEnabled': self.isFilterApplied(FilterTypes.HISTORIC, FilterAliases.HISTORIC),
         'nonHistoricEnabled': self.isFilterApplied(FilterTypes.HISTORIC, FilterAliases.NON_HISTORIC),
         'appliedEnabled': self.isFilterApplied(FilterTypes.APPLIED),
         'groups': groups,
         'selectedGroup': selectedGroup,
         'groupCount': groupCount,
         'formfactorGroups': formfactors,
         'hideOnAnotherVehEnabled': self.isFilterApplied(FilterTypes.USED_UP),
         'showOnlyProgressionDecalsEnabled': self.isFilterApplied(FilterTypes.PROGRESSION),
         'showOnlyEditableStylesEnabled': self.isFilterApplied(FilterTypes.EDITABLE_STYLES, FilterAliases.EDITABLE_STYLES),
         'showOnlyNonEditableStylesEnabled': self.isFilterApplied(FilterTypes.EDITABLE_STYLES, FilterAliases.NON_EDITABLE_STYLES)}

    def clearFilter(self):
        for carouselFilter in self.__carouselFilters.itervalues():
            carouselFilter.clear()

        self.__setSelectedGroupIdx(None)
        return

    def invalidateItems(self):
        self.__carouselCache.invalidateItemsData()
        self.invalidateFilteredItems()

    def invalidateFilteredItems(self):
        self.__carouselCache.invalidateCarouselData()
        self.selectItem()

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

    def _dispose(self):
        self.__carouselCache.fini()
        self.__carouselCache = None
        self.__ctx = None
        super(CustomizationCarouselDataProvider, self)._dispose()
        return

    def __initFilters(self):
        self.__carouselFilters[FilterTypes.HISTORIC] = DisjunctionCarouselFilter(criteria={FilterAliases.HISTORIC: REQ_CRITERIA.CUSTOMIZATION.HISTORICAL,
         FilterAliases.NON_HISTORIC: ~REQ_CRITERIA.CUSTOMIZATION.HISTORICAL})
        self.__carouselFilters[FilterTypes.INVENTORY] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: self.__ctx.mode.getItemInventoryCount(item) > 0))
        self.__carouselFilters[FilterTypes.APPLIED] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.intCD in self.__ctx.mode.getAppliedItems(isOriginal=False)))
        self.__carouselFilters[FilterTypes.USED_UP] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: not isItemUsedUp(item)), requirements=lambda : self.__ctx.isItemsOnAnotherVeh, inverse=True)
        self.__carouselFilters[FilterTypes.EDITABLE_STYLES] = DisjunctionCarouselFilter(criteria={FilterAliases.EDITABLE_STYLES: REQ_CRITERIA.CUSTOM(lambda item: item.canBeEditedForVehicle(g_currentVehicle.item.intCD)),
         FilterAliases.NON_EDITABLE_STYLES: REQ_CRITERIA.CUSTOM(lambda item: not item.canBeEditedForVehicle(g_currentVehicle.item.intCD))}, requirements=lambda : self.__ctx.mode.tabId == CustomizationTabs.STYLES)
        self.__carouselFilters[FilterTypes.PROGRESSION] = SimpleCarouselFilter(criteria=REQ_CRITERIA.CUSTOM(lambda item: item.isProgressive), requirements=lambda : self.__ctx.isProgressiveItemsExist)
        self.__carouselFilters[FilterTypes.FORMFACTORS] = FormfactorsCarouselFilter(requirements=lambda : self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS)

    def __getSelectedGroupIdx(self):
        season, modeId, tabId = self.__ctx.season, self.__ctx.modeId, self.__ctx.mode.tabId
        selectedGroup = self.__selectedGroup.get(modeId, {}).get(season, {}).get(tabId)
        return selectedGroup

    def __setSelectedGroupIdx(self, index=None):
        season, modeId, tabId = self.__ctx.season, self.__ctx.modeId, self.__ctx.mode.tabId
        itemsData = self.__carouselCache.getItemsData()
        if index is not None and index >= len(itemsData.groups):
            index = None
        self.__selectedGroup.setdefault(modeId, {}).setdefault(season, {})[tabId] = index
        return

    def __createFilterCriteria(self):
        requirement = REQ_CRITERIA.EMPTY
        groupIdx = self.__getSelectedGroupIdx()
        if groupIdx is not None and groupIdx != -1:
            itemsData = self.__carouselCache.getItemsData()
            groupId = itemsData.groups.keys()[groupIdx]
            groupName = itemsData.groups[groupId]
            requirement |= REQ_CRITERIA.CUSTOMIZATION.ONLY_IN_GROUP(groupName)
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


class FilterTypes(object):
    HISTORIC = 1
    INVENTORY = 2
    APPLIED = 3
    USED_UP = 4
    EDITABLE_STYLES = 5
    PROGRESSION = 6
    FORMFACTORS = 7


class FilterAliases(object):
    HISTORIC = 'historic'
    NON_HISTORIC = 'nonHistoric'
    EDITABLE_STYLES = 'editableStyles'
    NON_EDITABLE_STYLES = 'nonEditableStyles'


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


class FormfactorsCarouselFilter(SimpleCarouselFilter):

    def __init__(self, requirements=None):
        self.__formfactors = set()
        criteria = REQ_CRITERIA.CUSTOM(lambda item: item.formfactor in self.formfactors)
        super(FormfactorsCarouselFilter, self).__init__(criteria, requirements)

    @property
    def formfactors(self):
        return self.__formfactors

    def update(self, value):
        self.__formfactors = set((formfactor for formfactor, isApplied in value.iteritems() if isApplied))
        super(FormfactorsCarouselFilter, self).update(bool(self.__formfactors))

    def clear(self):
        self.__formfactors = set()
        super(FormfactorsCarouselFilter, self).clear()
