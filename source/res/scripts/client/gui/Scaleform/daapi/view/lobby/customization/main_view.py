# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import logging
from collections import namedtuple
import BigWorld
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from Event import Event
from Math import Matrix
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION, CAROUSEL_ARROWS_HINT_SHOWN_FIELD
import adisp
from async import async, await
from gui import g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_item_vo import buildCustomizationItemDataVO
from gui.Scaleform.daapi.view.lobby.customization.shared import getEmptyRegions, checkSlotsFilling, CustomizationTabs, getItemTypesAvailableForVehicle
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams, GuiImplViewLoadParams
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.customization.constants import CustomizationModes
from gui.customization.shared import chooseMode, appliedToFromSlotsIds, C11nId, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_NAME, SEASON_TYPE_TO_IDX, SEASONS_ORDER, getTotalPurchaseInfo, containsVehicleBound, isVehicleCanBeCustomized
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResPureDialogBuilder, ResSimpleDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.lobby.customization.customization_cart.customization_cart_view import CustomizationCartView
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import events
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showProgressiveItemsView
from gui.shared.event_dispatcher import tryToShowReplaceExistingStyleDialog
from gui.shared.formatters import formatPrice, formatPurchaseItems, text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType, ApplyArea
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_outfit.outfit import Area
from constants import NC_MESSAGE_PRIORITY
_logger = logging.getLogger(__name__)

class _ModalWindowsPopupHandler(IViewLifecycleHandler):
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DYNAMIC = (VIEW_ALIAS.SIMPLE_DIALOG,
     CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG,
     R.views.lobby.customization.CustomizationCart(),
     R.views.lobby.customization.progressive_items_view.ProgressiveItemsView())

    def __init__(self, onViewCreatedCallback, onViewDestroyedCallback):
        super(_ModalWindowsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DYNAMIC ])
        self.__viewStack = []
        self.__onViewCreatedCallback = onViewCreatedCallback
        self.__onViewDestroyedCallback = onViewDestroyedCallback

    def onViewCreated(self, view):
        self.__onViewCreatedCallback()
        self.__viewStack.append(view.key)

    def onViewDestroyed(self, _):
        if self.__viewStack:
            self.__viewStack.pop()
            if not self.__viewStack:
                self.__onViewDestroyedCallback()


CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'typeRegions'))
CustomizationAnchorsStateVO = namedtuple('CustomizationAnchorsStateVO', ('uid', 'value'))
CustomizationAnchorsSetVO = namedtuple('CustomizationAnchorsSetVO', ('rendererList',))
CustomizationAnchorPositionVO = namedtuple('CustomizationAnchorPositionVO', ('zIndex', 'slotId'))
AnchorPositionData = namedtuple('AnchorPositionData', ('angleToCamera', 'clipSpacePos', 'slotId'))
_WAITING_MESSAGE = 'loadHangarSpace'

class _SeasonSoundAnimation(object):

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


