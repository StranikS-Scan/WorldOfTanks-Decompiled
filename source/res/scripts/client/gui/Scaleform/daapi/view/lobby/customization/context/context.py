# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/context.py
import logging
import typing
import Event
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
import adisp
from gui import g_tankActiveCamouflage
from gui.Scaleform.daapi.view.lobby.customization.context.custom_mode import CustomMode
from gui.Scaleform.daapi.view.lobby.customization.context.editable_style_mode import EditableStyleMode
from gui.Scaleform.daapi.view.lobby.customization.context.styled_diffs_cache import StyleDiffsCache
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, resetC11nItemsNovelty, getCommonPurchaseItems, vehicleHasSlot, remove3DStyleIncompatibleCommonItems
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchors_updater import VehicleAnchorsUpdater
from gui.customization.constants import CustomizationModes
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.decorators import adisp_process
from functools import partial
from helpers import dependency
from items.components.c11n_constants import SeasonType
from shared_utils import first, nextTick
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from soft_exception import SoftException
from vehicle_outfit.outfit import Area
if typing.TYPE_CHECKING:
    from gui.customization.shared import C11nId, PurchaseItem
    from gui.customization.constants import CustomizationModeSource
_logger = logging.getLogger(__name__)

class _CustomizationEvents(object):

    def __init__(self):
        self._eventsManager = Event.EventManager()
        self.onBeforeModeChange = Event.Event(self._eventsManager)
        self.onModeChanged = Event.Event(self._eventsManager)
        self.onTabChanged = Event.Event(self._eventsManager)
        self.onSeasonChanged = Event.Event(self._eventsManager)
        self.onCacheResync = Event.Event(self._eventsManager)
        self.onSlotSelected = Event.Event(self._eventsManager)
        self.onSlotUnselected = Event.Event(self._eventsManager)
        self.onItemSelected = Event.Event(self._eventsManager)
        self.onItemUnselected = Event.Event(self._eventsManager)
        self.onItemInstalled = Event.Event(self._eventsManager)
        self.onItemsRemoved = Event.Event(self._eventsManager)
        self.onComponentChanged = Event.Event(self._eventsManager)
        self.onItemsBought = Event.Event(self._eventsManager)
        self.onItemSold = Event.Event(self._eventsManager)
        self.onItemLimitReached = Event.Event(self._eventsManager)
        self.onChangesCanceled = Event.Event(self._eventsManager)
        self.onCarouselFiltered = Event.Event(self._eventsManager)
        self.onFilterPopoverClosed = Event.Event(self._eventsManager)
        self.onPropertySheetShown = Event.Event(self._eventsManager)
        self.onPropertySheetHidden = Event.Event(self._eventsManager)
        self.onAnchorHovered = Event.Event(self._eventsManager)
        self.onAnchorUnhovered = Event.Event(self._eventsManager)
        self.onAnchorsStateChanged = Event.Event(self._eventsManager)
        self.onGetItemBackToHand = Event.Event(self._eventsManager)
        self.onUpdateSwitchers = Event.Event(self._eventsManager)
        self.onInstallNextCarouselItem = Event.Event(self._eventsManager)
        self.onShowStyleInfo = Event.Event(self._eventsManager)
        self.onHideStyleInfo = Event.Event(self._eventsManager)
        self.onUpdateStyleInfoDOF = Event.Event(self._eventsManager)
        self.onEditModeEnabled = Event.Event(self._eventsManager)
        self.onPersonalNumberCleared = Event.Event(self._eventsManager)
        self.onProlongStyleRent = Event.Event(self._eventsManager)
        self.onCloseDialogShown = Event.Event(self._eventsManager)
        self.onCloseDialogClosed = Event.Event(self._eventsManager)

    def fini(self):
        self._eventsManager.clear()


