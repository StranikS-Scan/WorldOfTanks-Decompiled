# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import struct
from collections import namedtuple
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import async, process as adisp_process
from gui import DialogsInterface, g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_ITEM_MAPPING, DRAG_AND_DROP_INACTIVE_TABS, C11nTabs, SEASON_TYPE_TO_NAME, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_IDX, SEASONS_ORDER, getTotalPurchaseInfo
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.app_loader import g_appLoader
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.customization.shared import chooseMode, getAppliedRegionsForCurrentHangarVehicle, appliedToFromSlotsIds, C11nId, QUANTITY_LIMITED_CUSTOMIZATION_TYPES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.formatters import formatPrice
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.functions import makeTooltip
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, ApplyArea
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class _ModalWindowsPopupHandler(IViewLifecycleHandler):
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DIALOGS = (VIEW_ALIAS.SIMPLE_DIALOG, CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG)

    def __init__(self):
        super(_ModalWindowsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DIALOGS ])
        self.__viewStack = []

    def onViewCreated(self, view):
        self.__viewStack.append(view.key)
        self.service.suspendHighlighter()

    def onViewDestroyed(self, _):
        self.__viewStack.pop()
        if not self.__viewStack:
            self.service.resumeHighlighter()


class _C11ViewsPopupHandler(IViewLifecycleHandler):
    __VIEWS = (VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER, VIEW_ALIAS.CUSTOMIZATION_KIT_POPOVER)

    def __init__(self, onViewPopupCallback):
        super(_C11ViewsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__VIEWS ])
        self.__onViewPopupCallback = onViewPopupCallback

    def onViewCreated(self, view):
        self.__onViewPopupCallback()


CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'typeRegions', 'maxItemsReached'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid', 'tooltip'))
CustomizationSlotIdVO = namedtuple('CustomizationSlotIdVO', ('areaId', 'slotId', 'regionId'))
CustomizationAnchorsSetVO = namedtuple('CustomizationAnchorsSetVO', ('rendererList',))
CustomizationAnchorPositionVO = namedtuple('CustomizationAnchorPositionVO', ('zIndex', 'slotId'))
AnchorPositionData = namedtuple('AnchorPositionData', ('angleToCamera', 'clipSpacePos', 'slotId'))
_WAITING_MESSAGE = 'loadHangarSpace'

class _SeasonSoundAnimantion(object):

    def __init__(self, maxFilledSeasonSlots, soundManager):
        self._maxFilledSeasonSlots = maxFilledSeasonSlots
        self._filledSeasonSlots = None
        self._soundManager = soundManager
        return

    def setFilledSeasonSlots(self, filledSeasonSlots, tabChanged):
        if self._filledSeasonSlots is None:
            self._filledSeasonSlots = filledSeasonSlots
            return
        else:
            if tabChanged:
                if filledSeasonSlots == self._maxFilledSeasonSlots:
                    self._soundManager.playInstantSound(SOUNDS.CUST_TICK_ON_ALL)
                elif filledSeasonSlots > self._filledSeasonSlots:
                    self._soundManager.playInstantSound(SOUNDS.CUST_TICK_ON)
                elif filledSeasonSlots < self._filledSeasonSlots:
                    self._soundManager.playInstantSound(SOUNDS.CUST_TICK_OFF)
            elif filledSeasonSlots > self._filledSeasonSlots:
                if filledSeasonSlots - self._filledSeasonSlots == self._maxFilledSeasonSlots:
                    self._soundManager.playInstantSound(SOUNDS.CUST_TICK_ON_ALL)
                else:
                    self._soundManager.playInstantSound(SOUNDS.CUST_TICK_ON)
            elif filledSeasonSlots < self._filledSeasonSlots:
                self._soundManager.playInstantSound(SOUNDS.CUST_TICK_OFF)
            self._filledSeasonSlots = filledSeasonSlots
            return


