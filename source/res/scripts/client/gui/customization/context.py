# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/context.py
from collections import defaultdict
from copy import deepcopy
from functools import partial
from collections import namedtuple
import logging
import BigWorld
import Event
from AccountCommands import isCodeValid
from debug_utils import LOG_WARNING
from gui.shared.utils import code2str
from soft_exception import SoftException
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.decorators import process
from gui import g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, C11nTabs, TABS_SLOT_TYPE_MAPPING, TYPES_ORDER, SEASONS_ORDER, getStylePurchaseItems, getStyleInventoryCount, getItemInventoryCount, getItemAppliedCount, formatPersonalNumber, OutfitInfo, getCustomPurchaseItems, AdditionalPurchaseGroups, getOutfitWithoutItems, fitPersonalNumber
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchors_updater import VehicleAnchorsUpdater
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsSeller
from gui.shared.gui_items.processors.vehicle import VehicleAutoStyleEquipProcessor
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.customization.containers import emptyComponent
from items.components.c11n_components import isPersonalNumberAllowed
from items.components.c11n_constants import ApplyArea, SeasonType, DEFAULT_SCALE_FACTOR_ID, DEFAULT_PALETTE, Options, ProjectionDecalDirectionTags
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, C11nId, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_IDX, appliedToFromSlotsIds, QUANTITY_LIMITED_CUSTOMIZATION_TYPES
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
from constants import CLIENT_COMMAND_SOURCES
_logger = logging.getLogger(__name__)
CaruselItemData = namedtuple('CaruselItemData', ('index', 'intCD'))
CaruselItemData = partial(CaruselItemData, index=-1, intCD=-1)
InscriptionSlotInfo = namedtuple('InscriptionSlotInfo', ('item', 'number'))