class CustomizationContext(object):
    _service = dependency.descriptor(ICustomizationService)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self._vehicle = None
        self.__season = None
        self.__modeId = None
        self.__styleModeId = None
        self.__modes = {CustomizationModes.CUSTOM: CustomMode(self),
         CustomizationModes.STYLE_2D: StyledMode(self, is3DMode=False),
         CustomizationModes.STYLE_3D: StyledMode(self, is3DMode=True),
         CustomizationModes.STYLE_2D_EDITABLE: EditableStyleMode(self)}
        self.__events = None
        self.__isItemsOnAnotherVeh = False
        self.__isProgressiveItemsExist = False
        self.__isModeChangeInProgress = False
        self.__vehicleAnchorsUpdater = VehicleAnchorsUpdater(self)
        self.__c11nCameraManager = C11nHangarCameraManager()
        self.__stylesDiffsCache = StyleDiffsCache()
        self.__commonOriginalOutfit = None
        self.__commonOriginal3DOutfit = None
        self.__commonModifiedOutfit = None
        self.__commonOutfitStyleId = None
        self.__commonOutfitDiff = None
        self.updateCommonOutfits()
        self.__carouselItems = None
        self.__initialItemCD = None
        self.__applyingItems = False
        return

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def isItemsOnAnotherVeh(self):
        return self.__isItemsOnAnotherVeh

    @property
    def isProgressiveItemsExist(self):
        return self.__isProgressiveItemsExist

    def setIsProgressiveItemsExist(self, value):
        self.__isProgressiveItemsExist = value

    @property
    def carouselItems(self):
        return self.__carouselItems

    def setCarouselItems(self, carouselItems):
        self.__carouselItems = carouselItems

    @property
    def events(self):
        return self.__events

    @property
    def season(self):
        return self.__season

    @property
    def modeId(self):
        return self.__modeId

    @property
    def mode(self):
        return self.__modes[self.modeId]

    @property
    def styleMode(self):
        return self.__modes[self.__styleModeId]

    @property
    def vehicleAnchorsUpdater(self):
        return self.__vehicleAnchorsUpdater

    @property
    def c11nCameraManager(self):
        return self.__c11nCameraManager

    @property
    def stylesDiffsCache(self):
        return self.__stylesDiffsCache

    @property
    def commonOriginalOutfit(self):
        if not self.__commonOriginalOutfit:
            self.updateCommonOutfits()
        return self.__commonOriginal3DOutfit if self.isInStyleMode(CustomizationModes.STYLE_3D) else self.__commonOriginalOutfit

    @property
    def commonModifiedOutfit(self):
        if not self.__commonModifiedOutfit:
            self.updateCommonOutfits()
        if self.__styleModeId and self.styleMode.modifiedStyle:
            currentStyleId = self.styleMode.modifiedStyle.id
        else:
            currentStyleId = 0
        if self.__commonOutfitStyleId == currentStyleId:
            return self.__commonModifiedOutfit
        else:
            if self.__commonOutfitDiff:
                self.__commonModifiedOutfit = self.__commonModifiedOutfit.adjust(self.__commonOutfitDiff)
                self.__commonOutfitDiff = None
            if self.isInStyleMode(CustomizationModes.STYLE_3D):
                newOutfit = self.__commonModifiedOutfit.copy()
                remove3DStyleIncompatibleCommonItems(newOutfit, self.styleMode.modifiedStyle)
                newOutfit.invalidate()
                self.__commonOutfitDiff = newOutfit.diff(self.__commonModifiedOutfit)
                self.__commonModifiedOutfit = newOutfit
            self.__commonOutfitStyleId = currentStyleId
            return self.__commonModifiedOutfit

    @property
    def isModeChangeInProgress(self):
        return self.__isModeChangeInProgress

    @property
    def applyingItems(self):
        return self.__applyingItems

    def setIsItemsOnAnotherVeh(self, value):
        self.__isItemsOnAnotherVeh = value

    def init(self, season=None, modeId=None, tabId=None, itemCD=None):
        if not g_currentVehicle.isPresent():
            raise SoftException('There is no vehicle in hangar for customization.')
        self._vehicle = g_currentVehicle.item
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._service.onOutfitChanged += self.__onOutfitChanged
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.__season = season or self.__getStartSeason()
        self.__modeId = self.__getStartMode(modeId, tabId)
        if self.__modeId in CustomizationModes.BASE_STYLES:
            self.__styleModeId = self.__modeId
        self.mode.start(tabId)
        self.__events = _CustomizationEvents()
        self.__vehicleAnchorsUpdater.startUpdater()
        self.__c11nCameraManager.init()
        if itemCD is not None:
            if g_currentPreviewVehicle.isPresent():
                g_currentPreviewVehicle.selectNoVehicle()
                g_currentPreviewVehicle.onChanged += self.__onPreviewVehicleChanged
                self.__initialItemCD = itemCD
            else:
                self.selectItem(itemCD)
        return

    def fini(self):
        self.__stylesDiffsCache.fini()
        self.__stylesDiffsCache = None
        self.__c11nCameraManager.fini()
        self.__c11nCameraManager = None
        self.__vehicleAnchorsUpdater.stopUpdater()
        self.__vehicleAnchorsUpdater = None
        self.__commonOriginalOutfit = None
        self.__commonOriginal3DOutfit = None
        self.__commonModifiedOutfit = None
        self.__commonOutfitStyleId = None
        self.__commonOutfitDiff = None
        self.__events.fini()
        self.__events = None
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self._service.onOutfitChanged -= self.__onOutfitChanged
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        g_currentPreviewVehicle.onChanged -= self.__onPreviewVehicleChanged
        for mode in self.__modes.itervalues():
            mode.fini()

        self.__modes.clear()
        return

    def changeMode(self, modeId, tabId=None, source=None):
        if modeId not in CustomizationModes.ALL:
            _logger.warning('Wrong customization mode: %s', modeId)
            return
        elif self.__modeId == modeId:
            return
        else:
            self.__isModeChangeInProgress = True
            prevMode = self.mode
            prevModeId = self.__modeId
            prevMode.unselectItem()
            prevMode.unselectSlot()
            prevMode.stop()
            self.__modeId = modeId
            if self.__modeId not in CustomizationModes.STYLES:
                self.__styleModeId = None
            elif self.__modeId in CustomizationModes.BASE_STYLES:
                self.__styleModeId = self.__modeId
            if prevModeId != CustomizationModes.STYLE_2D_EDITABLE and modeId != CustomizationModes.STYLE_2D_EDITABLE:
                self.__commonOutfitStyleId = None
            newMode = self.__modes[modeId]
            newMode.start(tabId=tabId, source=source)
            self.refreshOutfit()
            self.events.onBeforeModeChange()
            self.events.onModeChanged(modeId, prevModeId)
            self.__isModeChangeInProgress = False
            self.events.onTabChanged(self.mode.tabId)
            return

    def editStyle(self, intCD, source=None):
        style = self._service.getItemByCD(intCD)
        if style is None:
            _logger.error('Invalid style intCD: %s', intCD)
            return
        elif not style.isEditable:
            _logger.error('Failed to start Editable Style Mode: style is not editable: %s', style)
            return
        else:
            self.changeMode(CustomizationModes.STYLE_3D if style.is3D else CustomizationModes.STYLE_2D, source=source)
            currentStyleItem = self.mode.currentOutfit.style
            currentStyleIntCD = currentStyleItem.compactDescr if currentStyleItem else None
            if currentStyleIntCD != intCD:
                self.mode.installItem(intCD, StyledMode.STYLE_SLOT)
            self.changeMode(CustomizationModes.STYLE_2D_EDITABLE, source=source)
            return

    def canEditStyle(self, itemCD):
        if self.__modeId in CustomizationModes.STYLES:
            outfit = self.mode.getModifiedOutfit()
            if outfit is not None and outfit.style is not None:
                currentStyle = self._itemsCache.items.getItemByCD(outfit.style.compactDescr)
                item = self._itemsCache.items.getItemByCD(itemCD)
                isCurrentLevelEditable = True
                if outfit.progressionLevel != currentStyle.getProgressionLevel():
                    isCurrentLevelEditable = currentStyle.isProgressionPurchasable(outfit.progressionLevel)
                return currentStyle.isEditable and isCurrentLevelEditable and currentStyle.isItemInstallable(item)
        return False

    def changeModeWithProgressionDecal(self, itemCD, scrollToItem=False):
        goToEditableStyle = self.canEditStyle(itemCD)
        self.changeMode(CustomizationModes.STYLE_2D_EDITABLE if goToEditableStyle else CustomizationModes.CUSTOM)
        self.mode.changeTab(CustomizationTabs.PROJECTION_DECALS, itemCD=itemCD if scrollToItem else None)
        return

    def changeSeason(self, season):
        if season not in SeasonType.COMMON_SEASONS:
            _logger.warning('Wrong season: %s', season)
            return
        oldSeason = self.__season
        self.__season = season
        self.removeOldSeasonPreview(oldSeason)
        self.refreshOutfit()
        self.events.onSeasonChanged(season)

    def selectSlot(self, slotId):
        self.mode.selectSlot(slotId)

    def unselectSlot(self):
        self.mode.unselectSlot()

    def selectItem(self, intCD, progressionLevel=-1):
        self.mode.selectItem(intCD, progressionLevel)

    def unselectItem(self):
        self.mode.unselectItem()

    def cancelChanges(self):
        self.__commonModifiedOutfit = self.commonOriginalOutfit.copy()
        if self.isInStyleMode(CustomizationModes.STYLE_3D) and self.__commonOutfitDiff:
            for slotType in GUI_ITEM_TYPE.COMMON_C11N_COMPATIBLE_WITH_3D_STYLES:
                for partIdx in Area.ALL:
                    multiSlot = self.__commonOutfitDiff.getContainer(partIdx).slotFor(slotType)
                    if multiSlot:
                        for idx in range(multiSlot.capacity()):
                            slotData = multiSlot.getSlotData(idx)
                            if not slotData.isEmpty():
                                multiSlot.remove(idx)

        self.mode.cancelChanges()

    def removeOldSeasonPreview(self, season):
        outfit = self.mode.getModifiedOutfit(season)
        outfit.removePreview()

    def getPurchaseItems(self):
        return self.mode.getPurchaseItems() + getCommonPurchaseItems(self.commonModifiedOutfit)

    def getNotModifedCommonItems(self):
        commonOutfit = self.commonOriginalOutfit
        commonModifiedOutfit = self.commonModifiedOutfit
        df = commonModifiedOutfit.diff(commonOutfit)
        notModifiedItems = df.diff(commonOutfit)
        return notModifiedItems

    def updateCommonOutfits(self):
        outfit = self._service.getCommonOutfit()
        self.__commonOriginalOutfit = outfit.copy()
        self.__commonOriginal3DOutfit = outfit.copy()
        remove3DStyleIncompatibleCommonItems(self.__commonOriginal3DOutfit, self.styleMode.originalStyle if self.isInStyleMode(CustomizationModes.STYLE_3D) else None)
        self.__commonOriginal3DOutfit.invalidate()
        self.__commonModifiedOutfit = outfit.copy()
        self.__commonOutfitStyleId = None
        self.__commonOutfitDiff = None
        return

    def updateOutfits(self):
        self.updateCommonOutfits()
        for mode in self.__modes.itervalues():
            if mode.isInited:
                mode.updateOutfits()

    def refreshOutfit(self, season=None):
        season = self.season if season == SeasonType.ALL or season is None else season
        outfit = self.mode.getModifiedOutfit(season)
        if season is not None and season != self.season:
            outfit.invalidateItemsCounter()
        else:
            outfit.invalidate()
            self._service.tryOnOutfit(outfit.adjust(self.commonModifiedOutfit))
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self.season
        return

    @adisp.adisp_async
    @adisp_process('customizationApply')
    def applyItems(self, purchaseItems, callback):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.__applyingItems = True
        yield self.mode.applyItems(purchaseItems)
        self.__applyingItems = False
        self.__onCacheResync(-1, {})
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        callback(None)
        return

    def isCommonOutfitModified(self):
        modifiedOutfit = self.commonModifiedOutfit
        originalOutfit = self.commonOriginalOutfit
        for _, component, _, _, _ in originalOutfit.diff(modifiedOutfit).itemsFull():
            if component.isFilled():
                return True

        for _, component, _, _, _ in modifiedOutfit.diff(originalOutfit).itemsFull():
            if component.isFilled():
                return True

        return False

    def isOutfitsModified(self):
        if self.mode.isOutfitsModified():
            return True
        return True if self.isCommonOutfitModified() else False

    @staticmethod
    def resetItemsNovelty(items):
        items = [ (g_currentVehicle.item.intCD, intCD) for intCD in items ]
        resetC11nItemsNovelty(items=items)

    def returnToStyleMode(self, source=None):
        if self.__styleModeId is None:
            _logger.error('There is no previously open style mode to return to, source: %s', source)
            return
        else:
            self.changeMode(self.__styleModeId, source=source)
            return

    def hasCommonItems(self):
        for intCD in self.commonModifiedOutfit.items():
            item = self._service.getItemByCD(intCD)
            if not item.isHiddenInUI() and item.itemTypeID in GUI_ITEM_TYPE.COMMON_C11NS:
                return True

        return False

    def isInStyleMode(self, styleModeId):
        return self.__styleModeId is not None and self.__styleModeId == styleModeId

    def __onCacheResync(self, reason, items):
        if self.events:
            self.events.onCacheResync(reason, items)

    def __onVehicleChanged(self):
        if self._vehicle is None or not g_currentVehicle.isPresent():
            _logger.error('There is no vehicle in hangar for customization.')
            return
        else:
            if self._vehicle != g_currentVehicle.item:
                self._vehicle = g_currentVehicle.item
                self.stylesDiffsCache.clearDiffs()
                self.updateOutfits()
                self.refreshOutfit()
            return

    def __onPreviewVehicleChanged(self):
        nextTick(partial(self.selectItem, self.__initialItemCD))()
        self.__initialItemCD = None
        g_currentPreviewVehicle.onChanged -= self.__onPreviewVehicleChanged
        return

    def __onVehicleChangeStarted(self):
        if self._vehicle is None or not g_currentVehicle.isPresent():
            _logger.error('There is no vehicle in hangar for customization.')
            return
        elif self._vehicle.intCD == g_currentVehicle.item.intCD:
            return
        else:
            for mode in self.__modes.itervalues():
                if mode.isInited:
                    mode.onVehicleChangeStarted()

            return

    def __onOutfitChanged(self):
        self.refreshOutfit()

    def __getStartSeason(self):
        return g_tankActiveCamouflage[g_currentVehicle.item.intCD] if g_currentVehicle.item.intCD in g_tankActiveCamouflage else first(SeasonType.COMMON_SEASONS)

    def __getStartMode(self, modeId=None, tabId=None):
        if modeId is not None:
            if modeId == CustomizationModes.STYLE_2D_EDITABLE:
                _logger.error('Cannot enter editable style mode without entering a base style mode first.')
                return self.__getDefaultStartMode()
            if modeId in CustomizationModes.BASE_STYLES and not vehicleHasSlot(GUI_ITEM_TYPE.STYLE):
                _logger.warning("Tried entering {} customization mode but the vehicle doesn't have a slot for a style.").format(modeId)
                return CustomizationModes.CUSTOM
            return modeId
        elif tabId is not None:
            modeId = self.__getDefaultStartMode()
            if tabId not in CustomizationTabs.MODES[modeId]:
                modeId = CustomizationTabs.TAB_TO_MODE[tabId]
            if modeId in CustomizationModes.BASE_STYLES and not vehicleHasSlot(GUI_ITEM_TYPE.STYLE):
                return CustomizationModes.CUSTOM
            return modeId
        else:
            return self.__getDefaultStartMode()

    def __getDefaultStartMode(self):
        style = self._service.getCurrentStyle()
        if style and style.is3D:
            return CustomizationModes.STYLE_3D
        return CustomizationModes.STYLE_2D if style and not style.is3D or self._service.isNationalOutfitInstalled() else CustomizationModes.CUSTOM
