# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import logging
import struct
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentVehicle
from Math import Matrix
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION, CAROUSEL_ARROWS_HINT_SHOWN_FIELD
from adisp import async, process as adisp_process
from gui import DialogsInterface, g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_SLOT_TYPE_MAPPING, DRAG_AND_DROP_INACTIVE_TABS, C11nTabs
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.CUSTOMIZATION_DIALOGS import CUSTOMIZATION_DIALOGS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.customization.shared import chooseMode, getAppliedRegionsForCurrentHangarVehicle, appliedToFromSlotsIds, C11nId, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_NAME, SEASON_TYPE_TO_IDX, SEASONS_ORDER, getTotalPurchaseInfo, containsVehicleBound
from gui.impl.pub import UIImplType
from gui.hangar_cameras.c11n_hangar_camera_manager import C11nCameraModes
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.formatters import formatPrice, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, ApplyArea
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.impl.gen import R
from gui.impl.lobby.customization.customization_cart_view import CustomizationCartView
from gui.Scaleform.framework import ScopeTemplates
_logger = logging.getLogger(__name__)

class _ModalWindowsPopupHandler(IViewLifecycleHandler):
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DYNAMIC = (VIEW_ALIAS.SIMPLE_DIALOG, CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, R.views.lobby.customization.CustomizationCart())

    def __init__(self, onViewCreatedCallback, onViewDestroyedCallback):
        super(_ModalWindowsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DYNAMIC ])
        self.__viewStack = []
        self.__onViewCreatedCallback = onViewCreatedCallback
        self.__onViewDestroyedCallback = onViewDestroyedCallback

    def onViewCreated(self, view):
        self.__onViewCreatedCallback()
        self.__viewStack.append(view.key)

    def onViewDestroyed(self, _):
        self.__viewStack.pop()
        if not self.__viewStack:
            self.__onViewDestroyedCallback()


CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'typeRegions'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))
CustomizationAnchorsStateVO = namedtuple('CustomizationAnchorsStateVO', ('uid', 'value'))
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