class MainView(CustomizationMainViewMeta):
    _COMMON_SOUND_SPACE = C11N_SOUND_SPACE
    _ZOOM_ON_EMBLEM = 0.6
    _ZOOM_ON_INSCRIPTION = 0.1
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, _=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.__locatedOnEmbelem = False
        self.itemIsPicked = False
        self.__propertiesSheet = None
        self._seasonSoundAnimantion = None
        self._isPropertySheetShown = False
        self.__ctx = None
        self.__renderEnv = None
        return

    def showBuyWindow(self):
        self.changeVisible(False)
        self.__releaseItemSound()
        self.soundManager.playInstantSound(SOUNDS.SELECT)
        purchaseItems = self.__ctx.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.totalPrice == ITEM_PRICE_EMPTY:
            self.__ctx.applyItems(purchaseItems)
        else:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onPressClearBtn(self):
        self.__ctx.cancelChanges()

    def onPressEscBtn(self):
        tabIndex = self.__ctx.currentTab
        if tabIndex not in C11nTabs.REGIONS and self.__ctx.isAnyAnchorSelected() or self.service.isRegionSelected():
            self.__clearItem()
            if self._isPropertySheetShown:
                self.__hidePropertiesSheet()
            self.as_enableDNDS(True)
        else:
            self.onCloseWindow()

    def onPressSelectNextItem(self):
        self.__installNextCarouselItem(shift=1)

    def onPressSelectPrevItem(self):
        self.__installNextCarouselItem(shift=-1)

    def __installNextCarouselItem(self, shift=1):
        if not self.__ctx.isAnyAnchorSelected() or self.__ctx.isCaruselItemSelected():
            return
        else:
            c11nBottomPanel = self.components[VIEW_ALIAS.CUSTOMIZATION_BOTTOM_PANEL]
            tabIndex = self.__ctx.currentTab
            if tabIndex == C11nTabs.STYLE:
                item = self.__ctx.modifiedStyle
            else:
                item = self.__ctx.getItemFromSelectedRegion()
            if item is not None:
                carouselItems = c11nBottomPanel.carouselItems
                index = carouselItems.index(item.intCD) + shift
                if 0 <= index < len(carouselItems):
                    intCD = carouselItems[index]
                    self.__ctx.caruselItemSelected(index, intCD)
            return

    def changeVisible(self, value):
        _, slotType, _ = self.__ctx.selectedAnchor
        self.__ctx.anchorSelected(slotType, -1, -1)
        self.as_hideS(value)

    def onReleaseItem(self):
        self.__ctx.caruselItemUnselected()
        self.__releaseItemSound()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET:
            self.__propertiesSheet = viewPy

    def changeSeason(self, seasonIdx):
        if seasonIdx in SEASON_IDX_TO_TYPE:
            self.__ctx.changeSeason(SEASON_IDX_TO_TYPE[seasonIdx])
        else:
            _logger.error('Wrong season index %(seasonIdx)d', {'seasonIdx': seasonIdx})
        if self.__ctx.isAnyAnchorSelected():
            self.service.selectRegions(ApplyArea.NONE)
            self.__ctx.anchorSelected(-1, -1, -1)
            tabIndex = self.__ctx.currentTab
            if tabIndex not in C11nTabs.REGIONS:
                self.as_updateSelectedRegionsS(-1)
                self.as_enableDNDS(True)
            self.__resetCameraFocus()
            if self._isPropertySheetShown:
                self.__hidePropertiesSheet()

    def __onSeasonChanged(self, seasonType):
        seasonName = SEASON_TYPE_TO_NAME.get(seasonType)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.__setAnchorsInitData(True)

    def __onTabChanged(self, tabIndex):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.service.stopHighlighter()
        if tabIndex in C11nTabs.REGIONS:
            itemTypeID = TABS_ITEM_MAPPING[tabIndex]
            self.service.startHighlighter(chooseMode(itemTypeID, g_currentVehicle.item))
        self.__setAnchorsInitData()
        if self.__locatedOnEmbelem and self.__ctx.c11CameraManager is not None:
            self.__ctx.c11CameraManager.clearSelectedEmblemInfo()
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview()
        self.__updateAnchorsData()
        if tabIndex == C11nTabs.STYLE:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)._asdict()
        elif tabIndex == C11nTabs.EFFECT:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.MODIFICATION, 0)._asdict()
        else:
            slotIdVO = None
        self.as_updateSelectedRegionsS(slotIdVO)
        self.__updateDnd()
        self.__hidePropertiesSheet()
        return

    def __onItemsInstalled(self, item, slotId, limitReached):
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        else:
            areaId, slotType, regionIdx = self.__ctx.selectedAnchor
            self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
            self.__showPropertiesSheet(areaId, slotType, regionIdx)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        if limitReached:
            self.__clearItem()

    def __onItemsRemoved(self):
        self.soundManager.playInstantSound(SOUNDS.REMOVE)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        self.__clearItem()

    def __onModeChanged(self, mode):
        self.__setHeaderInitData()
        self.__setSeasonData(True)

    def fadeOutAnchors(self, isFadeOut):
        self.fadeAnchorsOut = isFadeOut

    def onCloseWindow(self):
        if self.isDisposed():
            return
        if self._isPropertySheetShown:
            self.__clearItem()
        if self.__ctx.isOutfitsModified():
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__onCloseWindow)
        else:
            self.__onCloseWindow(proceed=True)

    def itemContextMenuDisplayed(self):
        cmHandler = self.app.contextMenuManager.getCurrentHandler()
        if isinstance(cmHandler, CustomizationItemCMHandler):
            cmHandler.onSelected += self._itemCtxMenuSelected

    def onLobbyClick(self):
        if self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION, C11nTabs.PROJECTION_DECAL):
            self.__hidePropertiesSheet()
            self.__clearItem()
        if not self.__ctx.isCaruselItemSelected():
            self.as_enableDNDS(True)

    def onChangeSize(self):
        self.__updateAnchorsData()

    def playCustomSound(self, sound):
        self.soundManager.playInstantSound(sound)

    def onSelectAnchor(self, areaId, slotType, regionIdx):
        if not self.__ctx.isCaruselItemSelected():
            self.as_enableDNDS(False)
        anchorSelected = self.__ctx.isAnchorSelected(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
        itemInstalled = self.__ctx.anchorSelected(slotType, areaId, regionIdx)
        self.__hideAnchorSwitchers()
        if self.__ctx.isSlotFilled(self.__ctx.selectedAnchor):
            if self.__ctx.isCaruselItemSelected():
                if anchorSelected and not itemInstalled:
                    self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                    self.__showPropertiesSheet(areaId, slotType, regionIdx)
            else:
                self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                self.__showPropertiesSheet(areaId, slotType, regionIdx)
        else:
            self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
            self.__hidePropertiesSheet()

    def __locateCameraOnAnchor(self, areaId, slotType, regionIdx):
        if self.__ctx.c11CameraManager is None:
            return
        else:
            self.__updateAnchorsData()
            if slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
                if slotType == GUI_ITEM_TYPE.EMBLEM:
                    emblemType = 'player'
                    zoom = MainView._ZOOM_ON_EMBLEM
                else:
                    emblemType = 'inscription'
                    zoom = MainView._ZOOM_ON_INSCRIPTION
                self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnEmblem(areaId == Area.HULL, emblemType, regionIdx, zoom)
            else:
                anchorParams = self.service.getAnchorParams(areaId, slotType, regionIdx)
                if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnAnchor(anchorParams.pos, anchorParams.normal)
                else:
                    self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnAnchor(anchorParams.pos, None)
            return

    def __onItemsBought(self, purchaseItems, results):
        errorCount = 0
        for result in results:
            if not result.success:
                errorCount += 1
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

        if not errorCount:
            cart = getTotalPurchaseInfo(purchaseItems)
            if cart.totalPrice != ITEM_PRICE_EMPTY:
                msgCtx = {'money': formatPrice(cart.totalPrice.price),
                 'count': cart.numSelected}
                SystemMessages.pushI18nMessage(MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CONVERTER_CUSTOMIZATIONSBUY, type=CURRENCY_TO_SM_TYPE.get(cart.totalPrice.getCurrency(byWeight=True), SM_TYPE.PurchaseForGold), **msgCtx)
            else:
                SystemMessages.pushI18nMessage(MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CONVERTER_CUSTOMIZATIONS, type=SM_TYPE.Information)
            self.__onCloseWindow(proceed=True)

    def onAnchorsShown(self, anchors):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setAnchors(anchors)
        return

    def propertiesSheetSet(self, sheet, width, height, crnterX, centerY):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMenuParams(sheet, width, height, crnterX, centerY)
        return

    def _populate(self):
        super(MainView, self)._populate()
        self.__ctx = self.service.getCtx()
        self.__ctx.onCustomizationSeasonChanged += self.__onSeasonChanged
        self.__ctx.onCustomizationModeChanged += self.__onModeChanged
        self.__ctx.onCustomizationTabChanged += self.__onTabChanged
        self.__ctx.onCustomizationItemInstalled += self.__onItemsInstalled
        self.__ctx.onCustomizationItemsRemoved += self.__onItemsRemoved
        self.__ctx.onCustomizationItemsBought += self.__onItemsBought
        self.__ctx.onCacheResync += self.__onCacheResync
        self.__ctx.onChangesCanceled += self.__onChangesCanceled
        self.__ctx.onCaruselItemSelected += self.__onCarouselItemSelected
        self.__ctx.onPropertySheetHidden += self.__onPropertySheetHidden
        self.__ctx.onPropertySheetShown += self.__onPropertySheetShown
        self.__ctx.onClearItem += self.__onClearItem
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_ModalWindowsPopupHandler(), _C11ViewsPopupHandler(self.__hidePropertiesSheet)])
        self.lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        self._seasonSoundAnimantion = _SeasonSoundAnimantion(len(SeasonType.COMMON_SEASONS), self.soundManager)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__ctx.refreshOutfit()
        self.as_selectSeasonS(SEASON_TYPE_TO_IDX[self.__ctx.currentSeason])
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
        self._isPropertySheetShown = False
        if self.__ctx.c11CameraManager is not None:
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(forceLocate=True)
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        self.__renderEnv.enable(True)
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMainView(self.flashObject)
        return

    def _dispose(self):
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        if g_appLoader.getSpaceID() != _SPACE_ID.LOGIN:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.EXIT)
        if self.__ctx.c11CameraManager is not None:
            if self.__locatedOnEmbelem:
                self.__ctx.c11CameraManager.clearSelectedEmblemInfo()
            self.__ctx.c11CameraManager.locateCameraToStartState()
        self._seasonSoundAnimantion = None
        self.__renderEnv.enable(False)
        self.__renderEnv = None
        self.__viewLifecycleWatcher.stop()
        self.service.stopHighlighter()
        self.lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh -= self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted -= self.__onRegionHighlighted
        if g_currentVehicle.item:
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self.__ctx.currentSeason
            g_currentVehicle.refreshModel()
        self.__hidePropertiesSheet()
        self.__propertiesSheet = None
        self.__ctx.onPropertySheetShown -= self.__onPropertySheetShown
        self.__ctx.onPropertySheetHidden -= self.__onPropertySheetHidden
        self.__ctx.onCaruselItemSelected -= self.__onCarouselItemSelected
        self.__ctx.onChangesCanceled -= self.__onChangesCanceled
        self.__ctx.onCacheResync -= self.__onCacheResync
        self.__ctx.onCustomizationItemsBought -= self.__onItemsBought
        self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
        self.__ctx.onCustomizationItemInstalled -= self.__onItemsInstalled
        self.__ctx.onCustomizationTabChanged -= self.__onTabChanged
        self.__ctx.onCustomizationModeChanged -= self.__onModeChanged
        self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
        self.__ctx.onClearItem -= self.__onClearItem
        self.__ctx = None
        self.service.destroyCtx()
        super(MainView, self)._dispose()
        return

    @adisp_process
    def _itemCtxMenuSelected(self, ctxMenuID, itemIntCD):
        item = self.itemsCache.items.getItemByCD(itemIntCD)
        if ctxMenuID == CustomizationOptions.BUY:
            yield DialogsInterface.showDialog(ConfirmC11nBuyMeta(itemIntCD))
        elif ctxMenuID == CustomizationOptions.SELL:
            inventoryCount = self.__ctx.getItemInventoryCount(item)
            yield DialogsInterface.showDialog(ConfirmC11nSellMeta(itemIntCD, inventoryCount, self.__ctx.sellItem))
        elif ctxMenuID == CustomizationOptions.REMOVE_FROM_TANK:
            if self.__ctx.mode == C11nMode.CUSTOM:
                self.__ctx.removeItems(False, itemIntCD)
            else:
                self.__ctx.removeStyle(itemIntCD)

    def _getUpdatedAnchorsData(self):
        tabIndex = self.__ctx.currentTab
        cType = TABS_ITEM_MAPPING[tabIndex]
        slotIds = []
        if tabIndex == C11nTabs.STYLE:
            slotId = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)
            slotIds.append(slotId)
        else:
            for areaId in Area.ALL:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, cType)
                for regionsIndex in regionsIndexes:
                    slotId = CustomizationSlotIdVO(areaId, cType, regionsIndex)
                    slotIds.append(slotId)

        anchorVOs = []
        for zIdx, slotId in enumerate(slotIds):
            anchorVOs.append(CustomizationAnchorPositionVO(zIdx, slotId._asdict())._asdict())

        return CustomizationAnchorsSetVO(anchorVOs)._asdict()

    def __updateAnchorsData(self):
        self.as_setAnchorsDataS(self._getUpdatedAnchorsData())

    def __onRegionHighlighted(self, slotType, areaId, regionIdx, highlightingType, highlightingResult):
        region = None
        if self.__ctx.currentTab == C11nTabs.EFFECT:
            areaId = Area.MISC
            slotType = GUI_ITEM_TYPE.MODIFICATION
        if areaId != -1 and regionIdx != -1:
            region = CustomizationSlotIdVO(areaId, slotType, regionIdx)._asdict()
        else:
            self.__hidePropertiesSheet()
        self.as_onRegionHighlightedS(region, highlightingType, highlightingResult)
        if highlightingType:
            if highlightingResult:
                anchorSelected = self.__ctx.isAnchorSelected(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
                itemInstalled = self.__ctx.anchorSelected(slotType, areaId, regionIdx)
                slotFilled = self.__ctx.isSlotFilled(self.__ctx.selectedAnchor)
                if self.__ctx.currentTab in (C11nTabs.EFFECT, C11nTabs.STYLE):
                    applyArea = ApplyArea.ALL
                else:
                    applyArea = appliedToFromSlotsIds([self.__ctx.selectedAnchor])
                if self.__ctx.isCaruselItemSelected():
                    self.service.highlightRegions(self.__ctx.getEmptyRegions())
                    if slotFilled and anchorSelected and not itemInstalled:
                        self.service.selectRegions(applyArea)
                        self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                        self.__showPropertiesSheet(areaId, slotType, regionIdx)
                        self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                    else:
                        self.service.selectRegions(ApplyArea.NONE)
                        self.__hidePropertiesSheet()
                        self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                else:
                    if slotFilled:
                        self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                        self.__showPropertiesSheet(areaId, slotType, regionIdx)
                    else:
                        self.__resetCameraFocus()
                        self.__hidePropertiesSheet()
                    self.service.selectRegions(applyArea)
            else:
                self.__clearItem()
        elif highlightingResult:
            self.soundManager.playInstantSound(SOUNDS.HOVER)
        return

    def __onSpaceCreateHandler(self):
        Waiting.hide(_WAITING_MESSAGE)
        self.__ctx.refreshOutfit()
        self.__updateAnchorsData()

    def __onSpaceDestroyHandler(self, _):
        Waiting.hide(_WAITING_MESSAGE)
        self.__onCloseWindow(proceed=True)

    def __onSpaceRefreshHandler(self):
        Waiting.show(_WAITING_MESSAGE)

    def __onCloseWindow(self, proceed):
        if proceed:
            if self._isPropertySheetShown:
                self.__clearItem()
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.__onCloseWindow(proceed=True)
            return
        self.__setHeaderInitData()
        self.__setSeasonData()

    def __onChangesCanceled(self):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        self.__hidePropertiesSheet()
        self.__clearItem()

    def __onCarouselItemSelected(self, index, intCD):
        tabIndex = self.__ctx.currentTab
        if tabIndex == C11nTabs.STYLE or tabIndex == C11nTabs.EFFECT:
            self.service.selectRegions(ApplyArea.ALL)
            areaId, slotType, regionIdx = self.__ctx.selectedAnchor
            self.onSelectAnchor(areaId, slotType, regionIdx)
        if not self.__propertiesSheet.isVisible and not self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.PICK)
            self.itemIsPicked = True
        if self.__ctx.isAnyAnchorSelected() and not self.__ctx.isCaruselItemSelected():
            areaId, slotType, regionIdx = self.__ctx.selectedAnchor
            self.__showPropertiesSheet(areaId, slotType, regionIdx)

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onCloseWindow(proceed=True)

    def __onPropertySheetShown(self):
        self._isPropertySheetShown = True
        self.__updateDnd()

    def __onPropertySheetHidden(self):
        tabIndex = self.__ctx.currentTab
        if tabIndex in C11nTabs.REGIONS:
            self.service.resetHighlighting()
        else:
            self.__hideAnchorSwitchers()
        self._isPropertySheetShown = False
        self.__updateDnd()

    def __updateDnd(self):
        isDndEnable = False
        if not self._isPropertySheetShown:
            isDndEnable = self.__ctx.currentTab not in DRAG_AND_DROP_INACTIVE_TABS
        self.as_enableDNDS(isDndEnable)

    def __setSeasonData(self, forceAnim=False):
        seasonRenderersList = []
        filledSeasonSlots = 0
        for season in SEASONS_ORDER:
            seasonName = SEASON_TYPE_TO_NAME.get(season)
            if self.__ctx.mode == C11nMode.CUSTOM:
                isFilled = self.__ctx.checkSlotsFillingForSeason(season)
            else:
                isFilled = self.__ctx.modifiedStyle is not None
            filledSeasonSlots += int(isFilled)
            seasonRenderersList.append({'nameText': VEHICLE_CUSTOMIZATION.getSeasonName(seasonName),
             'nameSelectedText': VEHICLE_CUSTOMIZATION.getSeasonSelectedName(seasonName),
             'seasonImageSrc': RES_ICONS.getSeasonImage(seasonName),
             'seasonBGImageSrc': RES_ICONS.getSeasonBGImage(seasonName),
             'seasonShineImageSrc': RES_ICONS.getSeasonShineImage(seasonName),
             'isFilled': isFilled,
             'forceAnim': forceAnim,
             'tooltip': makeTooltip(body=VEHICLE_CUSTOMIZATION.getSheetSeasonName(seasonName))})

        self.as_setSeasonsBarDataS(seasonRenderersList)
        self._seasonSoundAnimantion.setFilledSeasonSlots(filledSeasonSlots, forceAnim)
        return

    def __setAnchorsInitData(self, update=False):

        def customizationSlotIdToUid(customizationSlotIdVO):
            s = struct.pack('bbh', customizationSlotIdVO.areaId, customizationSlotIdVO.slotId, customizationSlotIdVO.regionId)
            return struct.unpack('I', s)[0]

        tabIndex = self.__ctx.currentTab
        anchorVOs = []
        cType = TABS_ITEM_MAPPING[tabIndex]
        maxItemsReached = False
        if tabIndex == C11nTabs.STYLE:
            anchorId = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)
            uid = customizationSlotIdToUid(anchorId)
            anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), self.__ctx.modifiedStyle.intCD if self.__ctx.modifiedStyle is not None else 0, uid, None)._asdict())
        else:
            potentialPlaceTooltip = None
            if cType in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
                outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
                if self.__ctx.isC11nItemsQuantityLimitReached(outfit, cType):
                    maxItemsReached = True
                    potentialPlaceTooltip = makeTooltip(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_POTENTIALPROJDECALPLACE_TITLE, VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_POTENTIALPROJDECALPLACE_TEXT)
            for areaId in Area.ALL:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, cType)
                slot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(cType)
                for regionsIndex in regionsIndexes:
                    anchorId = CustomizationSlotIdVO(areaId, cType, regionsIndex)
                    slotId = self.__ctx.getSlotIdByAnchorId(C11nId(areaId=areaId, slotType=cType, regionIdx=regionsIndex))
                    itemIntCD = 0
                    if slotId is not None:
                        item = slot.getItem(slotId.regionIdx)
                        itemIntCD = item.intCD if item is not None else 0
                    tooltip = None
                    if not itemIntCD:
                        tooltip = potentialPlaceTooltip
                    uid = customizationSlotIdToUid(anchorId)
                    anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), itemIntCD, uid, tooltip)._asdict())

        if tabIndex in C11nTabs.REGIONS:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_REGION
        elif tabIndex == C11nTabs.PROJECTION_DECAL:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_PROJECTION_DECAL
        else:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_DECAL
        if update:
            self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, typeRegions, maxItemsReached)._asdict())
        else:
            self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, typeRegions, maxItemsReached)._asdict())
        return

    def __setHeaderInitData(self):
        vehicle = g_currentVehicle.item
        self.as_setHeaderDataS({'tankTier': str(int2roman(vehicle.level)),
         'tankName': vehicle.shortUserName,
         'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'isElite': vehicle.isElite,
         'closeBtnTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN})

    def __showPropertiesSheet(self, areaId, slotType, regionIdx):
        if self.__propertiesSheet:
            if self.__ctx.vehicleAnchorsUpdater is not None:
                self.__ctx.vehicleAnchorsUpdater.attachMenuToAnchor(self.__ctx.selectedAnchor)
                if self.__ctx.currentTab in C11nTabs.REGIONS:
                    self.__ctx.vehicleAnchorsUpdater.changeAnchorParams(self.__ctx.selectedAnchor, True, False)
            if self.__propertiesSheet.isVisible:
                self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            self.__propertiesSheet.show(areaId, slotType, regionIdx)
            tabIndex = self.__ctx.currentTab
            if tabIndex not in C11nTabs.REGIONS:
                self.__showAnchorSwitchers(tabIndex == C11nTabs.EMBLEM)
        return

    def __hidePropertiesSheet(self):
        if self.__propertiesSheet:
            if self.__ctx.vehicleAnchorsUpdater is not None and self.__ctx.currentTab in C11nTabs.REGIONS:
                self.__ctx.vehicleAnchorsUpdater.changeAnchorParams(self.__ctx.selectedAnchor, True, True)
            self.__propertiesSheet.hide()
        return

    def getItemTabsData(self):
        data = []
        pluses = []
        for tabIdx in self.__ctx.visibleTabs:
            itemTypeID = TABS_ITEM_MAPPING[tabIdx]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            showPlus = not self.__checkSlotsFilling(itemTypeID, self._currentSeason)
            data.append({'label': _ms(ITEM_TYPES.customizationPlural(typeName)),
             'tooltip': makeTooltip(ITEM_TYPES.customizationPlural(typeName), TOOLTIPS.customizationItemTab(typeName)),
             'id': tabIdx})
            pluses.append(showPlus)

        return (data, pluses)

    @async
    @adisp_process
    def __confirmHeaderNavigation(self, callback):
        if self._isPropertySheetShown:
            self.__clearItem()
        if self.__ctx.isOutfitsModified():
            result = yield DialogsInterface.showI18nConfirmDialog('customization/close')
        else:
            result = True
        if result:
            self.__onCloseWindow(proceed=True)
        callback(result)

    def __releaseItemSound(self):
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.RELEASE)
            self.itemIsPicked = False

    def __resetCameraFocus(self):
        if self.__locatedOnEmbelem:
            if self.__ctx.c11CameraManager is not None:
                self.__ctx.c11CameraManager.clearSelectedEmblemInfo()
                self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(preserveAngles=True)
            self.__updateAnchorsData()
            self.__locatedOnEmbelem = False
        return

    def __resetUIFocus(self):
        self.as_onRegionHighlightedS(-1, True, False)

    def __onClearItem(self):
        self.__clearItem()

    def __clearItem(self):
        self.service.highlightRegions(ApplyArea.NONE)
        self.service.selectRegions(ApplyArea.NONE)
        self.__resetCameraFocus()
        _, slotType, _ = self.__ctx.selectedAnchor
        self.__ctx.anchorSelected(slotType, -1, -1)
        self.__resetUIFocus()
        self.as_releaseItemS()

    def __hideAnchorSwitchers(self, anchor=None):
        if anchor is not None:
            areaId, slotType, regionIdx = anchor
        else:
            areaId, slotType, regionIdx = (-1, -1, -1)
        self.as_setAnchorSwitchersVisibleS(False, CustomizationSlotIdVO(areaId, slotType, regionIdx)._asdict())
        return

    def __showAnchorSwitchers(self, isNarrowSlot):
        areaId, slotType, regionIdx = self.__ctx.selectedAnchor
        self.as_setAnchorSwitchersVisibleS(True, CustomizationSlotIdVO(areaId, slotType, regionIdx)._asdict(), isNarrowSlot)
