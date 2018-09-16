# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/context.py
from collections import defaultdict
from functools import partial
from collections import namedtuple
import Event
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.decorators import process
from gui import g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.view.lobby.customization.customization_carousel import comparisonKey
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, C11nTabs, TABS_ITEM_MAPPING, TYPE_TO_TAB_IDX, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_IDX, getStylePurchaseItems, getStyleInventoryCount, getItemInventoryCount, SEASONS_ORDER, OutfitInfo, getCustomPurchaseItems, AdditionalPurchaseGroups, getOutfitWithoutItems
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsSeller
from gui.shared.gui_items.customization.outfit import Area
from items.components.c11n_constants import SeasonType
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from gui.customization.shared import createCustomizationBaseRequestCriteria
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle
from shared_utils import first
CustomizationRegion = namedtuple('CustomizationRegion', ('slotType', 'areaId', 'regionIdx'))
CustomizationRegion = partial(CustomizationRegion, slotType=-1, areaId=-1, regionIdx=-1)
CaruselItemData = namedtuple('CaruselItemData', ('index', 'intCD'))
CaruselItemData = partial(CaruselItemData, index=-1, intCD=-1)

class CustomizationContext(object):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    eventsCache = dependency.descriptor(IEventsCache)

    @property
    def visibleTabs(self):
        return self.__visibleTabs[self._currentSeason]

    @property
    def currentTab(self):
        return self._tabIndex

    @property
    def currentSeason(self):
        return self._currentSeason

    @property
    def currentOutfit(self):
        return self._currentOutfit

    @property
    def originalOutfit(self):
        return self._originalOutfits[self._currentSeason]

    @property
    def originalMode(self):
        return self._originalMode

    @property
    def mode(self):
        return self._mode

    @property
    def originalStyle(self):
        return self._originalStyle

    @property
    def modifiedStyle(self):
        return self._modifiedStyle

    @property
    def selectedRegion(self):
        return self._selectedRegion

    @property
    def selectedCaruselItem(self):
        return self._selectedCaruselItem

    def __init__(self):
        self._currentSeason = SeasonType.SUMMER
        self.__visibleTabs = defaultdict(set)
        self._tabIndex = C11nTabs.PAINT
        self._lastTab = C11nTabs.PAINT
        self._originalStyle = None
        self._modifiedStyle = None
        self._originalOutfits = {}
        self._modifiedOutfits = {}
        self._currentOutfit = None
        self._originalMode = C11nMode.CUSTOM
        self._mode = self._originalMode
        self._state = {}
        self._selectedCaruselItem = CaruselItemData()
        self._selectedRegion = CustomizationRegion()
        self._eventsManager = Event.EventManager()
        self.onCustomizationSeasonChanged = Event.Event(self._eventsManager)
        self.onCustomizationModeChanged = Event.Event(self._eventsManager)
        self.onCustomizationTabChanged = Event.Event(self._eventsManager)
        self.onCustomizationItemInstalled = Event.Event(self._eventsManager)
        self.onCustomizationItemsRemoved = Event.Event(self._eventsManager)
        self.onCustomizationCamouflageColorChanged = Event.Event(self._eventsManager)
        self.onCustomizationCamouflageScaleChanged = Event.Event(self._eventsManager)
        self.onCustomizationItemsBought = Event.Event(self._eventsManager)
        self.onCustomizationItemSold = Event.Event(self._eventsManager)
        self.onCacheResync = Event.Event(self._eventsManager)
        self.onChangesCanceled = Event.Event(self._eventsManager)
        self.onCaruselItemSelected = Event.Event(self._eventsManager)
        self.onCaruselItemUnselected = Event.Event(self._eventsManager)
        self.onCarouselFilter = Event.Event(self._eventsManager)
        self.onCustomizationRegionSelected = Event.Event(self._eventsManager)
        self.onPropertySheetShown = Event.Event(self._eventsManager)
        self.onPropertySheetHidden = Event.Event(self._eventsManager)
        return

    def changeSeason(self, seasonIdx):
        self._currentSeason = SEASON_IDX_TO_TYPE[seasonIdx]
        self.refreshOutfit()
        self.onCustomizationSeasonChanged(self._currentSeason)

    def refreshOutfit(self):
        if self._mode == C11nMode.STYLE:
            if self._modifiedStyle:
                self._currentOutfit = self._modifiedStyle.getOutfit(self._currentSeason)
            else:
                self._currentOutfit = self.service.getEmptyOutfit()
        else:
            self._currentOutfit = self._modifiedOutfits[self._currentSeason]
        self.service.tryOnOutfit(self._currentOutfit)
        g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self._currentSeason

    def tabChanged(self, tabIndex):
        self._tabIndex = tabIndex
        if self._tabIndex == C11nTabs.EFFECT:
            self._selectedRegion = CustomizationRegion(slotType=GUI_ITEM_TYPE.MODIFICATION, areaId=Area.MISC, regionIdx=0)
        elif self._tabIndex == C11nTabs.STYLE:
            self._selectedRegion = CustomizationRegion(slotType=GUI_ITEM_TYPE.STYLE, areaId=Area.CHASSIS, regionIdx=0)
        else:
            self._selectedRegion = CustomizationRegion()
        self._selectedCaruselItem = CaruselItemData()
        self.onCustomizationTabChanged(tabIndex)

    def regionSelected(self, slotType, areaId, regionIdx):
        if self._tabIndex in (C11nTabs.EFFECT, C11nTabs.STYLE):
            return
        self._selectedRegion = CustomizationRegion(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
        self.onCustomizationRegionSelected(self._selectedRegion.slotType, self._selectedRegion.areaId, self._selectedRegion.regionIdx)
        if areaId != -1 and regionIdx != -1 and self._selectedCaruselItem.intCD != -1:
            self.installItem(self._selectedCaruselItem.intCD, areaId, slotType, regionIdx, SEASON_TYPE_TO_IDX[self.currentSeason])

    def installItem(self, intCD, areaId, slotType, regionId, seasonIdx, component=None):
        item = self.service.getItemByCD(intCD)
        if item.isHidden and not self.getItemInventoryCount(item):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
            return False
        if slotType == GUI_ITEM_TYPE.STYLE:
            self._modifiedStyle = item
        else:
            season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
            outfit = self._modifiedOutfits[season]
            outfit.getContainer(areaId).slotFor(slotType).set(item, idx=regionId, component=component)
            outfit.invalidate()
        self.refreshOutfit()
        self.onCustomizationItemInstalled()
        return True

    def installItemToAllTankAreas(self, season, slotType, currentSlotData):
        currentSeasonIdx = SEASON_TYPE_TO_IDX[season]
        additionalyApplyedItems = 0
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            multiSlot = self.currentOutfit.getContainer(areaId).slotFor(slotType)
            for regionIdx in regionsIndexes:
                slotData = multiSlot.getSlotData(regionIdx)
                df = currentSlotData.weakDiff(slotData)
                if slotData.item is None or df.item is not None:
                    self.installItem(currentSlotData.item.intCD, areaId, slotType, regionIdx, currentSeasonIdx, currentSlotData.component)
                    additionalyApplyedItems += 1

        return additionalyApplyedItems

    def installItemForAllSeasons(self, areaID, slotType, regionIdx, currentSlotData):
        additionalyApplyedItems = 0
        for season in SeasonType.COMMON_SEASONS:
            slotData = self.getModifiedOutfit(season).getContainer(areaID).slotFor(slotType).getSlotData(regionIdx)
            df = currentSlotData.weakDiff(slotData)
            if slotData.item is None or df.item is not None:
                seasonIdx = SEASON_TYPE_TO_IDX[season]
                self.installItem(currentSlotData.item.intCD, areaID, slotType, regionIdx, seasonIdx)
                additionalyApplyedItems += 1

        return additionalyApplyedItems

    def removeItemFromRegion(self, season, areaId, slotType, regionId):
        outfit = self._modifiedOutfits[season]
        slot = outfit.getContainer(areaId).slotFor(slotType)
        if slot.capacity() > regionId:
            slot.remove(idx=regionId)
        self.refreshOutfit()
        self.onCustomizationItemsRemoved()

    def removeItemFromAllTankAreas(self, season, slotType):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            for regionIdx in regionsIndexes:
                self.removeItemFromRegion(season, areaId, slotType, regionIdx)

    def removeItemForAllSeasons(self, areaID, slotType, regionIdx):
        for season in SeasonType.COMMON_SEASONS:
            self.removeItemFromRegion(season, areaID, slotType, regionIdx)

    def removeStyle(self, intCD):
        if self._modifiedStyle and self._modifiedStyle.intCD == intCD:
            self._modifiedStyle = None
        self.refreshOutfit()
        self.onCustomizationItemsRemoved()
        return

    def removeItems(self, onlyCurrent, *intCDs):

        def intCdFilter(item):
            return item.intCD in intCDs

        if onlyCurrent:
            self.removeItemsFromOutfit(self._currentOutfit, intCdFilter, False)
        else:
            for outfit in self._modifiedOutfits.itervalues():
                self.removeItemsFromOutfit(outfit, intCdFilter, False)

        self.refreshOutfit()
        self.onCustomizationItemsRemoved()

    def removeItemsFromOutfit(self, outfit, filterMethod=None, refresh=True):
        for slot in outfit.slots():
            for idx in range(slot.capacity()):
                item = slot.getItem(idx)
                if item and (not filterMethod or filterMethod(item)):
                    slot.remove(idx)

        if refresh:
            self.refreshOutfit()
            self.onCustomizationItemsRemoved()

    def switchToCustom(self):
        if self._mode != C11nMode.CUSTOM:
            self._mode = C11nMode.CUSTOM
            self._tabIndex = self._lastTab
        self.refreshOutfit()
        self.onCustomizationModeChanged(self._mode)

    def switchToStyle(self):
        if self._mode != C11nMode.STYLE:
            self._mode = C11nMode.STYLE
            self._lastTab = self._tabIndex
            self._tabIndex = C11nTabs.STYLE
        self.refreshOutfit()
        self.onCustomizationModeChanged(self._mode)

    def cancelChanges(self):
        if self._mode == C11nMode.STYLE:
            self.__cancelModifiedStyle()
        else:
            self.__cancelModifiedOufits()
        self.refreshOutfit()
        self.onChangesCanceled()

    def caruselItemSelected(self, index, intCD):
        self._selectedCaruselItem = CaruselItemData(index=index, intCD=intCD)
        if self.isRegionSelected() and self._selectedCaruselItem.intCD != -1:
            self.installItem(self._selectedCaruselItem.intCD, self._selectedRegion.areaId, self._selectedRegion.slotType, self._selectedRegion.regionIdx, SEASON_TYPE_TO_IDX[self.currentSeason])
        self.onCaruselItemSelected(index, intCD)

    def caruselItemUnselected(self):
        if self._selectedCaruselItem.index != -1:
            prevSelectCaruselItem = self._selectedCaruselItem
            self._selectedCaruselItem = CaruselItemData()
            self.onCaruselItemUnselected(prevSelectCaruselItem.index, prevSelectCaruselItem.intCD)

    def applyCarouselFilter(self, **kwargs):
        self.onCarouselFilter(**kwargs)

    def changeCamouflageColor(self, areaId, regionIdx, paletteIdx):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.palette != paletteIdx:
            component.palette = paletteIdx
            self.refreshOutfit()
            self.onCustomizationCamouflageColorChanged(areaId, regionIdx, paletteIdx)

    def changeCamouflageScale(self, areaId, regionIdx, scale):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.patternSize != scale:
            component.patternSize = scale
            self.refreshOutfit()
            self.onCustomizationCamouflageScaleChanged(areaId, regionIdx, scale)

    def getOutfitsInfo(self):
        outfitsInfo = {}
        for season in SEASONS_ORDER:
            outfitsInfo[season] = OutfitInfo(self._originalOutfits[season], self._modifiedOutfits[season])

        return outfitsInfo

    def getStyleInfo(self):
        return OutfitInfo(self._originalStyle, self._modifiedStyle)

    def getPurchaseItems(self):
        return getCustomPurchaseItems(self.getOutfitsInfo()) if self._mode == C11nMode.CUSTOM else getStylePurchaseItems(self.getStyleInfo())

    def getItemInventoryCount(self, item):
        return getItemInventoryCount(item, self.getOutfitsInfo()) if self._mode == C11nMode.CUSTOM else getStyleInventoryCount(item, self.getStyleInfo())

    def getModifiedOutfit(self, season):
        return self._modifiedOutfits.get(season)

    def getAppliedItems(self, isOriginal=True):
        outfits = self._originalOutfits if isOriginal else self._modifiedOutfits
        style = self._originalStyle if isOriginal else self._modifiedStyle
        seasons = SeasonType.COMMON_SEASONS if isOriginal else (self._currentSeason,)
        appliedItems = set()
        for seasonType in seasons:
            outfit = outfits[seasonType]
            appliedItems.update((i.intCD for i in outfit.items()))

        if style:
            appliedItems.add(style.intCD)
        return appliedItems

    def isItemInOutfit(self, item):
        return any((outfit.has(item) for outfit in self._originalOutfits.itervalues())) or any((outfit.has(item) for outfit in self._modifiedOutfits.itervalues()))

    def getNotModifiedItems(self, season):
        df = self._modifiedOutfits[season].diff(self._originalOutfits[season])
        notModifiedItems = df.diff(self._originalOutfits[self.currentSeason])
        return notModifiedItems

    @process('buyAndInstall')
    def applyItems(self, purchaseItems):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        groupHasItems = {AdditionalPurchaseGroups.STYLES_GROUP_ID: False,
         SeasonType.WINTER: False,
         SeasonType.SUMMER: False,
         SeasonType.DESERT: False}
        modifiedOutfits = {season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()}
        for pItem in purchaseItems:
            if not pItem.selected:
                if pItem.slot:
                    slot = modifiedOutfits[pItem.group].getContainer(pItem.areaID).slotFor(pItem.slot)
                    slot.remove(pItem.regionID)
            groupHasItems[pItem.group] = True

        if self._mode == C11nMode.CUSTOM:
            groupHasItems[self._currentSeason] = True
        empty = self.service.getEmptyOutfit()
        for season in SeasonType.COMMON_SEASONS:
            if groupHasItems[season]:
                yield OutfitApplier(g_currentVehicle.item, empty, season).request()

        results = []
        for season in SeasonType.COMMON_SEASONS:
            if groupHasItems[season]:
                outfit = modifiedOutfits[season]
                result = yield OutfitApplier(g_currentVehicle.item, outfit, season).request()
                results.append(result)

        if groupHasItems[AdditionalPurchaseGroups.STYLES_GROUP_ID]:
            result = yield StyleApplier(g_currentVehicle.item, self._modifiedStyle).request()
            results.append(result)
        self.onCustomizationItemsBought(purchaseItems, results)
        self.__onCacheResync()
        self.itemsCache.onSyncCompleted += self.__onCacheResync

    @process('sellItem')
    def sellItem(self, intCD, count):
        if not count:
            return
        item = self.service.getItemByCD(intCD)
        if item.fullInventoryCount(g_currentVehicle.item) < count:
            if self._mode == C11nMode.CUSTOM:
                for season, outfit in getOutfitWithoutItems(self.getOutfitsInfo(), intCD, count):
                    yield OutfitApplier(g_currentVehicle.item, outfit, season).request()

            else:
                yield StyleApplier(g_currentVehicle.item).request()
        yield CustomizationsSeller(g_currentVehicle.item, item, count).request()
        nextTick(self.refreshOutfit)()
        nextTick(partial(self.onCustomizationItemSold, item=item, count=count))()

    def init(self):
        self.service.onOutfitChanged += self.__onOutfitChanged
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.carveUpOutfits()
        self.__updateVisibleTabsList()
        if self._originalStyle:
            self._mode = C11nMode.STYLE
        else:
            self._mode = C11nMode.CUSTOM
            if not self._originalOutfits[self._currentSeason].isInstalled() and not self.isOutfitsEmpty(self._modifiedOutfits) and not self._modifiedStyle:
                self._mode = C11nMode.STYLE
        self._originalMode = self._mode
        if self._mode == C11nMode.STYLE:
            self._tabIndex = C11nTabs.STYLE
            self._lastTab = first(self.visibleTabs, -1)
        else:
            self._tabIndex = first(self.visibleTabs, -1)
            self._lastTab = self._tabIndex
        self.refreshOutfit()

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.service.onOutfitChanged -= self.__onOutfitChanged
        self._eventsManager.clear()

    def checkSlotsFillingForSeason(self, season):
        checkedSlotTypes = (TABS_ITEM_MAPPING[tabId] for tabId in self.visibleTabs)
        return all((self.checkSlotsFilling(slotType, season) for slotType in checkedSlotTypes))

    def checkSlotsFilling(self, slotType, season):
        allSlotsFilled = True
        for areaId in Area.ALL:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            for regionIdx in regionsIndexes:
                item = self.getModifiedOutfit(season).getContainer(areaId).slotFor(slotType).getItem(regionIdx)
                if item is None:
                    break
            else:
                continue

            allSlotsFilled = False
            break

        return allSlotsFilled

    def carveUpOutfits(self, preserve=False):
        if preserve:
            self.__preserveState()
            self.__carveUpOutfits()
            self.__restoreState()
        else:
            self.__carveUpOutfits()

    def isOutfitsModified(self):
        if self._mode == self._originalMode:
            if self._mode == C11nMode.STYLE:
                currentStyle = self.service.getCurrentStyle()
                if self._modifiedStyle and currentStyle:
                    return self._modifiedStyle.intCD != currentStyle.intCD
                return not (self._modifiedStyle is None and currentStyle is None)
            for season in SeasonType.COMMON_SEASONS:
                outfit = self._modifiedOutfits[season]
                currOutfit = self._originalOutfits[season]
                if not currOutfit.isEqual(outfit) or not outfit.isEqual(currOutfit):
                    return True

            return False
        else:
            if self._mode == C11nMode.CUSTOM:
                if self.isOutfitsEmpty(self._modifiedOutfits) and self._originalStyle is None:
                    return False
            elif self._modifiedStyle is None and self.isOutfitsEmpty(self._originalOutfits):
                return False
            return True
            return

    @staticmethod
    def isOutfitsEmpty(outfits):
        outfitsEmpty = True
        for season in SeasonType.COMMON_SEASONS:
            outfit = outfits[season]
            if not outfit.isEmpty():
                outfitsEmpty = False
                break

        return outfitsEmpty

    def isRegionSelected(self):
        return self._selectedRegion.areaId != -1 and self._selectedRegion.regionIdx != -1

    def __carveUpOutfits(self):
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.service.getCustomOutfit(season)
            self._modifiedOutfits[season] = outfit.copy()
            if outfit.isInstalled():
                self._originalOutfits[season] = outfit.copy()
            self._originalOutfits[season] = self.service.getEmptyOutfit()
            for slot in self._modifiedOutfits[season].slots():
                for idx in range(slot.capacity()):
                    item = slot.getItem(idx)
                    if item and item.isHidden and item.fullInventoryCount(g_currentVehicle.item) == 0:
                        slot.remove(idx)

        style = self.service.getCurrentStyle()
        if self.service.isCurrentStyleInstalled():
            self._originalStyle = style
            self._modifiedStyle = style
        else:
            self._originalStyle = None
            if style and style.isHidden and style.fullInventoryCount(g_currentVehicle.item) == 0:
                self._modifiedStyle = None
            else:
                self._modifiedStyle = style
        if style:
            self._currentOutfit = style.getOutfit(self._currentSeason)
        else:
            self._currentOutfit = self._modifiedOutfits[self._currentSeason]
        return

    def __cancelModifiedOufits(self):
        for season in SeasonType.COMMON_SEASONS:
            self._modifiedOutfits[season] = self._originalOutfits[season].copy()

    def __cancelModifiedStyle(self):
        self._modifiedStyle = self._originalStyle

    def __onOutfitChanged(self):
        self.refreshOutfit()

    def __preserveState(self):
        self._state.update(modifiedStyle=self._modifiedStyle, modifiedOutfits={season:outfit.copy() for season, outfit in self._modifiedOutfits.iteritems()})

    def __restoreState(self):
        self._modifiedStyle = self._state.get('modifiedStyle')
        self._modifiedOutfits = self._state.get('modifiedOutfits')
        if self._modifiedStyle:
            self._modifiedStyle = self.service.getItemByCD(self._modifiedStyle.intCD)
        self._state.clear()

    def __onCacheResync(self, *_):
        if g_currentVehicle.isPresent():
            self.carveUpOutfits(preserve=True)
            self.__updateVisibleTabsList()
            self.refreshOutfit()
        self.onCacheResync()

    def __updateVisibleTabsList(self):
        visibleTabs = defaultdict(set)
        anchorsData = g_currentVehicle.hangarSpace.getSlotPositions()
        requirement = createCustomizationBaseRequestCriteria(g_currentVehicle.item, self.eventsCache.randomQuestsProgress, self.getAppliedItems())
        items = self.service.getItems(GUI_ITEM_TYPE.CUSTOMIZATIONS, criteria=requirement)
        for item in sorted(items.itervalues(), key=comparisonKey):
            tabIndex = TYPE_TO_TAB_IDX.get(item.itemTypeID)
            if tabIndex not in C11nTabs.VISIBLE or tabIndex == C11nTabs.CAMOUFLAGE and g_currentVehicle.item.descriptor.type.hasCustomDefaultCamouflage:
                continue
            for seasonType in SeasonType.COMMON_SEASONS:
                if item.season & seasonType:
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

        self.__visibleTabs = visibleTabs