class _VehicleSlotSelector(object):
    __service = dependency.descriptor(ICustomizationService)
    __CLICKS_TO_SELECT_SLOT = 2

    def __init__(self):
        self.__selectionCount = 0
        self.__prevSelectedSlot = None
        self.__ctx = self.__service.getCtx()
        return

    def selectItem(self, intCD):
        self.__selectionCount = 0
        self.__prevSelectedSlot = None
        return

    def unselectItem(self):
        self.__selectionCount = 0
        self.__prevSelectedSlot = None
        return

    def selectSlot(self, slotId):
        if self.__ctx.mode.selectedItem is not None:
            if self.__prevSelectedSlot == slotId:
                self.__selectionCount += 1
            else:
                self.__selectionCount = 1
        self.__prevSelectedSlot = slotId
        if self.__selectionCount == self.__CLICKS_TO_SELECT_SLOT:
            self.__ctx.mode.unselectItem()
        self.__ctx.mode.selectSlot(slotId)
        return

    def unselectSlot(self):
        self.__ctx.mode.unselectSlot()


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

    def __init__(self, ctx=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.__propertiesSheet = None
        self.__styleInfo = None
        self.__bottomPanel = None
        self._seasonSoundAnimation = None
        self.__ctx = None
        self.__viewCtx = ctx or {}
        self.__renderEnv = None
        self.__initAnchorsPositionsCallback = None
        self.__selectedSlot = C11nId()
        self.__locateCameraToStyleInfo = False
        self.__carouselArrowsHintShown = False
        self.__dontPlayTabChangeSound = False
        self.__itemsGrabMode = False
        self.__finishGrabModeCallback = None
        self.__closeConfirmatorHelper = CloseConfirmatorsHelper()
        self.__closed = False
        return

    @async
    def showBuyWindow(self, ctx=None):
        if self.__propertiesSheet.handleBuyWindow():
            return
        isGamefaceBuyViewOpened = self.__isGamefaceBuyViewOpened()
        if isGamefaceBuyViewOpened:
            self.changeVisible(False)
        if self.__hasOpenedChildWindow():
            return
        purchaseItems = self.__ctx.mode.getPurchaseItems()
        cart = getTotalPurchaseInfo(purchaseItems)
        if cart.totalPrice == ITEM_PRICE_EMPTY:
            positive = yield await(tryToShowReplaceExistingStyleDialog(self))
            if not positive:
                self.onBuyConfirmed(False)
                return
            if containsVehicleBound(purchaseItems):
                self.__ctx.mode.unselectSlot()
                builder = ResSimpleDialogBuilder()
                builder.setPreset(DialogPresets.CUSTOMIZATION_INSTALL_BOUND)
                builder.setMessagesAndButtons(R.strings.dialogs.customization.change_install_bound)
                isOk = yield await(dialogs.showSimple(builder.build(self)))
                self.onBuyConfirmed(isOk)
            else:
                self.__applyItems(purchaseItems)
                if self.__styleInfo.visible:
                    self.__styleInfo.disableBlur()
        else:
            if isGamefaceBuyViewOpened:
                _logger.debug('Gameface customization cart is already opened, ignore event')
                return
            _logger.info('Gameface customization cart is opened')
            ctx = ctx or {}
            ctx.update(c11nView=self)
            self.fireEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.customization.CustomizationCart(), CustomizationCartView, ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)

    def onProgressionEntryPointClick(self):
        showProgressiveItemsView()

    def __onVehicleChangeStarted(self):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleChanged(self):
        self.__closed = False
        self.__locateCameraToStyleInfo = False
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        if self.__styleInfo is not None and self.__styleInfo.visible:
            self.__ctx.events.onHideStyleInfo()
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__initAnchorsPositionsCallback = BigWorld.callback(0.0, self.__initAnchorsPositions)
        return

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        self.__onVehicleLoadFinishedEvent()
        self.__onVehicleLoadFinishedEvent = Event()
        if self.__ctx.c11nCameraManager is None:
            _logger.warning('Missing customization camera manager')
            return
        else:
            if self.__locateCameraToStyleInfo:
                self.__locateCameraToStyleInfo = False
                self.__ctx.c11nCameraManager.locateCameraToStyleInfoPreview()
            return

    def __initAnchorsPositions(self):
        entity = self.__ctx.c11nCameraManager.vEntity
        self.__initAnchorsPositionsCallback = None
        if entity is not None:
            if entity.isVehicleLoaded:
                entity.appearance.updateAnchorsParams()
            else:
                self.__initAnchorsPositionsCallback = BigWorld.callback(0.0, self.__initAnchorsPositions)
                return
        self.__setAnchorsInitData()
        self.__locateCameraToCustomizationPreview(updateTankCentralPoint=True, forceLocate=True)
        return

    def onBuyConfirmed(self, isOk):
        if isOk:
            self.soundManager.playInstantSound(SOUNDS.SELECT)
            purchaseItems = self.__ctx.mode.getPurchaseItems()
            self.__applyItems(purchaseItems)
        else:
            self.changeVisible(True)
            self.__locateCameraToCustomizationPreview()
            self.service.resumeHighlighter()

    def onPressClearBtn(self):
        if self.__propertiesSheet is not None:
            self.__propertiesSheet.hide()
        self.__ctx.mode.cancelChanges()
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            self.__ctx.changeMode(CustomizationModes.STYLED)
            self.__ctx.mode.cancelChanges()
        return

    def onPressEscBtn(self):
        if self.__propertiesSheet.handleEscBtn():
            return
        else:
            progressiveView = self.__getProgressiveView()
            if self.__ctx.mode.selectedItem is not None:
                self.__ctx.mode.unselectItem()
            elif self.__ctx.mode.selectedSlot is not None:
                self.__ctx.mode.unselectSlot()
            elif self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
                self.__dontPlayTabChangeSound = True
                self.__ctx.changeMode(CustomizationModes.STYLED)
            elif progressiveView is not None:
                progressiveView.destroyWindow()
            else:
                self.onCloseWindow()
            return

    def onPressSelectNextItem(self, reverse=False):
        if self.__hasOpenedChildWindow():
            return
        self.soundManager.playInstantSound(SOUNDS.SELECT)
        self.__ctx.events.onInstallNextCarouselItem(reverse)
        self.__tryHideCarouselArrowsHint()

    def changeVisible(self, value):
        if self.isDisposed():
            return
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()
        self.as_hideS(value)

    def onReleaseItem(self):
        self.__ctx.mode.unselectItem()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET:
            self.__propertiesSheet = viewPy
        elif alias == VIEW_ALIAS.CUSTOMIZATION_STYLE_INFO:
            self.__styleInfo = viewPy
        elif alias == VIEW_ALIAS.CUSTOMIZATION_BOTTOM_PANEL:
            self.__bottomPanel = viewPy

    def changeSeason(self, seasonIdx, needToKeepSelect):
        item = self.__ctx.mode.selectedItem
        if seasonIdx in SEASON_IDX_TO_TYPE:
            season = SEASON_IDX_TO_TYPE[seasonIdx]
        else:
            season = SeasonType.UNDEFINED
            _logger.error('Wrong season index %(seasonIdx)d', {'seasonIdx': seasonIdx})
        if not self.__styleInfo.visible:
            self.__ctx.mode.unselectSlot()
            if item is not None and not item.season & season:
                self.__ctx.mode.unselectItem()
        self.__ctx.changeSeason(season)
        if self.__styleInfo.visible:
            return
        else:
            if item is not None and self.__bottomPanel.isItemUnsuitable(item):
                self.__ctx.mode.unselectItem()
                needToKeepSelect = False
            if item is not None and needToKeepSelect:
                itemDataVO = buildCustomizationItemDataVO(item=item, progressionLevel=self.__ctx.mode.storedProgressionLevel, vehicle=g_currentVehicle.item)
                self.as_reselectS(itemDataVO)
            return

    def __onSeasonChanged(self, seasonType):
        seasonName = SEASON_TYPE_TO_NAME.get(seasonType)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.__setAnchorsInitData(update=True)
        self.__setHeaderInitData()
        self.__setNotificationCounters()

    def __onBeforeModeChanged(self):
        self.__dontPlayTabChangeSound = True

    def __onModeChanged(self, modeId, prevModeId):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.__dontPlayTabChangeSound = True
        if modeId == CustomizationModes.EDITABLE_STYLE:
            self.soundManager.playInstantSound(SOUNDS.EDIT_MODE_SWITCH_ON)
        elif prevModeId == CustomizationModes.EDITABLE_STYLE:
            self.soundManager.playInstantSound(SOUNDS.EDIT_MODE_SWITCH_OFF)
        self.__setSeasonData(forceAnim=not (modeId == CustomizationModes.EDITABLE_STYLE and prevModeId == CustomizationModes.STYLED or modeId == CustomizationModes.STYLED and prevModeId == CustomizationModes.EDITABLE_STYLE))

    def __onTabChanged(self, tabIndex, itemCD=None):
        if self.__dontPlayTabChangeSound:
            self.__dontPlayTabChangeSound = False
        else:
            self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.service.stopHighlighter()
        if self.__ctx.mode.isRegion:
            slotType = self.__ctx.mode.slotType
            modeId = self.__ctx.modeId
            highlightingMode = chooseMode(slotType, modeId, g_currentVehicle.item)
            self.service.startHighlighter(highlightingMode)
        if self.__ctx.c11nCameraManager is not None:
            self.__locateCameraToCustomizationPreview(preserveAngles=True)
        self.__setAnchorsInitData()
        self.__updateAnchorsData()
        self.__updateDnd()
        self.__setHeaderInitData()
        self.__setNotificationCounters()
        self.__tryHideCarouselArrowsHint()
        return

    def __onItemsInstalled(self, item, slotId, season, component):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        if self.__ctx.mode.selectedItem is not None:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
            if self.__ctx.mode.isRegion:
                outfit = self.__ctx.mode.currentOutfit
                slotType = CustomizationTabs.SLOT_TYPES[self.__ctx.mode.tabId]
                emptyRegions = getEmptyRegions(outfit, slotType)
                self.service.highlightRegions(emptyRegions)
            if component is not None and not component.isFilled():
                BigWorld.callback(0.0, lambda : self.__selectSlot(slotId))
        elif slotId == self.__ctx.mode.selectedSlot:
            if season is None or season == self.__ctx.season:
                self.soundManager.playInstantSound(SOUNDS.APPLY)
            self.__locateCameraOnAnchor(slotId)
        return

    def __selectSlot(self, slotId):
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.selectSlot(slotId)

    def __onItemLimitReached(self, item):
        self.as_releaseItemS()

    def __onItemsRemoved(self, slotId=None):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        item = self.__ctx.mode.getItemFromSlot(self.__selectedSlot)
        if item is None and (slotId is None or slotId == self.__ctx.mode.selectedSlot):
            self.__ctx.mode.unselectSlot()
        return

    def fadeOutAnchors(self, isFadeOut):
        self.fadeAnchorsOut = isFadeOut

    def onCloseWindow(self, force=False):
        if self.isDisposed():
            return
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()
        if force:
            self.__onCloseWindow()
        else:
            self.__confirmClose()

    def onLobbyClick(self):
        if self.__ctx.mode.isRegion:
            return
        if self.__propertiesSheet.handleLobbyClick():
            return
        self.__ctx.mode.unselectSlot()
        self.as_releaseItemS()

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
        slotId = C11nId(areaId, slotType, regionIdx)
        anchorState = self.__ctx.vehicleAnchorsUpdater.getAnchorState(slotId)
        if anchorState == CUSTOMIZATION_ALIASES.ANCHOR_STATE_REMOVED:
            self.__ctx.mode.removeItem(slotId)
            self.onHoverAnchor(areaId, slotType, regionIdx, hover=True)
            return
        self.__slotSelector.selectSlot(slotId)

    def onHoverAnchor(self, areaID, slotID, regionID, hover):
        slotId = C11nId(areaID, slotID, regionID)
        if hover:
            self.__ctx.events.onAnchorHovered(slotId)
        else:
            self.__ctx.events.onAnchorUnhovered(slotId)

    def onDragAnchor(self, areaID, slotID, regionID):
        slotId = C11nId(areaID, slotID, regionID)
        if slotId.slotType not in (GUI_ITEM_TYPE.PROJECTION_DECAL, GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
            return
        elif self.__ctx.mode.selectedItem is not None or self.__ctx.mode.selectedSlot is not None:
            return
        else:
            item = self.__ctx.mode.getItemFromSlot(slotId)
            if item is not None:
                component = self.__ctx.mode.getComponentFromSlot(slotId)
                progressionLevel = item.getUsedProgressionLevel(component)
                self.__ctx.mode.removeItem(slotId)
                itemDataVO = buildCustomizationItemDataVO(item=item, progressionLevel=progressionLevel, vehicle=g_currentVehicle.item)
                self.as_attachToCursorS(itemDataVO)
            return

    def resetC11nItemsNovelty(self, itemsList):
        self.__ctx.resetItemsNovelty(itemsList)

    def __locateCameraOnAnchor(self, slotId, forceRotate=False):
        if self.__ctx.c11nCameraManager is None:
            return
        else:
            self.__updateAnchorsData()
            anchorParams = self.__ctx.mode.getAnchorParams(slotId)
            if anchorParams is None:
                _logger.warning('Anchor params not found for slot: %s', slotId)
                return
            if slotId.slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
                if slotId.slotType == GUI_ITEM_TYPE.EMBLEM:
                    relativeSize = MainView._ZOOM_ON_EMBLEM
                else:
                    relativeSize = MainView._ZOOM_ON_INSCRIPTION
                located = self.__ctx.c11nCameraManager.locateCameraOnDecal(location=anchorParams.location, width=anchorParams.descriptor.size, slotId=anchorParams.id, relativeSize=relativeSize, forceRotate=forceRotate)
            else:
                if slotId.slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
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
                located = self.__ctx.c11nCameraManager.locateCameraOnAnchor(position=anchorParams.location.position, normal=normal, up=anchorParams.location.up, slotId=anchorParams.id, forceRotate=forceRotate)
            if located and not forceRotate:
                self.__selectedSlot = slotId
                self.__propertiesSheet.locateOnAnchor(slotId)
                self.__ctx.vehicleAnchorsUpdater.onCameraLocated(self.__selectedSlot)
            return

    def __locateCameraToCustomizationPreview(self, **kwargs):
        if self.__ctx.c11nCameraManager is None:
            return
        else:
            self.__ctx.c11nCameraManager.locateCameraToCustomizationPreview(**kwargs)
            self.__selectedSlot = C11nId()
            self.__propertiesSheet.locateToCustomizationPreview()
            self.__ctx.vehicleAnchorsUpdater.onCameraLocated()
            return

    def __onItemsBought(self, originalOutfits, purchaseItems, results):
        if results:
            if not self.__checkPurchaseSuccess(results):
                _logger.error('Failed to purchase customization outfits.')
                return
            cart = getTotalPurchaseInfo(purchaseItems)
            if cart.totalPrice != ITEM_PRICE_EMPTY:
                currency = cart.totalPrice.getCurrency(byWeight=True)
                msgText = self.__getPurchaseMessage(cart, purchaseItems)
                msgType = CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.PurchaseForGold)
                priority = NC_MESSAGE_PRIORITY.DEFAULT if currency != Currency.CREDITS else None
            else:
                modifiedOutfits = self.__ctx.mode.getModifiedOutfits()
                msgText = self.__getModifyMessage(originalOutfits, modifiedOutfits)
                msgType = SM_TYPE.Information
                priority = None
            if msgText is not None:
                SystemMessages.pushMessage(text=msgText, type=msgType, priority=priority)
        self.__onCloseWindow()
        return

    def __checkPurchaseSuccess(self, results):
        success = True
        for result in results:
            success &= result.success
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

        return success

    def __getPurchaseMessage(self, cart, purchaseItems):
        msgKey = R.strings.messenger.serviceChannelMessages.sysMsg.customization
        money = formatPrice(cart.totalPrice.price)
        if cart.boughtCount == 1:
            pItem = findFirst(lambda i: not i.isFromInventory, purchaseItems)
            if pItem is None:
                _logger.error('Failed to construct customization purchase system message. Missing purchase item.')
                return
            item = pItem.item
            isStyle = item.itemTypeID == GUI_ITEM_TYPE.STYLE
            if isStyle and item.isProgression:
                msgKey = msgKey.buyProgressionStyle()
                msgCtx = {'name': item.userName,
                 'level': int2roman(self.__ctx.mode.getStyleProgressionLevel()),
                 'money': money}
            else:
                msgKey = msgKey.buyOne()
                itemTypeName = backport.text(R.strings.item_types.customization.style()) if isStyle else item.userType
                msgCtx = {'itemType': itemTypeName,
                 'itemName': item.userName,
                 'money': money}
        else:
            msgKey = msgKey.buyMany()
            msgCtx = {'items': formatPurchaseItems(purchaseItems),
             'money': money}
        return backport.text(msgKey, **msgCtx)

    def __getModifyMessage(self, originalOutfits, modifiedOutfits):
        forwardDiffs = False
        backwardDiffs = False
        for season in SeasonType.COMMON_SEASONS:
            originalOutfit = originalOutfits[season]
            modifiedOutfit = modifiedOutfits[season]
            forwardDiffs |= not originalOutfit.diff(modifiedOutfit).isEmpty()
            backwardDiffs |= not modifiedOutfit.diff(originalOutfit).isEmpty()

        originalProgression = originalOutfits[SeasonType.SUMMER].progressionLevel
        modifiedProgression = modifiedOutfits[SeasonType.SUMMER].progressionLevel
        isStyleProgressionLevelChanged = originalProgression != modifiedProgression
        hasModifications = forwardDiffs or isStyleProgressionLevelChanged
        hasRemovalsOnly = not hasModifications and backwardDiffs
        msgKey = R.strings.messenger.serviceChannelMessages.sysMsg.customization
        if hasModifications:
            msgText = backport.text(msgKey.change())
        elif hasRemovalsOnly:
            msgText = backport.text(msgKey.remove())
        else:
            _logger.error('Failed to construct customization purchase system message. Missing outfits diff.')
            msgText = None
        return msgText

    def onAnchorsShown(self, anchors):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.isVehicleLoaded:
            self.__setAnchors(anchors)
        else:
            self.__onVehicleLoadFinishedEvent += lambda : self.__setAnchors(anchors)

    def __setAnchors(self, anchors):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setAnchors(anchors)
        return

    def propertiesSheetSet(self, sheet, width, height, centerX, centerY):
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMenuParams(sheet, width, height, centerX, centerY)
        return

    def _populate(self):
        self._invalidate(self.__viewCtx)
        super(MainView, self)._populate()
        self.__ctx = self.service.getCtx()
        self.__selectFirstVisibleTab()
        self.__ctx.events.onSeasonChanged += self.__onSeasonChanged
        self.__ctx.events.onBeforeModeChange += self.__onBeforeModeChanged
        self.__ctx.events.onModeChanged += self.__onModeChanged
        self.__ctx.events.onTabChanged += self.__onTabChanged
        self.__ctx.events.onItemInstalled += self.__onItemsInstalled
        self.__ctx.events.onItemLimitReached += self.__onItemLimitReached
        self.__ctx.events.onItemsRemoved += self.__onItemsRemoved
        self.__ctx.events.onItemsBought += self.__onItemsBought
        self.__ctx.events.onCacheResync += self.__onCacheResync
        self.__ctx.events.onChangesCanceled += self.__onChangesCanceled
        self.__ctx.events.onItemSelected += self.__onItemSelected
        self.__ctx.events.onItemUnselected += self.__onItemUnselected
        self.__ctx.events.onPropertySheetHidden += self.__onPropertySheetHidden
        self.__ctx.events.onPropertySheetShown += self.__onPropertySheetShown
        self.__ctx.events.onProlongStyleRent += self.__onProlongStyleRent
        self.__ctx.events.onShowStyleInfo += self.__onShowStyleInfo
        self.__ctx.events.onHideStyleInfo += self.__onHideStyleInfo
        self.__ctx.events.onEditModeEnabled += self.__onEditModeEnabled
        self.__ctx.events.onGetItemBackToHand += self.__onGetItemBackToHand
        self.__ctx.events.onSlotSelected += self.__onSlotSelected
        self.__ctx.events.onSlotUnselected += self.__onSlotUnselected
        self.__ctx.events.onAnchorsStateChanged += self.__onAnchorsStateChanged
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_ModalWindowsPopupHandler(self.__onViewCreatedCallback, self.__onViewDestroyedCallback)])
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        self._seasonSoundAnimation = _SeasonSoundAnimation(len(SeasonType.COMMON_SEASONS), self.soundManager)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__ctx.refreshOutfit()
        self.__onVehicleLoadFinishedEvent = Event()
        self.as_selectSeasonS(SEASON_TYPE_TO_IDX[self.__ctx.season])
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ONLINE_COUNTER}), EVENT_BUS_SCOPE.LOBBY)
        if self.__ctx.c11nCameraManager is not None:
            self.__ctx.c11nCameraManager.locateCameraToCustomizationPreview(forceLocate=True)
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        self.__renderEnv.enable(True)
        if self.__ctx.vehicleAnchorsUpdater is not None:
            self.__ctx.vehicleAnchorsUpdater.setMainView(self.flashObject)
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
            entity.appearance.turretRotator.onTurretRotated += self.__onTurretAndGunRotated
        self.__slotSelector = _VehicleSlotSelector()
        BigWorld.callback(0.0, self.__initAnchorsPositions)
        BigWorld.callback(0.0, self.__setNotificationCounters)
        if self.__ctx.mode.isRegion:
            highlightingMode = chooseMode(self.__ctx.mode.slotType, self.__ctx.modeId, g_currentVehicle.item)
            self.service.startHighlighter(highlightingMode)
        self.as_progressionEntryPointVisibleS(any((g_currentVehicle.item.getAnchors(GUI_ITEM_TYPE.PROJECTION_DECAL, areaId) for areaId in Area.ALL)))
        self.__closeConfirmatorHelper.start(self.__closeConfirmator)
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
            entity.appearance.turretRotator.onTurretRotated -= self.__onTurretAndGunRotated
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__ctx.c11nCameraManager is not None:
            self.__ctx.c11nCameraManager.locateCameraToStartState()
        if self.__styleInfo is not None:
            self.__styleInfo.disableBlur()
            self.__disableStyleInfoSound()
        self._seasonSoundAnimation = None
        self.__renderEnv.enable(False)
        self.__renderEnv = None
        self.__viewLifecycleWatcher.stop()
        self.__viewLifecycleWatcher = None
        self.service.stopHighlighter()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh -= self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted -= self.__onRegionHighlighted
        if g_currentVehicle.isPresent():
            g_tankActiveCamouflage[g_currentVehicle.item.intCD] = self.__ctx.season
            g_currentVehicle.refreshModel()
        self.__propertiesSheet = None
        self.__styleInfo = None
        self.__bottomPanel = None
        self.__ctx.events.onPropertySheetShown -= self.__onPropertySheetShown
        self.__ctx.events.onPropertySheetHidden -= self.__onPropertySheetHidden
        self.__ctx.events.onItemSelected -= self.__onItemSelected
        self.__ctx.events.onItemUnselected -= self.__onItemUnselected
        self.__ctx.events.onChangesCanceled -= self.__onChangesCanceled
        self.__ctx.events.onCacheResync -= self.__onCacheResync
        self.__ctx.events.onItemsBought -= self.__onItemsBought
        self.__ctx.events.onItemsRemoved -= self.__onItemsRemoved
        self.__ctx.events.onItemInstalled -= self.__onItemsInstalled
        self.__ctx.events.onItemLimitReached -= self.__onItemLimitReached
        self.__ctx.events.onTabChanged -= self.__onTabChanged
        self.__ctx.events.onBeforeModeChange -= self.__onBeforeModeChanged
        self.__ctx.events.onModeChanged -= self.__onModeChanged
        self.__ctx.events.onSeasonChanged -= self.__onSeasonChanged
        self.__ctx.events.onProlongStyleRent -= self.__onProlongStyleRent
        self.__ctx.events.onShowStyleInfo -= self.__onShowStyleInfo
        self.__ctx.events.onHideStyleInfo -= self.__onHideStyleInfo
        self.__ctx.events.onEditModeEnabled -= self.__onEditModeEnabled
        self.__ctx.events.onGetItemBackToHand -= self.__onGetItemBackToHand
        self.__ctx.events.onSlotSelected -= self.__onSlotSelected
        self.__ctx.events.onSlotUnselected -= self.__onSlotUnselected
        self.__ctx.events.onAnchorsStateChanged -= self.__onAnchorsStateChanged
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        if self.__initAnchorsPositionsCallback is not None:
            BigWorld.cancelCallback(self.__initAnchorsPositionsCallback)
            self.__initAnchorsPositionsCallback = None
        super(MainView, self)._dispose()
        self.__ctx = None
        self.service.closeCustomization()
        self.__closeConfirmatorHelper.stop()
        if self.__itemsGrabMode:
            self.__clearGrabModeCallback()
            self.__finishGrabMode()
        return

    def _getUpdatedAnchorsData(self):
        anchorVOs = self.__ctx.mode.getAnchorVOs()
        anchorPositionVOs = []
        for zIdx, anchorVO in enumerate(anchorVOs):
            anchorPositionVOs.append(CustomizationAnchorPositionVO(zIdx, anchorVO['slotId'])._asdict())

        return CustomizationAnchorsSetVO(anchorPositionVOs)._asdict()

    def __selectFirstVisibleTab(self):
        visibleTabs = self.__bottomPanel.getVisibleTabs()
        if visibleTabs:
            self.__ctx.mode.changeTab(visibleTabs[0])
        else:
            _logger.info('There is no visible customization tabs for current vehicle: %s', g_currentVehicle.item)

    def __updateAnchorsData(self):
        self.as_setAnchorsDataS(self._getUpdatedAnchorsData())

    def __onRegionHighlighted(self, areaId, regionIdx, highlightingType, highlightingResult):
        if self.__ctx.mode.tabId in (CustomizationTabs.MODIFICATIONS, CustomizationTabs.STYLES):
            areaId = Area.MISC
        slotType = self.__ctx.mode.slotType
        if areaId != -1 and regionIdx != -1:
            region = C11nId(areaId, slotType, regionIdx)._asdict()
        else:
            region = None
        areaMouseBehavior = self.__ctx.mode.isRegion if self.service.isOver3dScene else False
        self.as_onRegionHighlightedS(region, highlightingType, highlightingResult, areaMouseBehavior)
        if highlightingType:
            if highlightingResult:
                slotId = C11nId(areaId, slotType, regionIdx)
                self.__slotSelector.selectSlot(slotId)
            else:
                self.__ctx.mode.unselectItem()
                self.__ctx.mode.unselectSlot()
        elif highlightingResult:
            self.soundManager.playInstantSound(SOUNDS.HOVER)
        return

    def __onSpaceCreateHandler(self):
        Waiting.hide(_WAITING_MESSAGE)
        self.__ctx.refreshOutfit()
        self.__updateAnchorsData()

    def __onSpaceDestroyHandler(self, _):
        Waiting.hide(_WAITING_MESSAGE)
        self.__onCloseWindow(immediate=True)

    def __onSpaceRefreshHandler(self):
        Waiting.show(_WAITING_MESSAGE)

    def __onCloseWindow(self, immediate=False):
        if self.__closed:
            return
        self.__closed = True
        if not immediate:
            self.__ctx.mode.unselectItem()
            self.__ctx.mode.unselectSlot()
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onCacheResync(self, *_):
        if not g_currentVehicle.isPresent():
            self.__onCloseWindow()
            return
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setNotificationCounters()

    def __onChangesCanceled(self):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        self.__ctx.mode.unselectItem()
        self.__ctx.mode.unselectSlot()

    def __onItemSelected(self, intCD):
        self.__slotSelector.selectItem(intCD)
        if self.__ctx.mode.selectedItem is not None:
            if not self.__itemsGrabMode:
                self.__itemsGrabMode = True
                self.soundManager.playInstantSound(SOUNDS.PICK)
            else:
                self.__clearGrabModeCallback()
        if self.__ctx.mode.isRegion:
            outfit = self.__ctx.mode.currentOutfit
            slotType = self.__ctx.mode.slotType
            emptyRegions = getEmptyRegions(outfit, slotType)
            self.service.highlightRegions(emptyRegions)
        self.__updateDnd()
        return

    def __onItemUnselected(self):
        self.__slotSelector.unselectItem()
        if self.__itemsGrabMode:
            self.__clearGrabModeCallback()
            self.__finishGrabModeCallback = BigWorld.callback(0.5, self.__finishGrabMode)
            self.as_releaseItemS()
        if self.__ctx.mode.isRegion:
            self.service.highlightRegions(ApplyArea.NONE)
        self.__updateDnd()

    def __finishGrabMode(self):
        self.__finishGrabModeCallback = None
        self.__itemsGrabMode = False
        self.soundManager.playInstantSound(SOUNDS.RELEASE)
        return

    def __clearGrabModeCallback(self):
        if self.__finishGrabModeCallback is not None:
            BigWorld.cancelCallback(self.__finishGrabModeCallback)
            self.__finishGrabModeCallback = None
        return

    def __onSlotSelected(self, slotId):
        if self.__ctx.mode.isRegion:
            if self.__ctx.mode.tabId in (CustomizationTabs.MODIFICATIONS, CustomizationTabs.STYLES):
                applyArea = ApplyArea.ALL
            else:
                applyArea = appliedToFromSlotsIds([slotId])
            self.service.selectRegions(applyArea)
            item = self.__ctx.mode.getItemFromSlot(slotId)
            if item is not None:
                self.__locateCameraOnAnchor(slotId)
            else:
                self.__locateCameraToCustomizationPreview(preserveAngles=True)
        else:
            self.__locateCameraOnAnchor(slotId)
        self.__updateDnd()
        return

    def __onSlotUnselected(self):
        self.__locateCameraToCustomizationPreview(preserveAngles=True)
        self.__updateAnchorsData()
        if self.__ctx.mode.isRegion:
            self.service.selectRegions(ApplyArea.NONE)
        self.__updateDnd()

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onCloseWindow()

    def __onPropertySheetShown(self, slotId):
        self.__updateDnd()
        c11nSettings = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
        if not c11nSettings.get(CAROUSEL_ARROWS_HINT_SHOWN_FIELD, False) and not self.__propertiesSheet.inEditMode:
            self.as_showCarouselsArrowsNotificationS(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_KEYBOARD_HINT)
            self.__carouselArrowsHintShown = True

    def __tryHideCarouselArrowsHint(self):
        if self.__carouselArrowsHintShown:
            c11nSettings = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
            c11nSettings[CAROUSEL_ARROWS_HINT_SHOWN_FIELD] = True
            AccountSettings.setSettings(CUSTOMIZATION_SECTION, c11nSettings)

    def __onPropertySheetHidden(self):
        if self.__ctx.mode.isRegion:
            self.service.resetHighlighting()
        self.__updateDnd()

    def __updateDnd(self):
        isDndEnable = True
        if self.__propertiesSheet.visible:
            isDndEnable = False
        if self.__ctx.mode.tabId in (CustomizationTabs.MODIFICATIONS, CustomizationTabs.STYLES):
            isDndEnable = False
        self.as_enableDNDS(isDndEnable)

    def __setSeasonData(self, forceAnim=False):
        seasonRenderersList = []
        filledSeasonSlots = 0
        for season in SEASONS_ORDER:
            seasonName = SEASON_TYPE_TO_NAME.get(season)
            isFilled = False
            if self.__ctx.modeId == CustomizationModes.CUSTOM:
                isFilled = False
                outfit = self.__ctx.mode.getModifiedOutfit(season)
                visibleTabs = self.__bottomPanel.getVisibleTabs()
                slotTypes = (CustomizationTabs.SLOT_TYPES[tabId] for tabId in visibleTabs)
                for slotType in slotTypes:
                    slotsCount, filledSlotsSlots = checkSlotsFilling(outfit, slotType)
                    if filledSlotsSlots < slotsCount:
                        break
                else:
                    isFilled = True

            elif self.__ctx.modeId in (CustomizationModes.STYLED, CustomizationModes.EDITABLE_STYLE):
                isFilled = self.__ctx.mode.currentOutfit.style is not None
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
        self._seasonSoundAnimation.setFilledSeasonSlots(filledSeasonSlots, forceAnim)
        return

    def __setNotificationCounters(self):
        seasonCounters = {season:0 for season in SEASONS_ORDER}
        if self.__ctx.modeId == CustomizationModes.STYLED:
            itemTypes = (GUI_ITEM_TYPE.STYLE,)
        else:
            itemTypes = getItemTypesAvailableForVehicle() - {GUI_ITEM_TYPE.STYLE}
        if self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            itemsFilter = lambda item: self.__ctx.mode.style.isItemInstallable(item) and not item.isAllSeason()
        else:
            itemsFilter = lambda item: not item.isAllSeason()
        for season in SEASONS_ORDER:
            if self.__ctx.season != season:
                seasonCounters[season] = g_currentVehicle.item.getC11nItemsNoveltyCounter(g_currentVehicle.itemsCache.items, itemTypes, season, itemsFilter)
            seasonCounters[season] = 0

        self.as_setNotificationCountersS([ seasonCounters[season] for season in SEASONS_ORDER ])

    def __setAnchorsInitData(self, update=False):
        if not g_currentVehicle.isPresent():
            _logger.warning('There is no vehicle in hangar for customization.')
            return
        anchorVOs = self.__ctx.mode.getAnchorVOs()
        if self.__ctx.mode.isRegion:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_REGION
        elif self.__ctx.mode.tabId == CustomizationTabs.PROJECTION_DECALS:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_PROJECTION_DECAL
        else:
            typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_DECAL
        if update:
            self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, typeRegions)._asdict())
        else:
            self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, typeRegions)._asdict())

    def __setHeaderInitData(self):
        vehicle = g_currentVehicle.item
        slotType = self.__ctx.mode.slotType
        if self.__ctx.modeId == CustomizationModes.STYLED:
            if self.__ctx.mode.modifiedStyle is not None:
                itemsCounter = text_styles.bonusPreviewText(backport.text(R.strings.vehicle_customization.customization.header.counter.style.installed()))
            else:
                itemsCounter = text_styles.stats(backport.text(R.strings.vehicle_customization.customization.header.counter.style.notInstalled()))
        elif self.__ctx.modeId == CustomizationModes.EDITABLE_STYLE:
            itemsCounter = text_styles.bonusPreviewText(backport.text(R.strings.vehicle_customization.customization.header.counter.editablestyle.installed(), name=self.__ctx.mode.style.userName))
        elif isVehicleCanBeCustomized(g_currentVehicle.item, slotType):
            typeName = GUI_ITEM_TYPE_NAMES[slotType]
            outfit = self.__ctx.mode.currentOutfit
            slotsCount, filledSlotsCount = checkSlotsFilling(outfit, slotType)
            textStyle = text_styles.bonusPreviewText if slotsCount == filledSlotsCount else text_styles.stats
            template = '#vehicle_customization:customization/header/counter/' + typeName
            itemsCounter = textStyle(_ms(template, filled=filledSlotsCount, available=slotsCount))
        else:
            itemsCounter = ''
        self.as_setHeaderDataS({'tankTier': str(int2roman(vehicle.level)),
         'tankName': vehicle.shortUserName,
         'tankInfo': itemsCounter,
         'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
         'isElite': vehicle.isElite,
         'closeBtnTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN})
        return

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
                    self.__ctx.c11nCameraManager.locateCameraToStyleInfoPreview()
                else:
                    self.__locateCameraToStyleInfo = True
            return

    def __onHideStyleInfo(self, toBuyWindow=False):
        if self.__styleInfo is None:
            return
        else:
            self.__disableStyleInfoSound()
            self.__locateCameraToStyleInfo = False
            if toBuyWindow:
                self.changeVisible(False)
            else:
                self.__locateCameraToCustomizationPreview()
                self.service.resumeHighlighter()
            self.__styleInfo.hide()
            return

    def __disableStyleInfoSound(self):
        self.soundManager.setState(SOUNDS.STATE_STYLEINFO, SOUNDS.STATE_STYLEINFO_HIDE)
        self.soundManager.setRTPC(SOUNDS.RTPC_STYLEINFO, 0)

    def __onEditModeEnabled(self, enabled):
        if enabled and self.__selectedSlot != C11nId():
            self.__locateCameraOnAnchor(self.__selectedSlot, forceRotate=True)

    def __onGetItemBackToHand(self, item, progressionLevel=-1, scrollToItem=False):
        itemDataVO = buildCustomizationItemDataVO(item=item, progressionLevel=progressionLevel, vehicle=g_currentVehicle.item)
        self.as_attachToCursorS(itemDataVO)

    def __onViewCreatedCallback(self):
        if self.__styleInfo is not None and self.__styleInfo.visible:
            return
        else:
            self.__propertiesSheet.hide()
            self.service.suspendHighlighter()
            return

    def __onViewDestroyedCallback(self):
        if not g_currentVehicle.isPresent():
            return
        elif self.__styleInfo is not None and self.__styleInfo.visible:
            return
        else:
            self.__ctx.mode.unselectItem()
            self.__ctx.mode.unselectSlot()
            if self.__ctx.c11nCameraManager is not None and self.__ctx.c11nCameraManager.isStyleInfo():
                self.__locateCameraToCustomizationPreview(preserveAngles=True)
            self.service.resumeHighlighter()
            return

    def __onAnchorsStateChanged(self, changedStates):
        anchorStateVOs = [ CustomizationAnchorsStateVO(uid, state)._asdict() for uid, state in changedStates.iteritems() ]
        self.as_setAnchorsStateS({'anchorsData': anchorStateVOs})

    def __onTurretAndGunRotated(self):
        if self.__ctx.mode.isRegion:
            self.service.restartHighlighter()

    def __onSettingsChanged(self, diff):
        if self.__ctx.mode.isRegion and 'OBJECT_LOD' in diff:
            BigWorld.callback(0.0, self.service.restartHighlighter)

    def __hasOpenedChildWindow(self):
        views = self.guiLoader.windowsManager.findWindows(lambda w: w.parent == self.getParentWindow())
        return len(views) > 0

    def __isGamefaceBuyViewOpened(self):
        return self.guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.customization.CustomizationCart())

    def __getProgressiveView(self):
        return self.guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.customization.progressive_items_view.ProgressiveItemsView())

    @async
    def __confirmClose(self):
        if self.__hasOpenedChildWindow() or self.__isGamefaceBuyViewOpened():
            return
        yield await(self.__closeConfirmator())

    @async
    def __closeConfirmator(self):
        if self.__closed or not self.__ctx.isOutfitsModified():
            result = True
        else:
            builder = ResPureDialogBuilder()
            builder.setMessagesAndButtons(R.strings.dialogs.customization.close, focused=DialogButtons.CANCEL)
            self.__onViewCreatedCallback()
            result = yield await(dialogs.showSimple(builder.build(self)))
            self.__onViewDestroyedCallback()
        if result:
            self.__onCloseWindow()
        raise AsyncReturn(result)

    @adisp.process
    def __applyItems(self, purchaseItems):
        yield self.__ctx.applyItems(purchaseItems)
