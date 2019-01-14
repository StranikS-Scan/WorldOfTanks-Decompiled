# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/context.py
from collections import defaultdict
from functools import partial
from collections import namedtuple
import logging
import Event
from soft_exception import SoftException
from CurrentVehicle import g_currentVehicle
from gui.shared.utils.decorators import process
from gui import g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, C11nTabs, TABS_ITEM_MAPPING, TYPES_ORDER, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_IDX, getStylePurchaseItems, getStyleInventoryCount, getItemInventoryCount, getItemAppliedCount, SEASONS_ORDER, OutfitInfo, getCustomPurchaseItems, AdditionalPurchaseGroups, getOutfitWithoutItems
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchors_updater import VehicleAnchorsUpdater
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsSeller
from gui.shared.gui_items.processors.vehicle import VehicleAutoStyleEquipProcessor
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.customization.containers import emptyComponent
from items.components.c11n_constants import ApplyArea, SeasonType, DEFAULT_SCALE_FACTOR_ID, Options, ProjectionDecalDirectionTags
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, C11nId, appliedToFromSlotsIds, QUANTITY_LIMITED_CUSTOMIZATION_TYPES
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
from gui.Scaleform.daapi.view.lobby.customization.customization_inscription_controller import PersonalNumEditStatuses, PersonalNumEditCommands
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
    def selectedCaruselItem(self):
        return self._selectedCaruselItem

    @property
    def vehicleAnchorsUpdater(self):
        return self._vehicleAnchorsUpdater

    @property
    def c11CameraManager(self):
        return self._c11CameraManager

    @property
    def storedInscriptionSlotInfo(self):
        return self._storedPersonalNumbers.get(self._selectedAnchor, InscriptionSlotInfo(None, None))

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
        self._selectedAnchor = C11nId()
        self._eventsManager = Event.EventManager()
        self._vehicleAnchorsUpdater = None
        self._c11CameraManager = None
        self._autoRentEnabled = False
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
        self.onCarouselFilter = Event.Event(self._eventsManager)
        self.onCustomizationAnchorSelected = Event.Event(self._eventsManager)
        self.onPropertySheetShown = Event.Event(self._eventsManager)
        self.onPropertySheetHidden = Event.Event(self._eventsManager)
        self.onCustomizationItemDataChanged = Event.Event(self._eventsManager)
        self.onClearItem = Event.Event(self._eventsManager)
        self.onPersonalNumberEditModeChanged = Event.Event(self._eventsManager)
        self.onPersonalNumberEditModeCmdSent = Event.Event(self._eventsManager)
        self.onProlongStyleRent = Event.Event(self._eventsManager)
        self.onChangeAutoRent = Event.Event(self._eventsManager)
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self._numberEditModeActive = False
        self._numberIsEmpty = True
        self._storedPersonalNumbers = defaultdict()
        return

    def setCarouselItems(self, carouselItems):
        self._carouselItems = carouselItems

    def setNumberEditModeActive(self, value):
        self._numberEditModeActive = value

    def getNumberEditModeActive(self):
        return self._numberEditModeActive

    numberEditModeActive = property(getNumberEditModeActive, setNumberEditModeActive)

    def changeSeason(self, seasonType):
        self._currentSeason = seasonType
        self.refreshOutfit()
        self.onCustomizationSeasonChanged(self._currentSeason)

    def changeAutoRent(self):
        self._autoRentEnabled = not self._autoRentEnabled
        self.itemDataChanged(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
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
        if self.numberEditModeActive:
            self.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        self._tabIndex = tabIndex
        if self._tabIndex == C11nTabs.EFFECT:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.MODIFICATION, regionIdx=0)
        elif self._tabIndex == C11nTabs.STYLE:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        else:
            self._selectedAnchor = C11nId()
        self._selectedCaruselItem = CaruselItemData()
        if update:
            self.onCustomizationTabsUpdated(tabIndex)
        else:
            self.onCustomizationTabChanged(tabIndex)

    def anchorSelected(self, slotType, areaId, regionIdx):
        if self._tabIndex in (C11nTabs.EFFECT, C11nTabs.STYLE):
            return False
        else:
            prevSelectedAnchor = self._selectedAnchor
            self._selectedAnchor = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
            if prevSelectedAnchor != self._selectedAnchor:
                if self._vehicleAnchorsUpdater is not None and self.currentTab in C11nTabs.REGIONS:
                    self._vehicleAnchorsUpdater.changeAnchorParams(prevSelectedAnchor, True, True)
            self.onCustomizationAnchorSelected(self._selectedAnchor.slotType, self._selectedAnchor.areaId, self._selectedAnchor.regionIdx)
            if areaId != -1 and regionIdx != -1 and self._selectedCaruselItem.intCD != -1:
                slotId = self.__getFreeSlot(self._selectedAnchor, self._currentSeason)
                if slotId is None or not self.__isItemInstalledInOutfitSlot(slotId, self._selectedCaruselItem.intCD):
                    item = self.service.getItemByCD(self._selectedCaruselItem.intCD)
                    component = self.__getComponent(item, self.selectedAnchor)
                    if self.installItem(self._selectedCaruselItem.intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason], component):
                        return True
            return False

    def getSlotIdByAnchorId(self, anchorId, season=None):
        if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return anchorId
        else:
            if season is None:
                season = self.currentSeason
            outfit = self._modifiedOutfits[season]
            anchorParams = self.service.getAnchorParams(anchorId.areaId, anchorId.slotType, anchorId.regionIdx)
            if anchorParams is None:
                return
            multySlot = outfit.getContainer(anchorId.areaId).slotFor(anchorId.slotType)
            if multySlot is not None:
                for regionIdx in range(multySlot.capacity()):
                    component = multySlot.getComponent(regionIdx)
                    if component is not None and component.slotId == anchorParams.vehicleSlotId:
                        return C11nId(areaId=anchorId.areaId, slotType=anchorId.slotType, regionIdx=regionIdx)

            return
            return

    def getAnchorBySlotId(self, slotId):
        if slotId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return g_currentVehicle.item.getAnchorBySlotId(slotId.slotType, slotId.areaId, slotId.regionIdx)
        outfit = self._modifiedOutfits[self.currentSeason]
        multySlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        if multySlot is not None:
            slotData = multySlot.getSlotData(slotId.regionIdx)
            anchor = g_currentVehicle.item.getAnchorById(slotData.component.slotId)
            return anchor
        else:
            return

    def installItem(self, intCD, slotId, seasonIdx, component=None):
        if slotId is None:
            return False
        else:
            item = self.service.getItemByCD(intCD)
            if self.isBuyLimitReached(item):
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
                return False
            if slotId.slotType == GUI_ITEM_TYPE.STYLE:
                self._modifiedStyle = item
            else:
                season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
                outfit = self._modifiedOutfits[season]
                if slotId.slotType == GUI_ITEM_TYPE.INSCRIPTION:
                    prevInstalledItem = self.getItemFromSelectedRegion()
                    if prevInstalledItem and not self.numberEditModeActive:
                        self.storeInscriptionSlotInfo()
                if item.itemTypeID != GUI_ITEM_TYPE.PERSONAL_NUMBER and self.numberEditModeActive:
                    self.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_BY_INSCRIPTION_SELECT)
                outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).set(item, idx=slotId.regionIdx, component=component)
                outfit.invalidate()
            if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and self.storedInscriptionSlotInfo[1]:
                self.restoreInscriptionSlotContent()
            self.refreshOutfit()
            buyLimitReached = self.isBuyLimitReached(item)
            self.onCustomizationItemInstalled(item, slotId, buyLimitReached)
            return True

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

            inventoryCount = self.getItemInventoryCount(currentSlotData.item)
            toBye = needed - inventoryCount
            return toBye <= currentSlotData.item.buyCount
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
        outfit = self._modifiedOutfits[season]
        slot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        if slot.capacity() > slotId.regionIdx:
            item = slot.getItem(slotId.regionIdx)
            if item is not None and not item.isHiddenInUI():
                slot.remove(idx=slotId.regionIdx)
                if item.itemTypeID in (GUI_ITEM_TYPE.PERSONAL_NUMBER, GUI_ITEM_TYPE.INSCRIPTION):
                    self.resetInscriptionSlotInfo()
        if refresh:
            self.refreshOutfit()
            self.onCustomizationItemsRemoved()
        return

    def removeItemFromAllTankAreas(self, season, slotType):
        for areaId in Area.TANK_PARTS:
            regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, slotType)
            for regionIdx in regionsIndexes:
                slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
                self.removeItemFromSlot(season, slotId)

    def removeItemForAllSeasons(self, areaId, slotType, regionIdx):
        for season in SeasonType.COMMON_SEASONS:
            slotId = self.getSlotIdByAnchorId(C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx), season)
            self.removeItemFromSlot(season, slotId, refresh=False)

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
            self.refreshOutfit()
            self.tabChanged(self._lastTab)
            self.onCustomizationModeChanged(self._mode)

    def switchToStyle(self):
        if self.numberEditModeActive:
            self.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        if self._mode != C11nMode.STYLE:
            self._lastTab = self._tabIndex
            self._mode = C11nMode.STYLE
            self.refreshOutfit()
            self.tabChanged(C11nTabs.STYLE)
            self.onCustomizationModeChanged(self._mode)

    def cancelChanges(self):
        if self._mode == C11nMode.STYLE:
            self.__cancelModifiedStyle()
        else:
            self.__cancelModifiedOufits()
        self.refreshOutfit()
        self.resetInscriptionSlotInfo()
        self.onChangesCanceled()

    def caruselItemSelected(self, index, intCD):
        prevItemSelected = self.isCaruselItemSelected()
        self._selectedCaruselItem = CaruselItemData(index=index, intCD=intCD)
        itemSelected = self.isCaruselItemSelected()
        if self.isAnyAnchorSelected() and itemSelected and not prevItemSelected:
            slotId = self.__getFreeSlot(self.selectedAnchor, self.currentSeason)
            if slotId is None:
                return False
            item = self.service.getItemByCD(intCD)
            component = self.__getComponent(item, self.selectedAnchor)
            self.installItem(intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason], component)
            self._selectedCaruselItem = CaruselItemData()
        else:
            self.service.highlightRegions(self.getEmptyRegions())
        self.onCaruselItemSelected(index, intCD)
        return

    def caruselItemUnselected(self):
        self.service.highlightRegions(ApplyArea.NONE)
        if self._selectedCaruselItem.index != -1:
            prevSelectCaruselItem = self._selectedCaruselItem
            self._selectedCaruselItem = CaruselItemData()
            self.onCaruselItemUnselected(prevSelectCaruselItem.index, prevSelectCaruselItem.intCD)

    def isCaruselItemSelected(self):
        return self._selectedCaruselItem.index != -1

    def applyCarouselFilter(self, **kwargs):
        self.onCarouselFilter(**kwargs)

    def installNextCarouselItem(self, reverse):
        carouselIndex, item = self.__getNextCarouselItem(reverse)
        if item is None:
            return
        else:
            slotId = self.selectedSlot
            if self.currentTab != C11nTabs.STYLE:
                outfit = self._modifiedOutfits[self._currentSeason]
                slot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
                slotData = slot.getSlotData(slotId.regionIdx)
                anchor = self.getAnchorBySlotId(slotId)
                if slotData.item.itemTypeID in (GUI_ITEM_TYPE.PERSONAL_NUMBER, GUI_ITEM_TYPE.INSCRIPTION) and not self.numberEditModeActive:
                    self.storeInscriptionSlotInfo()
                slotData.item = item
                slotData.component = self.__getComponent(item, self._selectedAnchor)
                if item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
                    if self.storedInscriptionSlotInfo.number:
                        self.restoreInscriptionSlotContent()
                    else:
                        self.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_STARTED)
                elif self.numberEditModeActive:
                    self.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
                outfit.invalidate()
                self.refreshOutfit()
                self.itemDataChanged(slotId.areaId, slotId.slotType, anchor.regionIdx, changeAnchor=False, updatePropertiesSheet=True)
            else:
                self.installItem(item.intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason])
            self.onNextCarouselItemInstalled(carouselIndex)
            return

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
            if item is not None:
                index = self._carouselItems.index(item.intCD) + shift
                while 0 <= index < len(self._carouselItems):
                    intCD = self._carouselItems[index]
                    item = self.service.getItemByCD(intCD)
                    if self.isBuyLimitReached(item):
                        index += shift
                    return (index, item)

            return (None, None)

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

    def changePersonalNumberValue(self, value):
        slotId = self.getSlotIdByAnchorId(C11nId(self._selectedAnchor.areaId, GUI_ITEM_TYPE.PERSONAL_NUMBER, self._selectedAnchor.regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        self._numberIsEmpty = not bool(value)
        if component.number != value:
            component.number = value
            self.refreshOutfit()
        self.itemDataChanged(slotId.areaId, slotId.slotType, self._selectedAnchor.regionIdx, changeAnchor=False, updatePropertiesSheet=False, refreshCarousel=False)

    def isOnly1ChangedNumberInEditMode(self):
        if self.numberEditModeActive and not g_currentVehicle.item.descriptor.type.hasCustomDefaultCamouflage:
            purchaseItems = [ it for it in self.getPurchaseItems() if not it.isDismantling and it.group == self.currentSeason ]
            return len(purchaseItems) == 1 and purchaseItems[0].item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER
        return False

    def storeInscriptionSlotInfo(self):
        slotId = self.getSlotIdByAnchorId(C11nId(self._selectedAnchor.areaId, GUI_ITEM_TYPE.PERSONAL_NUMBER, self._selectedAnchor.regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        slotData = slot.getSlotData(slotId.regionIdx)
        component = slot.getComponent(slotId.regionIdx)
        if slotData and slotData.item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER:
            self._storedPersonalNumbers[self._selectedAnchor] = InscriptionSlotInfo(slotData.item, component.number)
        elif slotData and slotData.item.itemTypeID == GUI_ITEM_TYPE.INSCRIPTION:
            self._storedPersonalNumbers[self._selectedAnchor] = InscriptionSlotInfo(slotData.item, None)
        return

    def restoreInscriptionSlotContent(self):
        inscriptionSlotInfo = self._storedPersonalNumbers.get(self._selectedAnchor, InscriptionSlotInfo(None, None))
        if inscriptionSlotInfo:
            number = inscriptionSlotInfo.number
            if number:
                self.changePersonalNumberValue(number)
            else:
                item = inscriptionSlotInfo.item
                slotId = self.__getFreeSlot(self._selectedAnchor, self._currentSeason)
                outfit = self._modifiedOutfits[self._currentSeason]
                outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).set(item, idx=slotId.regionIdx)
                outfit.invalidate()
                buyLimitReached = self.isBuyLimitReached(item)
                self.onCustomizationItemInstalled(item, slotId, buyLimitReached)
        return

    def resetInscriptionSlotInfo(self):
        self._storedPersonalNumbers.clear()

    def sendNumberEditModeCommand(self, cmd):
        self.onPersonalNumberEditModeCmdSent(cmd)

    def mirrorProjectionDecal(self, areaId, regionIdx):
        slotId = self.getSlotIdByAnchorId(C11nId(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        component.options ^= Options.MIRRORED
        self.refreshOutfit()
        self.onProjectionDecalMirrored(areaId, regionIdx)
        self.itemDataChanged(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx)

    def moveProjectionDecal(self, areaId, regionIdx, reverse=False):
        slotType = GUI_ITEM_TYPE.PROJECTION_DECAL
        outfit = self._modifiedOutfits[self._currentSeason]
        currentAnchorId = C11nId(areaId, slotType, regionIdx)
        currentAnchor = g_currentVehicle.item.getAnchorBySlotId(slotType, areaId, regionIdx)
        slotId = self.getSlotIdByAnchorId(currentAnchorId)
        slot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        slotData = slot.getSlotData(slotId.regionIdx)
        nextAnchor = self.__getNextProjectionDecalAnchor(currentAnchor, slotData.item.formfactor, reverse)
        self._selectedAnchor = C11nId(areaId, slotType, nextAnchor.regionIdx)
        slotData.component.slotId = nextAnchor.slotId
        outfit.invalidate()
        self.refreshOutfit()
        self.itemDataChanged(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, nextAnchor.regionIdx, changeAnchor=True, updatePropertiesSheet=True)

    def __getNextProjectionDecalAnchor(self, anchor, formfactor, reverse):
        parent = anchor if anchor.isParent else g_currentVehicle.item.getAnchorById(anchor.parentSlotId)
        availableAnchors = parent.getChilds(formfactor)
        currentIdx = availableAnchors.index(anchor.slotId)
        nextIdx = currentIdx - 1 if reverse else currentIdx + 1
        nextAnchorId = availableAnchors[nextIdx % len(availableAnchors)]
        nextAnchor = g_currentVehicle.item.getAnchorById(nextAnchorId)
        return nextAnchor

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
            self._autoRentEnabled = True
            self.itemDataChanged(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
            self.onProlongStyleRent()
        return

    @process('customizationApply')
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
            if self.__prolongStyleRent:
                if self._modifiedStyle.boundInventoryCount.get(g_currentVehicle.item.intCD, 0) > 0 or self._originalStyle and self._modifiedStyle.id == self._originalStyle.id:
                    self.service.buyItems(self._modifiedStyle, 1, g_currentVehicle.item)
                self.__prolongStyleRent = False
            result = yield StyleApplier(g_currentVehicle.item, self._modifiedStyle).request()
            results.append(result)
        if self._autoRentEnabled != g_currentVehicle.item.isAutoRentStyle:
            yield VehicleAutoStyleEquipProcessor(g_currentVehicle.item, self._autoRentEnabled).request()
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
        if self.hangarSpace.spaceInited:
            self._c11CameraManager = C11nHangarCameraManager(self.hangarSpace.space.getCameraManager())
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
        self._autoRentEnabled = g_currentVehicle.item.isAutoRentStyle
        self.carveUpOutfits()
        self.refreshOutfit()

    def checkSlotsFillingForSeason(self, season):
        checkedSlotTypes = (TABS_ITEM_MAPPING[tabId] for tabId in self.visibleTabs)
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
                    vehicle = g_currentVehicle.item
                    availableRegions = len([ anchor for anchor in vehicle.getAnchors(slotType, areaId).itervalues() if anchor.isParent ])
                    maxRegions = QUANTITY_LIMITED_CUSTOMIZATION_TYPES[slotType]
                    regionsIndexes = tuple(range(min(availableRegions, maxRegions)))
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
            if self.numberEditModeActive and self.isOnly1ChangedNumberInEditMode() and self._numberIsEmpty:
                return False
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

    def isAnchorSelected(self, slotType, areaId, regionIdx):
        return self._selectedAnchor.slotType == slotType and self._selectedAnchor.areaId == areaId and self._selectedAnchor.regionIdx == regionIdx

    def isAnyAnchorSelected(self):
        return self._selectedAnchor.areaId != -1 and self._selectedAnchor.regionIdx != -1

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
                        item = multySlot.getItem(slotId.regionIdx)
                        return item is not None
            return False
            return

    def getFilledProjectionDecalSlotRegion(self, regionIdx, season):
        slotType, areaId = GUI_ITEM_TYPE.PROJECTION_DECAL, Area.MISC
        slot = g_currentVehicle.item.getAnchorBySlotId(slotType, areaId, regionIdx)
        outfit = self._modifiedOutfits[season]
        multySlot = outfit.getContainer(areaId).slotFor(slotType)
        for region in range(multySlot.capacity()):
            component = multySlot.getComponent(region)
            if component is not None:
                itemSlot = g_currentVehicle.item.getAnchorById(component.slotId)
                if (itemSlot.parentSlotId or itemSlot.slotId) == (slot.parentSlotId or slot.slotId):
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
        slotType = TABS_ITEM_MAPPING[self._tabIndex]
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
        outfit = self.currentOutfit
        slot = self.selectedSlot
        if slot.slotType == GUI_ITEM_TYPE.STYLE:
            return self._modifiedStyle
        else:
            container = outfit.getContainer(slot.areaId)
            return container.slotFor(slot.slotType).getItem(slot.regionIdx) if container else None

    def itemDataChanged(self, areaId, slotType, regionIdx, changeAnchor=False, updatePropertiesSheet=False, refreshCarousel=True):
        self.onCustomizationItemDataChanged(areaId, slotType, regionIdx, changeAnchor, updatePropertiesSheet, refreshCarousel)

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

    def updateVisibleTabsList(self, visibleTabs):
        for seasonType in SeasonType.COMMON_SEASONS:
            self.__visibleTabs[seasonType] = sorted(list(visibleTabs[seasonType]), key=lambda it: TYPES_ORDER.index(TABS_ITEM_MAPPING[it]))

        if self._mode == C11nMode.STYLE:
            tabIndex = C11nTabs.STYLE
            self._lastTab = first(self.visibleTabs, -1)
        else:
            tabIndex = first(self.visibleTabs, -1)
            self._lastTab = tabIndex
        self.tabChanged(tabIndex, update=True)

    def __getComponent(self, item, selectedAnchor):
        component = emptyComponent(item.itemTypeID)
        if selectedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            component.id = item.id
            anchor = g_currentVehicle.item.getAnchorBySlotId(selectedAnchor.slotType, selectedAnchor.areaId, selectedAnchor.regionIdx)
            if anchor is None:
                _logger.warning('Wrong slotId in ProjectDecalComponent (slotId=%(slotId)d component=%(component)s)', {'slotId': component.slotId,
                 'component': component})
                return
            component.slotId = anchor.slotId
            component.scaleFactorId = DEFAULT_SCALE_FACTOR_ID
            if item.canBeMirrored and item.direction != ProjectionDecalDirectionTags.ANY and anchor.direction != ProjectionDecalDirectionTags.ANY and item.direction != anchor.direction:
                component.options |= Options.MIRRORED
            return component
        else:
            return component

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
