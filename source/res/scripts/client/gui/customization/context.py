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
from items.components.c11n_constants import ApplyArea, SeasonType, DEFAULT_SCALE_FACTOR_ID
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from gui.customization.shared import getAppliedRegionsForCurrentHangarVehicle, C11nId, getVehicleProjectionDecalSlotParams, appliedToFromSlotsIds, QUANTITY_LIMITED_CUSTOMIZATION_TYPES
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
_logger = logging.getLogger(__name__)
CaruselItemData = namedtuple('CaruselItemData', ('index', 'intCD'))
CaruselItemData = partial(CaruselItemData, index=-1, intCD=-1)

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
        self.onCustomizationSeasonChanged = Event.Event(self._eventsManager)
        self.onCustomizationModeChanged = Event.Event(self._eventsManager)
        self.onCustomizationTabChanged = Event.Event(self._eventsManager)
        self.onCustomizationItemInstalled = Event.Event(self._eventsManager)
        self.onCustomizationItemsRemoved = Event.Event(self._eventsManager)
        self.onCustomizationCamouflageColorChanged = Event.Event(self._eventsManager)
        self.onCustomizationCamouflageScaleChanged = Event.Event(self._eventsManager)
        self.onCustomizationProjectionDecalScaleChanged = Event.Event(self._eventsManager)
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
        return

    def changeSeason(self, seasonType):
        self._currentSeason = seasonType
        self.refreshOutfit()
        self.onCustomizationSeasonChanged(self._currentSeason)

    def changeAutoRent(self):
        self._autoRentEnabled = not self._autoRentEnabled
        self.itemDataChanged(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)

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

    def tabChanged(self, tabIndex):
        self._tabIndex = tabIndex
        if self._tabIndex == C11nTabs.EFFECT:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.MODIFICATION, regionIdx=0)
        elif self._tabIndex == C11nTabs.STYLE:
            self._selectedAnchor = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
        else:
            self._selectedAnchor = C11nId()
        self._selectedCaruselItem = CaruselItemData()
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
                outfit = self._modifiedOutfits[self._currentSeason]
                slotId = self.__getFreeSlot(self._selectedAnchor, outfit)
                if slotId is None or not self.__isItemInstalledInOutfitSlot(slotId, self._selectedCaruselItem.intCD):
                    item = self.service.getItemByCD(self._selectedCaruselItem.intCD)
                    component = self.__getComponent(item.id, self.selectedAnchor)
                    if self.installItem(self._selectedCaruselItem.intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason], component):
                        return True
            return False

    def getSlotIdByAnchorId(self, anchorId):
        if anchorId.slotType != GUI_ITEM_TYPE.PROJECTION_DECAL:
            return anchorId
        else:
            outfit = self._modifiedOutfits[self.currentSeason]
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

    def installItem(self, intCD, slotId, seasonIdx, component=None):
        if slotId is None:
            return False
        else:
            item = self.service.getItemByCD(intCD)
            inventoryCount = self.getItemInventoryCount(item)
            if item.isHidden and not inventoryCount:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_PROHIBITED, type=SystemMessages.SM_TYPE.Warning, itemName=item.userName)
                return False
            if slotId.slotType == GUI_ITEM_TYPE.STYLE:
                self._modifiedStyle = item
            else:
                season = SEASON_IDX_TO_TYPE.get(seasonIdx, self._currentSeason)
                outfit = self._modifiedOutfits[season]
                outfit.getContainer(slotId.areaId).slotFor(slotId.slotType).set(item, idx=slotId.regionIdx, component=component)
                outfit.invalidate()
            self.refreshOutfit()
            buyLimitReached = self.isBuyLimitReached(item)
            self.onCustomizationItemInstalled(item, slotId, buyLimitReached)
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

    def installItemForAllSeasons(self, areaID, slotType, regionIdx, currentSlotData):
        additionalyApplyedItems = 0
        for season in SeasonType.COMMON_SEASONS:
            slotData = self.getModifiedOutfit(season).getContainer(areaID).slotFor(slotType).getSlotData(regionIdx)
            df = currentSlotData.weakDiff(slotData)
            if slotData.item is None or df.item is not None:
                seasonIdx = SEASON_TYPE_TO_IDX[season]
                self.installItem(currentSlotData.item.intCD, C11nId(areaId=areaID, slotType=slotType, regionIdx=regionIdx), seasonIdx)
                additionalyApplyedItems += 1

        return additionalyApplyedItems

    def removeItemFromSlot(self, season, slotId, refresh=True):
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
                self.removeItemFromSlot(season, slotId)

    def removeItemForAllSeasons(self, areaId, slotType, regionIdx):
        slotId = C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx)
        for season in SeasonType.COMMON_SEASONS:
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
        self._mode = C11nMode.CUSTOM
        self.refreshOutfit()
        self.tabChanged(self._lastTab)
        self.onCustomizationModeChanged(self._mode)

    def switchToStyle(self):
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
        self.onChangesCanceled()

    def caruselItemSelected(self, index, intCD):
        prevItemSelected = self.isCaruselItemSelected()
        self._selectedCaruselItem = CaruselItemData(index=index, intCD=intCD)
        itemSelected = self.isCaruselItemSelected()
        if self.isAnyAnchorSelected() and itemSelected and not prevItemSelected:
            slotId = self.__getFreeSlot(self.selectedAnchor, self._modifiedOutfits[self.currentSeason])
            if slotId is None:
                return False
            item = self.service.getItemByCD(self._selectedCaruselItem.intCD)
            component = self.__getComponent(item.id, self.selectedAnchor)
            self.installItem(self._selectedCaruselItem.intCD, slotId, SEASON_TYPE_TO_IDX[self.currentSeason], component)
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

    def changeCamouflageColor(self, areaId, regionIdx, paletteIdx):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.palette != paletteIdx:
            component.palette = paletteIdx
            self.refreshOutfit()
            self.onCustomizationCamouflageColorChanged(areaId, regionIdx, paletteIdx)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.CAMOUFLAGE, regionIdx)

    def changeCamouflageScale(self, areaId, regionIdx, scale):
        component = self.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).getComponent(regionIdx)
        if component.patternSize != scale:
            component.patternSize = scale
            self.refreshOutfit()
            self.onCustomizationCamouflageScaleChanged(areaId, regionIdx, scale)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.CAMOUFLAGE, regionIdx)

    def changeProjectionDecalScale(self, areaId, regionIdx, scale):
        slotId = self.getSlotIdByAnchorId(C11nId(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx))
        slot = self.currentOutfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
        component = slot.getComponent(slotId.regionIdx)
        if component.scaleFactorId != scale:
            component.scaleFactorId = scale
            self.refreshOutfit()
            self.onCustomizationProjectionDecalScaleChanged(areaId, regionIdx, scale)
            self.itemDataChanged(areaId, GUI_ITEM_TYPE.PROJECTION_DECAL, regionIdx)

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
        self._eventsManager.clear()
        self.settingsCore.interfaceScale.onScaleExactlyChanged -= self.__onInterfaceScaleChanged
        if self._c11CameraManager is not None:
            self._c11CameraManager.fini()
        self._c11CameraManager = None
        self._vehicleAnchorsUpdater.stopUpdater()
        self._vehicleAnchorsUpdater = None
        return

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
                    return self._modifiedStyle.intCD != currentStyle.intCD or self._autoRentEnabled != g_currentVehicle.item.isAutoRentStyle
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
                multySlot = outfit.getContainer(slotId.areaId).slotFor(slotId.slotType)
                if multySlot is not None:
                    item = multySlot.getItem(slotId.regionIdx)
                    return item is not None
            return False
            return

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
        fullCount = item.buyCount + item.inventoryCount
        isSpecial = item.isLimited or item.isHidden
        return isSpecial and inventoryCount == 0 and (item.buyCount == 0 or appliedCount >= fullCount)

    def getPurchaseLimit(self, item):
        appliedCount = getItemAppliedCount(item, self.getOutfitsInfo())
        purchaseLimit = item.buyCount - max(appliedCount - item.inventoryCount, 0)
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
        return outfit.getContainer(slot.areaId).slotFor(slot.slotType).getItem(slot.regionIdx)

    def itemDataChanged(self, areaId, slotType, regionIdx):
        self.onCustomizationItemDataChanged(areaId, slotType, regionIdx)

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
        self.tabChanged(tabIndex)

    def __getComponent(self, itemId, selectedAnchor):
        if selectedAnchor.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            component = emptyComponent(selectedAnchor.slotType)
            component.id = itemId
            anchorParams = self.service.getAnchorParams(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
            if anchorParams is None:
                return
            component.slotId = anchorParams.vehicleSlotId
            component.scaleFactorId = DEFAULT_SCALE_FACTOR_ID
            slotParams = getVehicleProjectionDecalSlotParams(g_currentVehicle.item.descriptor, component.slotId)
            if slotParams is None:
                _logger.warning('Wrong slotId in ProjectDecalComponent (slotId=%(slotId)d component=%(component)s)', {'slotId': component.slotId,
                 'component': component})
                return
            component.position = slotParams.position
            component.rotation = slotParams.rotation
            component.scale = slotParams.scale
            component.showOn = slotParams.showOn
            return component
        else:
            return

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

    def __getFreeSlot(self, anchorId, outfit):
        slotId = self.getSlotIdByAnchorId(anchorId)
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
