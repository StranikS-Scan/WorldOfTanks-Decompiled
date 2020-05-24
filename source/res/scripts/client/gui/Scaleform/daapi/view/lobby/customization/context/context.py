# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/context/context.py
import logging
import typing
import Event
from CurrentVehicle import g_currentVehicle
from gui import g_tankActiveCamouflage
from gui.Scaleform.daapi.view.lobby.customization.context.custom_mode import CustomMode
from gui.Scaleform.daapi.view.lobby.customization.context.editable_style_mode import EditableStyleMode
from gui.Scaleform.daapi.view.lobby.customization.context.styled_diffs_cache import StyleDiffsCache
from gui.Scaleform.daapi.view.lobby.customization.context.styled_mode import StyledMode
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.Scaleform.daapi.view.lobby.customization.vehicle_anchors_updater import VehicleAnchorsUpdater
from gui.customization.constants import CustomizationModes
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nHangarCameraManager
from helpers import dependency
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.customization.shared import C11nId, PurchaseItem
    from gui.customization.constants import CustomizationModeSource
_logger = logging.getLogger(__name__)

class _CustomizationEvents(object):

    def __init__(self):
        self._eventsManager = Event.EventManager()
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
        self.onResetItemsNovelty = Event.Event(self._eventsManager)
        self.onInstallNextCarouselItem = Event.Event(self._eventsManager)
        self.onShowStyleInfo = Event.Event(self._eventsManager)
        self.onHideStyleInfo = Event.Event(self._eventsManager)
        self.onUpdateStyleInfoDOF = Event.Event(self._eventsManager)
        self.onEditModeEnabled = Event.Event(self._eventsManager)
        self.onPersonalNumberCleared = Event.Event(self._eventsManager)
        self.onProlongStyleRent = Event.Event(self._eventsManager)

    def fini(self):
        self._eventsManager.clear()