class MainView(LobbySubView, CustomizationMainViewMeta):
    __background_alpha__ = 0.0
    _COMMON_SOUND_SPACE = C11N_SOUND_SPACE
    _ZOOM_ON_EMBLEM = 0.1
    _ZOOM_ON_INSCRIPTION = 0.1
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)
    appLoader = dependency.descriptor(IAppLoader)
    guiLoader = dependency.descriptor(IGuiLoader)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewCtx=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.itemIsPicked = False
        self.__propertiesSheet = None
        self.__styleInfo = None
        self._seasonSoundAnimantion = None
        self.__ctx = None
        self.__viewCtx = viewCtx or {}
        self.__renderEnv = None
        self.__initAnchorsPositionsCallback = None
        self.__setCollisionsCallback = None
        self.__selectedAnchor = C11nId()
        self.__locateCameraToStyleInfo = False
        self.__isHangarPlaceSwitched = False
        return

    def showBuyWindow(self, ctx=None):
        if self.__propertiesSheet.handleBuyWindow():
            return
        isGamefaceEnabled = self.__isGamefaceEnabled()
        isGamefaceBuyViewOpened = self.__isGamefaceBuyViewOpened()
        isGamefaceCanOpened = isGamefaceEnabled and not isGamefaceBuyViewOpened
        if not isGamefaceCanOpened:
            self.changeVisible(False)
        purchaseItems = self.__ctx.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.totalPrice == ITEM_PRICE_EMPTY:
            if containsVehicleBound(purchaseItems):
                DialogsInterface.showI18nConfirmDialog(CUSTOMIZATION_DIALOGS.CUSTOMIZATION_INSTALL_BOUND_CHECK_NOTIFICATION, self.onBuyConfirmed)
            else:
                self.__ctx.applyItems(purchaseItems)
                if self.__styleInfo.visible:
                    self.__styleInfo.disableBlur()
        elif isGamefaceEnabled:
            if isGamefaceBuyViewOpened:
                _logger.debug('Gameface customization cart is already opened, ignore event')
                return
            _logger.info('Gameface customization cart is opened')
            ctx = ctx or {}
            ctx.update(c11nView=self)
            self.fireEvent(events.LoadUnboundViewEvent(R.views.lobby.customization.CustomizationCart(), CustomizationCartView, ScopeTemplates.LOBBY_SUB_SCOPE, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            _logger.info('Scalefrom customization cart is opened')
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def __onVehicleChangeStarted(self):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleChanged(self):
        self.__locateCameraToStyleInfo = False
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        if self.__styleInfo is not None and self.__styleInfo.visible:
            self.__styleInfo.disableBlur()
            self.__onStyleInfoHidden()
        self.__clearSelectionAndHidePropertySheet()
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__initAnchorsPositionsCallback = BigWorld.callback(0.0, self.__initAnchorsPositions)
        self.__setCollisionsCallback = BigWorld.callback(0.0, self.__wrapSetCollisions)
        return

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        if self.__ctx.c11CameraManager is not None:
            return
        else:
            if self.__locateCameraToStyleInfo:
                self.__locateCameraToStyleInfo = False
                self.__ctx.c11CameraManager.locateCameraToStyleInfoPreview()
            return

    def __initAnchorsPositions(self):
        self.__initAnchorsPositionsCallback = None
        if self.__ctx.c11CameraManager is not None and self.__ctx.c11CameraManager.vEntity is not None:
            self.__ctx.c11CameraManager.vEntity.appearance.updateAnchorsParams()
        self.__setAnchorsInitData()
        self.__locateCameraToCustomizationPreview(updateTankCentralPoint=True)
        return

    def __wrapSetCollisions(self):
        self.__setCollisionsCallback = None
        self.__ctx.vehicleAnchorsUpdater.setCollisions()
        return

    def onBuyConfirmed(self, isOk):
        if isOk:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.SELECT)
            self.__ctx.applyItems(self.__ctx.getPurchaseItems())
        else:
            self.changeVisible(True)

    def onPressClearBtn(self):
        if self.__propertiesSheet is not None:
            self.__propertiesSheet.hide()
        self.__ctx.cancelChanges()
        return

    def onPressEscBtn(self):
        if self.__propertiesSheet.handleEscBtn():
            return
        tabIndex = self.__ctx.currentTab
        if tabIndex not in C11nTabs.REGIONS and self.__ctx.isAnyAnchorSelected() or self.service.isRegionSelected():
            self.__clearSelectionAndHidePropertySheet()
            self.as_enableDNDS(True)
        else:
            self.onCloseWindow()

    def onPressSelectNextItem(self, reverse=False):
        self.soundManager.playInstantSound(SOUNDS.SELECT)
        self.__ctx.installNextCarouselItem(reverse)

    def changeVisible(self, value):
        if self.isDisposed():
            return
        self.__clearSelectedAnchor()
        self.as_hideS(value)

    def onReleaseItem(self):
        if self.itemIsPicked:
            self.__ctx.caruselItemUnselected()
            self.__releaseItemSound()
            if not self.__propertiesSheet.visible:
                self.__clearSelectedAnchor()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET:
            self.__propertiesSheet = viewPy
        elif alias == VIEW_ALIAS.CUSTOMIZATION_STYLE_INFO:
            self.__styleInfo = viewPy

    def changeSeason(self, seasonIdx, needToKeepSelect):
        currentSelected = self.__ctx.selectedCarouselItem.intCD
        if self.__ctx.isAnyAnchorSelected() and not self.__styleInfo.visible:
            self.__clearSelectionAndHidePropertySheet()
        if seasonIdx in SEASON_IDX_TO_TYPE:
            self.__ctx.changeSeason(SEASON_IDX_TO_TYPE[seasonIdx])
        else:
            _logger.error('Wrong season index %(seasonIdx)d', {'seasonIdx': seasonIdx})
        if needToKeepSelect:
            self.as_reselectS(currentSelected)

    def __onSeasonChanged(self, seasonType):
        seasonName = SEASON_TYPE_TO_NAME.get(seasonType)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.__setAnchorsInitData(True)
        self.__setHeaderInitData()
        self.__setNotificationCounters()

    def __onTabChanged(self, tabIndex):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.service.stopHighlighter()
        if tabIndex in C11nTabs.REGIONS:
            itemTypeID = TABS_SLOT_TYPE_MAPPING[tabIndex]
            self.service.startHighlighter(chooseMode(itemTypeID, g_currentVehicle.item))
        if self.__ctx.c11CameraManager is not None:
            self.__locateCameraToCustomizationPreview(preserveAngles=True)
        self.__setAnchorsInitData()
        self.__updateAnchorsData()
        if tabIndex == C11nTabs.STYLE:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)._asdict()
        elif tabIndex == C11nTabs.EFFECT:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.MODIFICATION, 0)._asdict()
        else:
            slotIdVO = None
        self.as_updateSelectedRegionsS(slotIdVO)
        self.__updateDnd()
        self.__setHeaderInitData()
        self.__setNotificationCounters()
        return

    def __onItemsInstalled(self, item, component, slotId, limitReached):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        elif self.__ctx.c11CameraManager.currentMode == C11nCameraModes.PREVIEW:
            self.__locateCameraOnAnchor(slotId.areaId, slotId.slotType, slotId.regionIdx)
        if limitReached and (component is None or component.isFilled()):
            self.as_releaseItemS()
        return

    def __onItemsRemoved(self):
        self.soundManager.playInstantSound(SOUNDS.REMOVE)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        slotId = self.__ctx.getSlotIdByAnchorId(self.__selectedAnchor)
        if slotId is not None:
            item = self.__ctx.getItemFromRegion(slotId)
            if item is None:
                self.__clearItem(releaseItem=False)
        else:
            self.__clearItem(releaseItem=False)
        return

    def __onModeChanged(self, mode):
        self.__setHeaderInitData()
        self.__setSeasonData(True)
        self.__setAnchorsInitData()

    def fadeOutAnchors(self, isFadeOut):
        self.fadeAnchorsOut = isFadeOut

    def onCloseWindow(self, force=False):
        if self.isDisposed():
            return
        self.__clearSelectionAndHidePropertySheet()
        if force or not self.__ctx.isOutfitsModified():
            self.__onCloseWindow(proceed=True)
        else:
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__onCloseWindow)

    def itemContextMenuDisplayed(self):
        cmHandler = self.app.contextMenuManager.getCurrentHandler()
        if isinstance(cmHandler, CustomizationItemCMHandler):
            cmHandler.onSelected += self._itemCtxMenuSelected

    def onLobbyClick(self):
        if self.__propertiesSheet.handleLobbyClick():
            return
        if self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION, C11nTabs.PROJECTION_DECAL):
            self.__clearSelectionAndHidePropertySheet()
        if not self.__ctx.isCaruselItemSelected():
            self.as_enableDNDS(True)

    def onChangeSize(self):
        self.__updateAnchorsData()

    def playCustomSound(self, sound):
        self.soundManager.playInstantSound(sound)

    def onRemoveSelectedItem(self):
        if self.__styleInfo.visible:
            return
        else:
            if self.__propertiesSheet is not None:
                self.__propertiesSheet.handleDelBtn()
            return

    def onSelectAnchor(self, areaId, slotType, regionIdx):
        anchorId = C11nId(areaId, slotType, regionIdx)
        anchorState = self.__ctx.vehicleAnchorsUpdater.getAnchorState(anchorId)
        if anchorState == CUSTOMIZATION_ALIASES.ANCHOR_STATE_REMOVED:
            slotId = self.__ctx.getSlotIdByAnchorId(anchorId)
            self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
            return
        else:
            if not self.__ctx.isCaruselItemSelected():
                self.as_enableDNDS(False)
            self.__ctx.onSelectAnchor(areaId, slotType, regionIdx)
            anchorSelected = self.__ctx.isAnchorSelected(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
            itemInstalled = self.__ctx.anchorSelected(slotType, areaId, regionIdx)
            selectedAnchor = self.__ctx.selectedAnchor
            if selectedAnchor is not None and self.__ctx.isSlotFilled(selectedAnchor):
                if self.__ctx.isCaruselItemSelected():
                    if anchorSelected and not itemInstalled:
                        self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
                else:
                    self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
                component = self.__ctx.getComponentFromSelectedRegion()
                if component is not None and not component.isFilled():
                    self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
            else:
                self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
            return

    def onHoverAnchor(self, areaID, slotID, regionID, hover):
        anchorId = C11nId(areaID, slotID, regionID)
        if hover:
            self.__ctx.onAnchorHovered(anchorId)
        else:
            self.__ctx.onAnchorUnhovered(anchorId)

    def onDragAnchor(self, areaID, slotID, regionID):
        anchorId = C11nId(areaID, slotID, regionID)
        if anchorId.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
            return
        elif self.__ctx.isCaruselItemSelected() or self.__propertiesSheet.visible:
            return
        else:
            slotId = self.__ctx.getSlotIdByAnchorId(anchorId)
            if slotId is not None:
                item = self.__ctx.getItemFromRegion(slotId)
                if item is not None:
                    self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, slotId)
                    self.as_attachToCursorS(item.intCD)
            return

    def resetC11nItemsNovelty(self, itemsList):
        self.__ctx.resetC11nItemsNovelty(itemsList)

    def __locateCameraOnAnchor(self, areaId, slotType, regionIdx, forceRotate=False):
        if self.__ctx.c11CameraManager is None:
            return
        else:
            self.__updateAnchorsData()
            anchorParams = self.service.getAnchorParams(areaId, slotType, regionIdx)
            if anchorParams is None:
                return
            if slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
                if slotType == GUI_ITEM_TYPE.EMBLEM:
                    relativeSize = MainView._ZOOM_ON_EMBLEM
                else:
                    relativeSize = MainView._ZOOM_ON_INSCRIPTION
                located = self.__ctx.c11CameraManager.locateCameraOnDecal(location=anchorParams.location, width=anchorParams.descriptor.size, anchorId=anchorParams.id, relativeSize=relativeSize, forceRotate=forceRotate)
            else:
                if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                    normal = anchorParams.location.normal
                    if normal.dot((0.0, 1.0, 0.0)) > 0.99:
                        localPYR = anchorParams.descriptor.rotation
                        worldRotation = Matrix()
                        worldRotation.setRotateYPR((localPYR.y, localPYR.x, localPYR.z))
                        vehicleMatrix = self.hangarSpace.getVehicleEntity().model.matrix
                        worldRotation.postMultiply(vehicleMatrix)
                        normal.setPitchYaw(anchorParams.location.normal.pitch, worldRotation.yaw)
                else:
                    normal = None
                located = self.__ctx.c11CameraManager.locateCameraOnAnchor(position=anchorParams.location.position, normal=normal, up=anchorParams.location.up, anchorId=anchorParams.id, forceRotate=forceRotate)
            if located and not forceRotate:
                self.__selectedAnchor = C11nId(areaId, slotType, regionIdx)
                self.__propertiesSheet.locateOnAnchor(areaId, slotType, regionIdx)
                self.__ctx.vehicleAnchorsUpdater.onCameraLocated(self.__selectedAnchor)
            return

    def __locateCameraToCustomizationPreview(self, **kwargs):
        if self.__ctx.c11CameraManager is None:
            return
        else:
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(**kwargs)
            self.__selectedAnchor = C11nId()
            self.__propertiesSheet.locateToCustomizationPreview()
            self.__ctx.vehicleAnchorsUpdater.onCameraLocated()
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

    def propertiesSheetSet(self, sheet, width, height, centerX, centerY):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMenuParams(sheet, width, height, centerX, centerY)
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
        self.__ctx.onProlongStyleRent += self.__onProlongStyleRent
        self.__ctx.onShowStyleInfo += self.__onShowStyleInfo
        self.__ctx.onStyleInfoHidden += self.__onStyleInfoHidden
        self.__ctx.onResetC11nItemsNovelty += self.__onResetC11nItemsNovelty
        self.__ctx.onEditModeStarted += self.__onEditModeStarted
        self.__ctx.onGetItemBackToHand += self.__onGetItemBackToHand
        self.__ctx.onAnchorsStateChanged += self.__onAnchorsStateChanged
        self.__ctx.c11CameraManager.onTurretRotated += self.__onTurretRotated
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_ModalWindowsPopupHandler(self.__onViewCreatedCallback, self.__onViewDestroyedCallback)])
        self.lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        g_eventBus.addListener(events.HangarPlaceManagerEvent.ON_PLACE_SWITCHED, self.__onHangarPlaceSwitched, scope=EVENT_BUS_SCOPE.LOBBY)
        self._seasonSoundAnimantion = _SeasonSoundAnimantion(len(SeasonType.COMMON_SEASONS), self.soundManager)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__ctx.refreshOutfit()
        self.as_selectSeasonS(SEASON_TYPE_TO_IDX[self.__ctx.currentSeason])
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
        if self.__ctx.c11CameraManager is not None:
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(forceLocate=True)
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        self.__renderEnv.enable(True)
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMainView(self.flashObject)
        self._invalidate(self.__viewCtx)
        if self.__ctx.mode == C11nMode.STYLE:
            BigWorld.callback(0.0, lambda : self.__ctx.tabChanged(C11nTabs.STYLE))
        self.__ctx.vehicleAnchorsUpdater.setCollisions()
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        return

    def _invalidate(self, *args, **kwargs):
        super(MainView, self)._invalidate()
        callback = (args[0] or {}).get('callback')
        if callback is not None:
            callback()
        return

    def _dispose(self):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        if not self.__isHangarPlaceSwitched:
            self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
            self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        if self.appLoader.getSpaceID() != GuiGlobalSpaceID.LOGIN:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.EXIT)
        if self.__ctx.c11CameraManager is not None:
            self.__ctx.c11CameraManager.locateCameraToStartState(not self.__isHangarPlaceSwitched)
        if self.__styleInfo is not None:
            self.__styleInfo.disableBlur()
            self.__disableStyleInfoSound()
        self._seasonSoundAnimantion = None
        if not self.__isHangarPlaceSwitched:
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
        g_eventBus.removeListener(events.HangarPlaceManagerEvent.ON_PLACE_SWITCHED, self.__onHangarPlaceSwitched, scope=EVENT_BUS_SCOPE.LOBBY)
        if g_currentVehicle.item:
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self.__ctx.currentSeason
            g_currentVehicle.refreshModel()
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
        self.__ctx.onProlongStyleRent -= self.__onProlongStyleRent
        self.__ctx.onShowStyleInfo -= self.__onShowStyleInfo
        self.__ctx.onStyleInfoHidden -= self.__onStyleInfoHidden
        self.__ctx.onResetC11nItemsNovelty -= self.__onResetC11nItemsNovelty
        self.__ctx.onEditModeStarted -= self.__onEditModeStarted
        self.__ctx.onGetItemBackToHand -= self.__onGetItemBackToHand
        self.__ctx.onAnchorsStateChanged -= self.__onAnchorsStateChanged
        self.__ctx.c11CameraManager.onTurretRotated -= self.__onTurretRotated
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        if self.__initAnchorsPositionsCallback is not None:
            BigWorld.cancelCallback(self.__initAnchorsPositionsCallback)
            self.__initAnchorsPositionsCallback = None
        if self.__setCollisionsCallback is not None:
            BigWorld.cancelCallback(self.__setCollisionsCallback)
            self.__setCollisionsCallback = None
        self.__ctx = None
        self.service.closeCustomization()
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
                self.__ctx.removeItems(True, itemIntCD)
            else:
                self.__ctx.removeStyle(itemIntCD)
        elif ctxMenuID == CustomizationOptions.STYLE_INFO:
            self.__ctx.onShowStyleInfo(item)

    def _getUpdatedAnchorsData(self):
        tabIndex = self.__ctx.currentTab
        cType = TABS_SLOT_TYPE_MAPPING[tabIndex]
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
        elif self.__ctx.currentTab == C11nTabs.STYLE:
            areaId = Area.MISC
            slotType = GUI_ITEM_TYPE.STYLE
        if areaId != -1 and regionIdx != -1:
            region = CustomizationSlotIdVO(areaId, slotType, regionIdx)._asdict()
        self.as_onRegionHighlightedS(region, highlightingType, highlightingResult)
        if highlightingType:
            if highlightingResult:
                anchorSelected = self.__ctx.isAnchorSelected(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
                itemSelected = self.__ctx.isCaruselItemSelected()
                itemInstalled = self.__ctx.anchorSelected(slotType, areaId, regionIdx)
                slotFilled = self.__ctx.isSlotFilled(self.__ctx.selectedAnchor)
                if self.__ctx.currentTab in (C11nTabs.EFFECT, C11nTabs.STYLE):
                    applyArea = ApplyArea.ALL
                else:
                    applyArea = appliedToFromSlotsIds([self.__ctx.selectedAnchor])
                if itemSelected:
                    self.service.highlightRegions(self.__ctx.getEmptyRegions())
                    if slotFilled and anchorSelected and not itemInstalled:
                        self.service.selectRegions(applyArea)
                        self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                    else:
                        self.service.selectRegions(ApplyArea.NONE)
                else:
                    if slotFilled:
                        self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                    else:
                        self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                        self.__resetCameraFocus()
                    self.service.selectRegions(applyArea)
                self.__ctx.onSelectAnchor(areaId, slotType, regionIdx)
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
            if self.__propertiesSheet.visible:
                self.__clearItem()
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.__onCloseWindow(proceed=True)
            return
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setNotificationCounters()

    def __onChangesCanceled(self):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        self.__clearItem()

    def __onCarouselItemSelected(self, index, intCD):
        tabIndex = self.__ctx.currentTab
        if tabIndex in (C11nTabs.STYLE, C11nTabs.EFFECT):
            self.service.selectRegions(ApplyArea.ALL)
            areaId, slotType, regionIdx = self.__ctx.selectedAnchor
            self.onSelectAnchor(areaId, slotType, regionIdx)
        if not self.__ctx.isAnyAnchorSelected() and not self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.PICK)
            self.itemIsPicked = True

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onCloseWindow(proceed=True)

    def __onPropertySheetShown(self, anchorId):
        self.__updateDnd()
        custSett = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        if not custSett.get(CAROUSEL_ARROWS_HINT_SHOWN_FIELD, False) and not self.__propertiesSheet.inEditMode:
            self.as_showCarouselsArrowsNotificationS(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_KEYBOARD_HINT)
            custSett[CAROUSEL_ARROWS_HINT_SHOWN_FIELD] = True
            AccountSettings.setSettings(CUSTOMIZATION_SECTION, custSett)

    def __onPropertySheetHidden(self):
        if self.__ctx.currentTab in C11nTabs.REGIONS:
            self.service.resetHighlighting()
        self.__updateDnd()

    def __updateDnd(self):
        isDndEnable = False
        if not self.__propertiesSheet.visible:
            isDndEnable = self.__ctx.currentTab not in DRAG_AND_DROP_INACTIVE_TABS
        self.as_enableDNDS(isDndEnable)

    def __setSeasonData(self, forceAnim=False):
        seasonRenderersList = []
        filledSeasonSlots = 0
        for season in SEASONS_ORDER:
            seasonName = SEASON_TYPE_TO_NAME.get(season)
            if self.__ctx.mode == C11nMode.CUSTOM:
                isFilled = all((slotsCount == filledSlotsCount for slotsCount, filledSlotsCount in self.__ctx.checkSlotsFillingForSeason(season)))
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

    def __setNotificationCounters(self):
        currentSeason = self.__ctx.currentSeason
        seasonCounters = {season:0 for season in SEASONS_ORDER}
        if self.__ctx.mode == C11nMode.STYLE:
            itemTypes = (GUI_ITEM_TYPE.STYLE,)
        else:
            itemTypes = GUI_ITEM_TYPE.CUSTOMIZATIONS_WITHOUT_STYLE
        for season in SEASONS_ORDER:
            if currentSeason != season:
                seasonCounters[season] = g_currentVehicle.item.getC11nItemsNoveltyCounter(g_currentVehicle.itemsCache.items, itemTypes, season)
            seasonCounters[season] = 0

        self.as_setNotificationCountersS([ seasonCounters[season] for season in SEASONS_ORDER ])

    def __customizationSlotIdToUid(self, customizationSlotIdVO):
        s = struct.pack('bbh', customizationSlotIdVO.areaId, customizationSlotIdVO.slotId, customizationSlotIdVO.regionId)
        return struct.unpack('I', s)[0]

    def __setAnchorsInitData(self, update=False):
        if not g_currentVehicle.isPresent():
            return
        else:
            tabIndex = self.__ctx.currentTab
            anchorVOs = []
            slotType = TABS_SLOT_TYPE_MAPPING[tabIndex]
            if tabIndex == C11nTabs.STYLE:
                anchorId = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)
                uid = self.__customizationSlotIdToUid(anchorId)
                anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), self.__ctx.modifiedStyle.intCD if self.__ctx.modifiedStyle is not None else 0, uid)._asdict())
            else:
                for areaId in Area.ALL:
                    slot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(slotType)
                    for anchor in g_currentVehicle.item.getAnchors(slotType, areaId):
                        anchorId = CustomizationSlotIdVO(areaId, slotType, anchor.regionIdx)
                        slotId = self.__ctx.getSlotIdByAnchorId(C11nId(areaId=areaId, slotType=slotType, regionIdx=anchor.regionIdx))
                        itemIntCD = 0
                        if slotId and slotId.slotType == GUI_ITEM_TYPE.INSCRIPTION:
                            item = slot.getItem(slotId.regionIdx)
                            if not item:
                                slot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(GUI_ITEM_TYPE.PERSONAL_NUMBER)
                                item = slot.getItem(slotId.regionIdx)
                            itemIntCD = item.intCD if item is not None else 0
                        elif slotId:
                            item = slot.getItem(slotId.regionIdx)
                            itemIntCD = item.intCD if item is not None else 0
                        uid = self.__customizationSlotIdToUid(anchorId)
                        anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), itemIntCD, uid)._asdict())

            isRegions = tabIndex in C11nTabs.REGIONS
            if isRegions:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_REGION
            elif tabIndex == C11nTabs.PROJECTION_DECAL:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_PROJECTION_DECAL
            else:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_DECAL
            if update:
                self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, typeRegions)._asdict())
            else:
                self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, typeRegions)._asdict())
            return

    def __setHeaderInitData(self):
        vehicle = g_currentVehicle.item
        currentTab = self.__ctx.currentTab
        if currentTab == C11nTabs.STYLE:
            if self.__ctx.modifiedStyle:
                itemsCounter = text_styles.bonusPreviewText(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADER_COUNTER_STYLE_INSTALLED)
            else:
                itemsCounter = text_styles.stats(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADER_COUNTER_STYLE_NOTINSTALLED)
        else:
            itemTypeID = TABS_SLOT_TYPE_MAPPING[currentTab]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            slotsCount, filledSlotsCount = self.__ctx.checkSlotsFilling(itemTypeID, self.__ctx.currentSeason)
            textStyle = text_styles.bonusPreviewText if slotsCount == filledSlotsCount else text_styles.stats
            itemsCounter = textStyle(_ms('#vehicle_customization:customization/header/counter/' + typeName, filled=filledSlotsCount, available=slotsCount))
        self.as_setHeaderDataS({'tankTier': str(int2roman(vehicle.level)),
         'tankName': vehicle.shortUserName,
         'tankInfo': itemsCounter,
         'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'isElite': vehicle.isElite,
         'closeBtnTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN})

    @async
    @adisp_process
    def __confirmHeaderNavigation(self, callback):
        if self.__propertiesSheet.visible:
            self.__propertiesSheet.confirmHeaderNavigation()
            if not self.__styleInfo.visible:
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
        if self.__ctx.c11CameraManager is None:
            return
        else:
            if self.__selectedAnchor != C11nId() or self.__ctx.c11CameraManager.isStyleInfo():
                self.__locateCameraToCustomizationPreview(preserveAngles=True)
                self.__updateAnchorsData()
            return

    def __resetUIFocus(self):
        self.as_onRegionHighlightedS(-1, True, False)

    def __onClearItem(self):
        self.__clearItem()

    def __clearItem(self, releaseItem=True):
        self.service.highlightRegions(ApplyArea.NONE)
        self.service.selectRegions(ApplyArea.NONE)
        self.__resetCameraFocus()
        self.__clearSelectedAnchor()
        if releaseItem:
            self.__resetUIFocus()
            self.as_releaseItemS()

    def __clearSelectedAnchor(self):
        if self.__ctx.isAnyAnchorSelected():
            _, slotType, _ = self.__ctx.selectedAnchor
            self.__ctx.anchorSelected(slotType, -1, -1)

    def __clearSelectionAndHidePropertySheet(self):
        if self.__styleInfo.visible:
            return
        self.__clearItem()

    def __onProlongStyleRent(self):
        ctx = {'prolongStyleRent': True}
        self.showBuyWindow(ctx=ctx)

    def __onShowStyleInfo(self, style=None):
        if self.__styleInfo is None:
            return
        else:
            self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_SHOW)
            self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 1)
            self.service.suspendHighlighter()
            self.__styleInfo.show(style)
            entity = self.hangarSpace.getVehicleEntity()
            if entity and entity.appearance:
                if entity.appearance.isLoaded():
                    self.__ctx.c11CameraManager.locateCameraToStyleInfoPreview()
                else:
                    self.__locateCameraToStyleInfo = True
            return

    def __onStyleInfoHidden(self, toBuyWindow=False):
        if self.__styleInfo is None:
            return
        else:
            self.__disableStyleInfoSound()
            self.__locateCameraToStyleInfo = False
            if not toBuyWindow:
                self.__locateCameraToCustomizationPreview()
                self.service.resumeHighlighter()
            self.__styleInfo.hide()
            return

    def __disableStyleInfoSound(self):
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_HIDE)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 0)

    def __onEditModeStarted(self):
        if self.__selectedAnchor != C11nId():
            areaId, slotType, regionId = self.__selectedAnchor
            self.__locateCameraOnAnchor(areaId, slotType, regionId, forceRotate=True)

    def __onGetItemBackToHand(self, intCD):
        self.as_attachToCursorS(intCD)

    def __onViewCreatedCallback(self):
        if self.__styleInfo.visible:
            return
        self.__propertiesSheet.hide()
        self.service.suspendHighlighter()

    def __onViewDestroyedCallback(self):
        if self.__styleInfo.visible:
            return
        self.__clearItem()
        self.service.resumeHighlighter()

    def __onResetC11nItemsNovelty(self):
        self.__setNotificationCounters()

    def __onAnchorsStateChanged(self, changedStates):
        anchorStateVOs = [ CustomizationAnchorsStateVO(uid, state)._asdict() for uid, state in changedStates.iteritems() ]
        self.as_setAnchorsStateS({'anchorsData': anchorStateVOs})

    def __onTurretRotated(self):
        self.__setAnchorsInitData()
        tabIndex = self.__ctx.currentTab
        if tabIndex in C11nTabs.REGIONS:
            self.service.restartHighlighter()
        if self.__ctx.isAnyAnchorSelected():
            selectedAnchor = self.__ctx.selectedAnchor
            self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
        self.__ctx.refreshOutfit()

    def __isGamefaceEnabled(self):
        isGamefaceInitilized = self.guiLoader.implTypeMask & UIImplType.GAMEFACE_UI_IMPL > 0
        isGamefaceEnabled = self.lobbyContext.getServerSettings().isGamefaceEnabled()
        noInterfaceScale = self.settingsCore.interfaceScale.get() == 1.0
        return isGamefaceInitilized and isGamefaceEnabled and noInterfaceScale

    def __isGamefaceBuyViewOpened(self):
        return self.guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.customization.CustomizationCart())

    def __onHangarPlaceSwitched(self, _):
        self.__isHangarPlaceSwitched = True