class CustomizationContext(object):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)

    @property
    def visibleTabs(self):
        return self.__visibleTabs[self._currentSeason]

    @property
    def stylesTabEnabled(self):
        return self.__stylesTabEnabled[self._currentSeason]

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
    def selectedAnchor(self):
        return self._selectedAnchor

    @property
    def selectedSlot(self):
        return self.getSlotIdByAnchorId(self._selectedAnchor)

    @property
    def selectedCarouselItem(self):
        return self._selectedCarouselItem

    @property
    def vehicleAnchorsUpdater(self):
        return self._vehicleAnchorsUpdater

    @property
    def c11CameraManager(self):
        return self._c11CameraManager

    @property
    def storedPersonalNumber(self):
        return self._storedPersonalNumber

    def __init__(self):
        self._currentSeason = SeasonType.SUMMER
        self.__visibleTabs = defaultdict(list)
        self.__stylesTabEnabled = {seasonType:False for seasonType in SeasonType.COMMON_SEASONS}
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
        self._selectedCarouselItem = CaruselItemData()
        self._selectedAnchor = C11nId()
        self._eventsManager = Event.EventManager()
        self._vehicleAnchorsUpdater = None
        self._c11CameraManager = None
        self._autoRentEnabled = False
        self._autoRentChangeSource = CLIENT_COMMAND_SOURCES.UNDEFINED
        self._carouselItems = None
        self.__prolongStyleRent = False
        self.onCustomizationSeasonChanged = Event.Event(self._eventsManager)
        self.onCustomizationModeChanged = Event.Event(self._eventsManager)
        self.onCustomizationTabChanged = Event.Event(self._eventsManager)
        self.onCustomizationTabsUpdated = Event.Event(self._eventsManager)
        self.onCustomizationItemInstalled = Event.Event(self._eventsManager)
        self.onCustomizationItemsRemoved = Event.Event(self._eventsManager)
        self.onCamouflageColorChanged = Event.Event(self._eventsManager)
        self.onCamouflageScaleChanged = Event.Event(self._eventsManager)
        self.onProjectionDecalScaleChanged = Event.Event(self._eventsManager)
        self.onProjectionDecalMirrored = Event.Event(self._eventsManager)
        self.onNextCarouselItemInstalled = Event.Event(self._eventsManager)
        self.onCustomizationItemsBought = Event.Event(self._eventsManager)
        self.onCustomizationItemSold = Event.Event(self._eventsManager)
        self.onCacheResync = Event.Event(self._eventsManager)
        self.onChangesCanceled = Event.Event(self._eventsManager)
        self.onCaruselItemSelected = Event.Event(self._eventsManager)
        self.onCaruselItemUnselected = Event.Event(self._eventsManager)
        self.onEditModeStarted = Event.Event(self._eventsManager)
        self.onEditModeFinished = Event.Event(self._eventsManager)
        self.onCarouselFilter = Event.Event(self._eventsManager)
        self.onCustomizationAnchorSelected = Event.Event(self._eventsManager)
        self.onPropertySheetShown = Event.Event(self._eventsManager)
        self.onPropertySheetHidden = Event.Event(self._eventsManager)
        self.onShowStyleInfo = Event.Event(self._eventsManager)
        self.onStyleInfoHidden = Event.Event(self._eventsManager)
        self.onLocateToStyleInfo = Event.Event(self._eventsManager)
        self.onCustomizationItemDataChanged = Event.Event(self._eventsManager)
        self.onClearItem = Event.Event(self._eventsManager)
        self.onProlongStyleRent = Event.Event(self._eventsManager)
        self.onChangeAutoRent = Event.Event(self._eventsManager)
        self.onResetC11nItemsNovelty = Event.Event(self._eventsManager)
        self.onGetItemBackToHand = Event.Event(self._eventsManager)
        self.onPersonalNumberCleared = Event.Event(self._eventsManager)
        self.onSlotUnselected = Event.Event(self._eventsManager)
        self.onSelectAnchor = Event.Event(self._eventsManager)
        self.onFilterPopoverClosed = Event.Event(self._eventsManager)
        self.onCarouselRebuild = Event.Event(self._eventsManager)
        self.onFiltersRefreshNeeded = Event.Event(self._eventsManager)
        self.onAnchorHovered = Event.Event(self._eventsManager)
        self.onAnchorUnhovered = Event.Event(self._eventsManager)
        self.onAnchorsStateChanged = Event.Event(self._eventsManager)
        g_currentVehicle.onChangeStarted += self.__onChangeStarted
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self._storedPersonalNumber = None
        return

    def setCarouselItems(self, carouselItems):
        self._carouselItems = carouselItems
        self.onCarouselRebuild()

    def changeSeason(self, seasonType):
        self._currentSeason = seasonType
        self.refreshOutfit()
        self.onCustomizationSeasonChanged(self._currentSeason)

    def changeAutoRent(self, source=CLIENT_COMMAND_SOURCES.UNDEFINED):
        self._autoRentEnabled = not self._autoRentEnabled
        if source != CLIENT_COMMAND_SOURCES.UNDEFINED:
            self._autoRentChangeSource = source
        self.itemDataChanged(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0, refreshCarousel=True)
        self.onChangeAutoRent()

    def autoRentEnabled(self):
        return self._autoRentEnabled

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

    def tabChanged(self, tabIndex, update=False):
        self._tabIndex = tabIndex
        if self._tabIndex == C11nTabs.EFFECT:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.MODIFICATION, regionIdx=0)
        elif self._tabIndex == C11nTabs.STYLE:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        else:
            self._selectedAnchor = C11nId()
        self._selectedCarouselItem = CaruselItemData()
        if update:
            self.onCustomizationTabsUpdated(tabIndex)
        else:
            self.onCustomizationTabChanged(tabIndex)

    def anchorSelected(self, slotType, areaId, regionIdx):
        if self._tabIndex in (C11nTabs.EFFECT, C11nTabs.STYLE):
            return False
        else:
            self._selectedAnchor = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
            res = False
            if areaId == -1 or regionIdx == -1:
                self.onSlotUnselected()
                return False
            if self.currentTab == C11nTabs.INSCRIPTION:
                currentItem = self.getItemFromSelectedRegion()
                if currentItem is not None and currentItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                    currentComponent = self.getComponentFromSelectedRegion()
                    self.storePersonalNumber(currentComponent.number)
                else:
                    self.clearStoredPersonalNumber()
            if self.currentTab == C11nTabs.PROJECTION_DECAL:
                currentComponent = self.getComponentFromSelectedRegion()
                if currentComponent is not None and currentComponent.preview:
                    slot = self.currentOutfit.getContainer(self.selectedSlot.areaId).slotFor(self.selectedSlot.slotType)
                    slot.remove(idx=self.selectedSlot.regionIdx)
            if self._selectedCarouselItem.intCD != -1:
                slotId = self.__getFreeSlot(self.selectedAnchor, self.currentSeason)
                newItem = self.service.getItemByCD(self._selectedCarouselItem.intCD)
                if slotId is not None:
                    if not self.__isItemInstalledInOutfitSlot(slotId, newItem.intCD):
                        currentItem = self.getItemFromSelectedRegion()
                        currentComponent = self.getComponentFromSelectedRegion()
                        newComponent = self.__getComponent(newItem, currentItem, currentComponent, self.selectedAnchor)
                        seasonIdx = SEASON_TYPE_TO_IDX[self.currentSeason]
                        res = self.installItem(newItem.intCD, slotId, seasonIdx, newComponent)
                    elif slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                        multiSlot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
                        multiSlot.moveSlotTop(slotId)
                        self.currentOutfit.invalidate()
                        self.refreshOutfit()
            self.onCustomizationAnchorSelected(self.selectedAnchor.slotType, self.selectedAnchor.areaId, self.selectedAnchor.regionIdx)
            return res

    def getSlotIdByAnchorId(self, anchorId, season=None):
        if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return anchorId
        else:
            if season is None:
                season = self.currentSeason
            outfit = self._modifiedOutfits[season]
            anchor = self.getVehicleAnchor(anchorId)
            if anchor is None:
                return
            multySlot = outfit.getContainer(anchorId.areaId).slotFor(anchorId.slotType)
            if multySlot is not None:
                for regionIdx in range(multySlot.capacity()):
                    component = multySlot.getComponent(regionIdx)
                    if component is not None and component.slotId == anchor.slotId:
                        return C11nId(areaId=anchorId.areaId, slotType=anchorId.slotType, regionIdx=regionIdx)

            return
            return

    def getAnchorBySlotId(self, slotId):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            anchor = self.getVehicleAnchor(slotId)
            return anchor
        outfit = self._modifiedOutfits[self.currentSeason]
        multySlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        if multySlot is not None:
            slotData = multySlot.getSlotData(slotId.regionIdx)
            anchor = g_currentVehicle.item.getAnchorById(slotData.component.slotId)
            return anchor
        else:
            return

    def getVehicleAnchor(self, slotId):
        if not g_currentVehicle.isPresent():
            return None
        else:
            anchor = g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
            return anchor

    def installItem(self, intCD, slotId, seasonIdx, component=None):
        if slotId is None:
            return False
        else:
            item = self.service.getItemByCD(intCD)
            prevItem = self.getItemFromRegion(slotId)
            if prevItem is None or prevItem != item:
                if self.isBuyLimitReached(item):
                    SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
                    return False
            if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                if component is not None and component.isFilled():
                    number = fitPersonalNumber(component.number, item.digitsCount)
                    number = formatPersonalNumber(number, item.digitsCount)
                    if isPersonalNumberAllowed(number):
                        component.number = number
                    else:
                        component.number = ''
                        self.clearStoredPersonalNumber()
                        self.onPersonalNumberCleared(number)
            if slotId.slotType == GUI_ITEM_TYPE.STYLE:
                self._modifiedStyle = item
            else:
                season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
                outfit = self._modifiedOutfits[season]
                multiSlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
                multiSlot.set(item, idx=slotId.regionIdx, component=component)
                if slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    regionIdx = multiSlot.moveSlotTop(slotId)
                    slotId = C11nId(areaId=slotId.areaId, slotType=slotId.slotType, regionIdx=regionIdx)
                outfit.invalidate()
            self.refreshOutfit()
            buyLimitReached = self.isBuyLimitReached(item)
            self.onCustomizationItemInstalled(item, component, slotId, buyLimitReached)
            return True

    def previewSelectedDecal(self, anchorId):
        if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return
        else:
            intCD = self.selectedCarouselItem.intCD
            if intCD == -1:
                return
            item = self.service.getItemByCD(intCD)
            if self.isBuyLimitReached(item):
                return
            slotId = self.__getFreeSlot(anchorId, self.currentSeason)
            if slotId is None:
                return
            multiSlot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            component = self.__getComponent(item=item, prevItem=None, currentComponent=None, selectedAnchor=anchorId)
            component.preview = True
            multiSlot.set(item, idx=slotId.regionIdx, component=component)
            multiSlot.moveSlotTop(slotId)
            self.currentOutfit.invalidate()
            self.refreshOutfit()
            return

    def removeDecalPreview(self, anchorId):
        if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return
        else:
            slotId = self.getSlotIdByAnchorId(anchorId)
            if slotId is None:
                return
            slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            component = slot.getComponent(slotId.regionIdx)
            if component is not None and component.preview:
                slot.remove(idx=slotId.regionIdx)
            self.refreshOutfit()
            return

    def isPossibleToInstallToAllTankAreas(self, season, slotType, currentSlotData):
        if currentSlotData.item.isLimited or currentSlotData.item.isHidden:
            needed = 0
            for areaId in Area.TANK_PARTS:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
                multiSlot = self.currentOutfit.getContainer(areaId).slotFor(slotType)
                for regionIdx in regionsIndexes:
                    item = multiSlot.getItem(regionIdx)
                    if item is None or item != currentSlotData.item:
                        needed += 1

            inventoryCount = self.getItemInventoryCount(currentSlotData.item)
            toBye = needed - inventoryCount
            return toBye <= currentSlotData.item.buyCount
        else:
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
                    self.installItem(currentSlotData.item.intCD, C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx), currentSeasonIdx, currentSlotData.component)
                    additionalyApplyedItems += 1

        return additionalyApplyedItems

    def isPossibleToInstallItemForAllSeasons(self, areaID, slotType, regionIdx, currentSlotData):
        if currentSlotData.item.isLimited or currentSlotData.item.isHidden:
            needed = 0
            for season in SeasonType.COMMON_SEASONS:
                slotId = self.getSlotIdByAnchorId(C11nId(areaId=areaID, slotType=slotType, regionIdx=regionIdx), season)
                outfit = self.getModifiedOutfit(season)
                if slotId is not None:
                    item = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).getItem(slotId.regionIdx)
                else:
                    item = None
                if item is None or item != currentSlotData.item:
                    needed += 1

            if currentSlotData.item.isLimited:
                purchaseLimit = self.getPurchaseLimit(currentSlotData.item)
                inventoryCount = self.getItemInventoryCount(currentSlotData.item)
                return purchaseLimit + inventoryCount >= needed
            inventoryCount = self.getItemInventoryCount(currentSlotData.item)
            return inventoryCount >= needed
        else:
            return True

    def getLockedProjectionDecalSeasons(self, regionIdx):
        lockedSeasons = []
        for season in SeasonType.COMMON_SEASONS:
            outfit = self.getModifiedOutfit(season)
            if self.isC11nItemsQuantityLimitReached(outfit, GUI_ITEM_TYPE.PROJECTION_DECAL):
                region = self.getFilledProjectionDecalSlotRegion(regionIdx, season)
                if region == -1:
                    lockedSeasons.append(season)

        return lockedSeasons

    def installItemForAllSeasons(self, areaID, slotType, regionIdx, currentSlotData):
        additionalyApplyedItems = 0
        for season in SeasonType.COMMON_SEASONS:
            anchorId = C11nId(areaId=areaID, slotType=slotType, regionIdx=regionIdx)
            slotId = self.getSlotIdByAnchorId(anchorId, season)
            outfit = self.getModifiedOutfit(season)
            if slotId is None:
                region = self.getFilledProjectionDecalSlotRegion(regionIdx, season)
                if region == -1:
                    slotId = self.__getFreeSlot(anchorId, season)
                else:
                    slotId = C11nId(areaId=areaID, slotType=slotType, regionIdx=region)
            slotData = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).getSlotData(slotId.regionIdx)
            df = currentSlotData.weakDiff(slotData)
            if slotData.item is None or df.item is not None:
                seasonIdx = SEASON_TYPE_TO_IDX[season]
                self.installItem(currentSlotData.item.intCD, slotId, seasonIdx, currentSlotData.component)
                additionalyApplyedItems += 1

        return additionalyApplyedItems

    def removeItemFromSlot(self, season, slotId, refresh=True):
        if slotId is None:
            return
        else:
            outfit = self._modifiedOutfits[season]
            slot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            if slot.capacity() > slotId.regionIdx:
                item = slot.getItem(slotId.regionIdx)
                if item is not None and not item.isHiddenInUI():
                    slot.remove(idx=slotId.regionIdx)
            if refresh:
                self.refreshOutfit()
                self.onCustomizationItemsRemoved()
            return

    def removeItemFromAllTankAreas(self, season, slotType):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            for regionIdx in regionsIndexes:
                slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
                self.removeItemFromSlot(season, slotId, False)

        self.refreshOutfit()
        self.onCustomizationItemsRemoved()

    def removeItemForAllSeasons(self, areaId, slotType, regionIdx):
        for season in SeasonType.COMMON_SEASONS:
            slotId = self.getSlotIdByAnchorId(C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx), season)
            self.removeItemFromSlot(season, slotId, False)

        self.refreshOutfit()
        self.onCustomizationItemsRemoved()

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
                if item and (not filterMethod or filterMethod(item)) and not item.isHiddenInUI():
                    slot.remove(idx)

        if refresh:
            self.refreshOutfit()
            self.onCustomizationItemsRemoved()

    def switchToCustom(self):
        if self._mode != C11nMode.CUSTOM:
            self._mode = C11nMode.CUSTOM
            self.tabChanged(self._lastTab)
            self.refreshOutfit()
            self.onCustomizationModeChanged(self._mode)

    def switchToStyle(self):
        if self._mode != C11nMode.STYLE:
            self._lastTab = self._tabIndex
            self._mode = C11nMode.STYLE
            self.tabChanged(C11nTabs.STYLE)
            self.refreshOutfit()
            self.onCustomizationModeChanged(self._mode)

    def cancelChanges(self):
        if self._mode == C11nMode.STYLE:
            self.__cancelModifiedStyle()
        else:
            self.__cancelModifiedOufits()
        self.refreshOutfit()
        self.clearStoredPersonalNumber()
        self.onChangesCanceled()

    def caruselItemSelected(self, index, intCD):
        if index == -1:
            return
        else:
            prevItemSelected = self.isCaruselItemSelected()
            self._selectedCarouselItem = CaruselItemData(index=index, intCD=intCD)
            itemSelected = self.isCaruselItemSelected()
            if self.isAnyAnchorSelected() and itemSelected and not prevItemSelected:
                slotId = self.__getFreeSlot(self.selectedAnchor, self.currentSeason)
                if slotId is None:
                    return
                item = self.service.getItemByCD(intCD)
                currentItem = self.getItemFromSelectedRegion()
                currentComponent = self.getComponentFromSelectedRegion()
                component = self.__getComponent(item, currentItem, currentComponent, self.selectedAnchor)
                if self.currentTab == C11nTabs.INSCRIPTION:
                    slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
                    slotData = slot.getSlotData(slotId.regionIdx)
                    if slotData.item is not None and slotData.item.itemTypeID != item.itemTypeID and abs(self._carouselItems.index(slotData.item.intCD) - index) == 1:
                        self.__manageStoredPersonalNumber(slotData, item)
                        if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and self.storedPersonalNumber is not None:
                            component.number = self.storedPersonalNumber
                    elif item.itemTypeID != GUI_ITEM_TYPE.PERSONAL_NUMBER:
                        self.clearStoredPersonalNumber()
                self.installItem(intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason], component)
                self._selectedCarouselItem = CaruselItemData()
            else:
                self.service.highlightRegions(self.getEmptyRegions())
            self.onCaruselItemSelected(self._selectedCarouselItem.index, self._selectedCarouselItem.intCD)
            return

    def caruselItemUnselected(self):
        self.service.highlightRegions(ApplyArea.NONE)
        if self._selectedCarouselItem.index != -1:
            prevSelectCaruselItem = self._selectedCarouselItem
            self._selectedCarouselItem = CaruselItemData()
            self.onCaruselItemUnselected(prevSelectCaruselItem.index, prevSelectCaruselItem.intCD)

    def isCaruselItemSelected(self):
        return self._selectedCarouselItem.index != -1

    def applyCarouselFilter(self, **kwargs):
        self.onCarouselFilter(**kwargs)

    def installNextCarouselItem(self, reverse):
        _, item = self.__getNextCarouselItem(reverse)
        if item is None:
            return
        else:
            component = None
            if self.currentTab != C11nTabs.STYLE:
                outfit = self.currentOutfit
                slot = outfit.getContainer(self.selectedSlot.areaId).slotFor(self.selectedSlot.slotType)
                slotData = slot.getSlotData(self.selectedSlot.regionIdx)
                component = self.__getComponent(item, slotData.item, slotData.component, self.selectedAnchor)
                if self.currentTab == C11nTabs.INSCRIPTION:
                    if slotData.item.itemTypeID != item.itemTypeID:
                        self.__manageStoredPersonalNumber(slotData, item)
                        if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and self.storedPersonalNumber is not None:
                            component.number = self.storedPersonalNumber
                    elif item.itemTypeID != GUI_ITEM_TYPE.PERSONAL_NUMBER:
                        self.clearStoredPersonalNumber()
            self.installItem(item.intCD, self.selectedSlot, SEASON_TYPE_TO_IDX[self.currentSeason], component)
            self.onNextCarouselItemInstalled(item)
            return

    def getItemSwitchersState(self):
        nextIdx, nextItem = self.__getNextCarouselItem(reverse=False)
        prevIdx, prevItem = self.__getNextCarouselItem(reverse=True)
        installNext = nextIdx is not None and nextItem is not None
        installPrev = prevIdx is not None and prevItem is not None
        return (installPrev, installNext)

    def resetC11nItemsNovelty(self, itemsList):

        def _callback(self, resultID):
            if isCodeValid(resultID):
                self.onResetC11nItemsNovelty()
            else:
                LOG_WARNING('Error occurred while trying to reset c11n items novelty, reason by resultId = {}: {}'.format(resultID, code2str(resultID)))

        BigWorld.player().shop.resetC11nItemsNovelty([ (g_currentVehicle.item.intCD, intCD) for intCD in itemsList ], lambda resultId: _callback(self, resultId))

    def changeCamouflageColor(self, areaId, regionIdx, paletteIdx):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.palette != paletteIdx:
            component.palette = paletteIdx
            self.refreshOutfit()
            self.onCamouflageColorChanged(areaId, regionIdx, paletteIdx)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.CAMOUFLAGE, regionIdx)

    def changeCamouflageScale(self, areaId, regionIdx, scale):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.patternSize != scale:
            component.patternSize = scale
            self.refreshOutfit()
            self.onCamouflageScaleChanged(areaId, regionIdx, scale)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.CAMOUFLAGE, regionIdx)

    def changeProjectionDecalScale(self, areaId, regionIdx, scale):
        slotId = self.getSlotIdByAnchorId(C11nId(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        if component.scaleFactorId != scale:
            component.scaleFactorId = scale
            self.refreshOutfit()
            self.onProjectionDecalScaleChanged(areaId, regionIdx, scale)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx)

    def changePersonalNumberValue(self, value, slotId=None):
        slotId = slotId or self.selectedSlot
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        if component is None:
            return
        else:
            if component.number != value:
                component.number = value
                self.refreshOutfit()
            self.itemDataChanged(slotId.areaId, slotId.slotType, self.selectedAnchor.regionIdx)
            return

    def storePersonalNumber(self, number, digitsCount=None):
        if not number or not int(number):
            return
        digitsCount = digitsCount or self.getItemFromSelectedRegion().digitsCount
        formattedNumber = formatPersonalNumber(number, digitsCount)
        self._storedPersonalNumber = formattedNumber

    def clearStoredPersonalNumber(self):
        self._storedPersonalNumber = None
        return

    def mirrorProjectionDecal(self, areaId, regionIdx):
        slotId = self.getSlotIdByAnchorId(C11nId(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        component.options ^= Options.MIRRORED
        self.refreshOutfit()
        self.onProjectionDecalMirrored(areaId, regionIdx)
        self.itemDataChanged(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx)

    def getOutfitsInfo(self):
        outfitsInfo = {}
        for season in SEASONS_ORDER:
            outfitsInfo[season] = OutfitInfo(self._originalOutfits[season], self._modifiedOutfits[season])

        return outfitsInfo

    def getStyleInfo(self):
        return OutfitInfo(self._originalStyle, self._modifiedStyle)

    def getPurchaseItems(self):
        if self._mode == C11nMode.CUSTOM:
            currentSeason = self.currentSeason
            order = [currentSeason] + [ s for s in SEASONS_ORDER if s != currentSeason ]
            return getCustomPurchaseItems(self.getOutfitsInfo(), order)
        return getStylePurchaseItems(self.getStyleInfo(), buyMore=self.__prolongStyleRent)

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

    def prolongStyleRent(self, style):
        self.switchToStyle()
        if style is not None:
            self._modifiedStyle = style
            self.__prolongStyleRent = True
            self.refreshOutfit()
            self.itemDataChanged(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            self.onProlongStyleRent()
        return

    @process('customizationApply')
    def applyItems(self, purchaseItems):
        purchaseItems = deepcopy(purchaseItems)
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
            if self.__prolongStyleRent:
                if self._modifiedStyle.boundInventoryCount.get(g_currentVehicle.item.intCD, 0) > 0 or self._originalStyle and self._modifiedStyle.id == self._originalStyle.id:
                    self.service.buyItems(self._modifiedStyle, 1, g_currentVehicle.item)
                self.__prolongStyleRent = False
            result = yield StyleApplier(g_currentVehicle.item, self._modifiedStyle).request()
            results.append(result)
        if self._autoRentEnabled != g_currentVehicle.item.isAutoRentStyle:
            yield VehicleAutoStyleEquipProcessor(g_currentVehicle.item, self._autoRentEnabled, self._autoRentChangeSource).request()
            self._autoRentChangeSource = CLIENT_COMMAND_SOURCES.UNDEFINED
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
        if not g_currentVehicle.isPresent():
            raise SoftException('There is not vehicle in hangar for customization.')
        self._autoRentEnabled = g_currentVehicle.item.isAutoRentStyle
        self._vehicleAnchorsUpdater = VehicleAnchorsUpdater(self.service, self)
        self._vehicleAnchorsUpdater.startUpdater(self.settingsCore.interfaceScale.get())
        self._c11CameraManager = C11nHangarCameraManager()
        self._c11CameraManager.init()
        self.settingsCore.interfaceScale.onScaleExactlyChanged += self.__onInterfaceScaleChanged
        self.service.onOutfitChanged += self.__onOutfitChanged
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.carveUpOutfits()
        currVehSeasonType = g_tankActiveCamouflage.get(g_currentVehicle.item.intCD, SeasonType.SUMMER)
        self._currentSeason = currVehSeasonType
        if self._originalStyle:
            self._mode = C11nMode.STYLE
            self._tabIndex = C11nTabs.STYLE
        else:
            self._mode = C11nMode.CUSTOM
            self._tabIndex = C11nTabs.PAINT
            notInst = all([ not self._originalOutfits[season].isInstalled() for season in SeasonType.COMMON_SEASONS ])
            if notInst and not self.isOutfitsEmpty(self._modifiedOutfits) and not self._modifiedStyle:
                self._mode = C11nMode.STYLE
        self._originalMode = self._mode
        self.refreshOutfit()

    def fini(self):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.service.onOutfitChanged -= self.__onOutfitChanged
        g_currentVehicle.onChangeStarted -= self.__onChangeStarted
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self._eventsManager.clear()
        self.settingsCore.interfaceScale.onScaleExactlyChanged -= self.__onInterfaceScaleChanged
        if self._c11CameraManager is not None:
            self._c11CameraManager.fini()
        self._c11CameraManager = None
        if self._vehicleAnchorsUpdater is not None:
            self._vehicleAnchorsUpdater.stopUpdater()
        self._vehicleAnchorsUpdater = None
        return

    def __onVehicleChanged(self):
        self.carveUpOutfits()
        self.refreshOutfit()

    def __onChangeStarted(self):
        self.__prolongStyleRent = False
        self._autoRentEnabled = g_currentVehicle.item.isAutoRentStyle

    def checkSlotsFillingForSeason(self, season):
        checkedSlotTypes = (TABS_SLOT_TYPE_MAPPING[tabId] for tabId in self.visibleTabs)
        return (self.checkSlotsFilling(slotType, season) for slotType in checkedSlotTypes)

    def checkSlotsFilling(self, slotType, season):
        outfit = self.getModifiedOutfit(season)
        slotsCount = 0
        filledSlotsCount = 0
        for areaId in Area.ALL:
            if slotType not in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                if areaId == Area.MISC:
                    availableRegions = tuple(g_currentVehicle.item.getAnchors(slotType, areaId))
                    maxRegions = QUANTITY_LIMITED_CUSTOMIZATION_TYPES[slotType]
                    regionsIndexes = tuple(range(min(len(availableRegions), maxRegions)))
                else:
                    regionsIndexes = ()
            else:
                regionsIndexes = ()
            slotsCount += len(regionsIndexes)
            for regionIdx in regionsIndexes:
                item = outfit.getContainer(areaId).slotFor(slotType).getItem(regionIdx)
                if item is not None:
                    filledSlotsCount += 1

        return (slotsCount, filledSlotsCount)

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
                if self._modifiedStyle and self._originalStyle:
                    return self._modifiedStyle.intCD != self._originalStyle.intCD or self._autoRentEnabled != g_currentVehicle.item.isAutoRentStyle
                return not (self._modifiedStyle is None and self._originalStyle is None)
            for season in SeasonType.COMMON_SEASONS:
                outfit = self._modifiedOutfits[season]
                currOutfit = self._originalOutfits[season]
                for _, component in currOutfit.diff(outfit).itemsFull():
                    if component.isFilled():
                        return True

                for _, component in outfit.diff(currOutfit).itemsFull():
                    if component.isFilled():
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

    def isAnchorSelected(self, slotType, areaId, regionIdx):
        return self.selectedAnchor.areaId == areaId and self.selectedAnchor.slotType == slotType and self.selectedAnchor.regionIdx == regionIdx

    def isAnyAnchorSelected(self):
        return self.selectedAnchor.areaId != -1 and self.selectedAnchor.slotType != -1 and self.selectedAnchor.regionIdx != -1

    def isSlotFilled(self, anchorId):
        if anchorId.slotType == GUI_ITEM_TYPE.STYLE:
            return self._modifiedStyle is not None
        else:
            slotId = self.getSlotIdByAnchorId(anchorId)
            if slotId is not None:
                outfit = self._modifiedOutfits[self._currentSeason]
                area = outfit.getContainer(slotId.areaId)
                if area is not None:
                    multySlot = area.slotFor(slotId.slotType)
                    if multySlot is not None:
                        slotData = multySlot.getSlotData(slotId.regionIdx)
                        return slotData.item is not None and slotData.component.isFilled()
            return False
            return

    def getFilledProjectionDecalSlotRegion(self, regionIdx, season):
        slotType, areaId = GUI_ITEM_TYPE.PROJECTION_DECAL, Area.MISC
        slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
        anchor = self.getVehicleAnchor(slotId)
        outfit = self._modifiedOutfits[season]
        multySlot = outfit.getContainer(areaId).slotFor(slotType)
        for region in range(multySlot.capacity()):
            component = multySlot.getComponent(region)
            if component is not None:
                itemSlot = g_currentVehicle.item.getAnchorById(component.slotId)
                if itemSlot.slotId == anchor.slotId:
                    return region

        return -1

    def isC11nItemsQuantityLimitReached(self, outfit, slotType):
        if slotType not in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
            return False
        qtyDecals = 0
        for item in outfit.items():
            if item.itemTypeID == slotType:
                qtyDecals += 1

        return qtyDecals >= QUANTITY_LIMITED_CUSTOMIZATION_TYPES[slotType]

    def isBuyLimitReached(self, item):
        inventoryCount = self.getItemInventoryCount(item)
        appliedCount = getItemAppliedCount(item, self.getOutfitsInfo())
        fullCount = item.buyCount + item.inventoryCount + item.boundInventoryCount.get(g_currentVehicle.item.intCD, 0)
        isSpecial = item.isLimited or item.isHidden
        return isSpecial and inventoryCount == 0 and (item.buyCount == 0 or appliedCount >= fullCount)

    def getPurchaseLimit(self, item):
        appliedCount = getItemAppliedCount(item, self.getOutfitsInfo())
        inventoryCount = item.boundInventoryCount.get(g_currentVehicle.item.intCD, 0) + item.inventoryCount
        purchaseLimit = item.buyCount - max(appliedCount - inventoryCount, 0)
        return max(purchaseLimit, 0)

    def getEmptyRegions(self):
        emptyRegions = []
        slotType = TABS_SLOT_TYPE_MAPPING[self._tabIndex]
        for areaId in Area.ALL:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            for regionIdx in regionsIndexes:
                outfit = self.getModifiedOutfit(self._currentSeason)
                item = outfit.getContainer(areaId).slotFor(slotType).getItem(regionIdx)
                if item is None:
                    emptyRegions.append((areaId, slotType, regionIdx))

        mask = appliedToFromSlotsIds(emptyRegions)
        return mask

    def getItemFromSelectedRegion(self):
        return self.getItemFromRegion(self.selectedSlot) if self.selectedSlot is not None else None

    def getItemFromRegion(self, slotId):
        if slotId.slotType == GUI_ITEM_TYPE.STYLE:
            return self._modifiedStyle
        else:
            outfit = self.currentOutfit
            container = outfit.getContainer(slotId.areaId)
            return container.slotFor(slotId.slotType).getItem(slotId.regionIdx) if container else None

    def getComponentFromSelectedRegion(self):
        return self.getComponentFromRegion(self.selectedSlot) if self.selectedSlot is not None else None

    def getComponentFromRegion(self, slotId):
        if slotId.slotType == GUI_ITEM_TYPE.STYLE:
            return None
        else:
            outfit = self.currentOutfit
            container = outfit.getContainer(slotId.areaId)
            return container.slotFor(slotId.slotType).getComponent(slotId.regionIdx) if container else None

    def itemDataChanged(self, areaId, slotType, regionIdx, refreshCarousel=False):
        self.onCustomizationItemDataChanged(areaId, slotType, regionIdx, refreshCarousel)

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
            self.refreshOutfit()
        self.onCacheResync()

    def updateVisibleTabsList(self, visibleTabs, stylesTabEnabled):
        for seasonType in SeasonType.COMMON_SEASONS:
            self.__visibleTabs[seasonType] = sorted(list(visibleTabs[seasonType]), key=lambda it: TYPES_ORDER.index(TABS_SLOT_TYPE_MAPPING[it]))

        self.__stylesTabEnabled = stylesTabEnabled
        if self._mode == C11nMode.STYLE:
            tabIndex = C11nTabs.STYLE
            self._lastTab = first(self.visibleTabs, -1)
        else:
            tabIndex = first(self.visibleTabs, -1)
            self._lastTab = tabIndex
        self.tabChanged(tabIndex, update=True)

    def __getComponent(self, item, prevItem, currentComponent, selectedAnchor):
        baseComponent = None
        if self.currentTab != C11nTabs.STYLE:
            if prevItem is not None and prevItem.itemTypeID == item.itemTypeID:
                baseComponent = currentComponent
        anchor = self.getVehicleAnchor(selectedAnchor)
        if anchor is None:
            _logger.warning('Wrong slotId in ProjectDecalComponent (slotType=%(slotType)d areaId=%(areaId)s regionIdx=%(regionIdx)s)', {'slotType': selectedAnchor.slotType,
             'areaId': selectedAnchor.areaId,
             'regionIdx': selectedAnchor.regionIdx})
            return
        else:
            if baseComponent is not None:
                component = baseComponent
                if selectedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    component.slotId = anchor.slotId
                    if not item.canBeMirrored:
                        component.options = Options.NONE
                    elif prevItem.canBeMirrored:
                        if item.direction != prevItem.direction:
                            component.options ^= Options.MIRRORED
                    elif self.__ifNeedToMirrorProjectionDecal(item, anchor):
                        component.options |= Options.MIRRORED
                if selectedAnchor.slotType == GUI_ITEM_TYPE.CAMOUFLAGE:
                    component.palette = DEFAULT_PALETTE
            else:
                component = emptyComponent(item.itemTypeID)
                if selectedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    component.id = item.id
                    component.slotId = anchor.slotId
                    component.scaleFactorId = DEFAULT_SCALE_FACTOR_ID
                    if self.__ifNeedToMirrorProjectionDecal(item, anchor):
                        component.options |= Options.MIRRORED
            return component

    @staticmethod
    def __ifNeedToMirrorProjectionDecal(item, anchor):
        return item.canBeMirrored and item.direction != ProjectionDecalDirectionTags.ANY and anchor.direction != ProjectionDecalDirectionTags.ANY and item.direction != anchor.direction

    def __onInterfaceScaleChanged(self, scale):
        if self._vehicleAnchorsUpdater is not None:
            self._vehicleAnchorsUpdater.setInterfaceScale(scale)
        return

    def __isItemInstalledInOutfitSlot(self, slotId, itemIntCD):
        if slotId.slotType == GUI_ITEM_TYPE.STYLE:
            return self._modifiedStyle.intCD == itemIntCD
        else:
            outfit = self._modifiedOutfits[self._currentSeason]
            multySlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
            if multySlot is not None:
                item = multySlot.getItem(slotId.regionIdx)
                if item is not None:
                    return item.intCD == itemIntCD
            return False
            return

    def __getFreeSlot(self, anchorId, season):
        outfit = self.getModifiedOutfit(season)
        slotId = self.getSlotIdByAnchorId(anchorId, season)
        if slotId is not None:
            return slotId
        elif anchorId.slotType not in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
            return anchorId
        else:
            container = outfit.getContainer(anchorId.areaId)
            if container is None:
                return
            multySlot = outfit.misc.slotFor(anchorId.slotType)
            if multySlot is None:
                return
            for regionIdx in range(QUANTITY_LIMITED_CUSTOMIZATION_TYPES[anchorId.slotType]):
                if multySlot.getItem(regionIdx) is None:
                    return C11nId(areaId=anchorId.areaId, slotType=anchorId.slotType, regionIdx=regionIdx)

            return
            return

    def __manageStoredPersonalNumber(self, slotData, item):
        if slotData.item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
            self.storePersonalNumber(slotData.component.number)

    def __getNextCarouselItem(self, reverse):
        if not self.isAnyAnchorSelected() or self.isCaruselItemSelected():
            return (None, None)
        else:
            shift = -1 if reverse else 1
            tabIndex = self.currentTab
            if tabIndex == C11nTabs.STYLE:
                item = self.modifiedStyle
            else:
                item = self.getItemFromSelectedRegion()
            if item is not None and item.intCD in self._carouselItems:
                index = self._carouselItems.index(item.intCD) + shift
                while 0 <= index < len(self._carouselItems):
                    intCD = self._carouselItems[index]
                    item = self.service.getItemByCD(intCD)
                    if self.isBuyLimitReached(item):
                        index += shift
                    return (index, item)

            return (None, None)