class CustomizationContext(object):
    _service = dependency.descriptor(ICustomizationService)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__season = None
        self.__modeId = None
        self.__startMode = None
        self.__modes = {CustomizationModes.CUSTOM: CustomMode(self),
         CustomizationModes.STYLED: StyledMode(self),
         CustomizationModes.EDITABLE_STYLE: EditableStyleMode(self)}
        self.__events = None
        self.__isItemsOnAnotherVeh = False
        self.__isProgressiveItemsExist = False
        self.__vehicleAnchorsUpdater = VehicleAnchorsUpdater(self)
        self.__c11nCameraManager = C11nHangarCameraManager()
        self.__stylesDiffsCache = StyleDiffsCache()
        self.__carouselItems = None
        return

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
    def vehicleAnchorsUpdater(self):
        return self.__vehicleAnchorsUpdater

    @property
    def c11nCameraManager(self):
        return self.__c11nCameraManager

    @property
    def stylesDiffsCache(self):
        return self.__stylesDiffsCache

    def setIsItemsOnAnotherVeh(self, value):
        self.__isItemsOnAnotherVeh = value

    def init(self, season=None, modeId=None, tabId=None):
        if not g_currentVehicle.isPresent():
            raise SoftException('There is no vehicle in hangar for customization.')
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._service.onOutfitChanged += self.__onOutfitChanged
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.__season = season or self.__getStartSeason()
        self.__modeId = modeId or self.__getStartMode()
        self.__startMode = self.modeId
        self.mode.start(tabId)
        self.__events = _CustomizationEvents()
        self.__vehicleAnchorsUpdater.startUpdater()
        self.__c11nCameraManager.init()

    def fini(self):
        self.__stylesDiffsCache.fini()
        self.__stylesDiffsCache = None
        self.__c11nCameraManager.fini()
        self.__c11nCameraManager = None
        self.__vehicleAnchorsUpdater.stopUpdater()
        self.__vehicleAnchorsUpdater = None
        self.__events.fini()
        self.__events = None
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self._service.onOutfitChanged -= self.__onOutfitChanged
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        for mode in self.__modes.itervalues():
            mode.fini()

        self.__modes.clear()
        return

    def changeMode(self, modeId, tabId=None, source=None):
        if modeId not in CustomizationModes.ALL:
            _logger.warning('Wrong customization mode: %s', modeId)
            return
        if self.__modeId == modeId:
            return
        prevMode = self.mode
        prevMode.unselectItem()
        prevMode.unselectSlot()
        prevMode.stop()
        newMode = self.__modes[modeId]
        newMode.start(tabId=tabId, source=source)
        self.__modeId = modeId
        self.refreshOutfit()
        self.events.onModeChanged(modeId, prevMode.modeId)
        self.events.onTabChanged(self.mode.tabId)

    def editStyle(self, intCD, source=None):
        style = self._service.getItemByCD(intCD)
        if style is None:
            _logger.error('Invalid style intCD: %s', intCD)
            return
        elif not style.isEditable:
            _logger.error('Failed to start Editable Style Mode: style is not editable: %s', style)
            return
        else:
            self.changeMode(CustomizationModes.STYLED, source=source)
            currentStyleItem = self.mode.currentOutfit.style
            currentStyleIntCD = currentStyleItem.compactDescr if currentStyleItem else None
            if currentStyleIntCD != intCD:
                self.mode.installItem(intCD, StyledMode.STYLE_SLOT)
            self.changeMode(CustomizationModes.EDITABLE_STYLE, source=source)
            return

    def changeModeWithProgressionDecal(self, itemCD, scrollToItem=False):
        goToEditableStyle = False
        if self.__modeId in (CustomizationModes.STYLED, CustomizationModes.EDITABLE_STYLE):
            outfit = self.mode.getModifiedOutfit()
            if outfit is not None:
                currentStyle = outfit.style
                if currentStyle is not None:
                    item = self._itemsCache.items.getItemByCD(itemCD)
                    goToEditableStyle = currentStyle.isEditable and currentStyle.isItemInstallable(item.descriptor)
        self.changeMode(CustomizationModes.EDITABLE_STYLE if goToEditableStyle else CustomizationModes.CUSTOM)
        self.mode.changeTab(CustomizationTabs.PROJECTION_DECALS, itemCD=itemCD if scrollToItem else None)
        return

    def changeSeason(self, season):
        if season not in SeasonType.COMMON_SEASONS:
            _logger.warning('Wrong season: %s', season)
            return
        self.__season = season
        self.refreshOutfit()
        self.events.onSeasonChanged(season)

    def selectSlot(self, slotId):
        self.mode.selectSlot(slotId)

    def unselectSlot(self):
        self.mode.unselectSlot()

    def selectItem(self, intCD):
        self.mode.selectItem(intCD)

    def unselectItem(self):
        self.mode.unselectItem()

    def refreshOutfit(self, season=None):
        outfit = self.mode.getModifiedOutfit(season)
        if season is not None and season != self.season:
            outfit.invalidateItemsCounter()
        else:
            outfit.invalidate()
            self._service.tryOnOutfit(outfit)
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self.season
        return

    def applyItems(self, purchaseItems):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        isModeChanged = self.modeId != self.__startMode
        self.mode.applyItems(purchaseItems, isModeChanged)
        self.__onCacheResync()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def isOutfitsModified(self):
        if self.modeId != self.__startMode:
            startMode = self.__modes[self.__startMode]
            if not startMode.isOutfitsModified() and startMode.isOutfitsEmpty() and self.mode.isOutfitsEmpty():
                return False
            if startMode.modeId == CustomizationModes.STYLED and self.modeId == CustomizationModes.EDITABLE_STYLE:
                if not startMode.isOutfitsModified() and not self.mode.isOutfitsModified():
                    return startMode.originalStyle != self.mode.style
            return True
        return self.mode.isOutfitsModified()

    def __onCacheResync(self, *_):
        if g_currentVehicle.isPresent():
            for mode in self.__modes.itervalues():
                if mode.isInited:
                    mode.updateOutfits(preserve=True)

            self.refreshOutfit()
        self.events.onCacheResync()

    def __onVehicleChanged(self):
        for mode in self.__modes.itervalues():
            if mode.isInited:
                mode.updateOutfits()

        self.refreshOutfit()

    def __onVehicleChangeStarted(self):
        for mode in self.__modes.itervalues():
            if mode.isInited:
                mode.onVehicleChangeStarted()

    def __onOutfitChanged(self):
        self.refreshOutfit()

    def __getStartSeason(self):
        return g_tankActiveCamouflage[g_currentVehicle.item.intCD] if g_currentVehicle.item.intCD in g_tankActiveCamouflage else first(SeasonType.COMMON_SEASONS)

    def __getStartMode(self):
        return CustomizationModes.STYLED if self._service.isStyleInstalled() else CustomizationModes.CUSTOM
