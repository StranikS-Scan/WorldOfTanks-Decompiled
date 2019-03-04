# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import struct
from collections import namedtuple
import logging
import BigWorld
from Math import Matrix
from CurrentVehicle import g_currentVehicle
from adisp import async, process as adisp_process
from gui import DialogsInterface, g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.customization_inscription_controller import PersonalNumEditStatuses, PersonalNumEditCommands
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_SLOT_TYPE_MAPPING, DRAG_AND_DROP_INACTIVE_TABS, C11nTabs, SEASON_TYPE_TO_NAME, SEASON_IDX_TO_TYPE, SEASON_TYPE_TO_IDX, SEASONS_ORDER, getTotalPurchaseInfo, containsVehicleBound
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.daapi.view.meta.CustomizationMainViewMeta import CustomizationMainViewMeta
from gui.Scaleform.framework.entities.View import ViewKey, ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.CUSTOMIZATION_DIALOGS import CUSTOMIZATION_DIALOGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.app_loader import g_appLoader
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.customization.shared import chooseMode, getAppliedRegionsForCurrentHangarVehicle, appliedToFromSlotsIds, C11nId, QUANTITY_LIMITED_CUSTOMIZATION_TYPES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbyHeaderMenuEvent
from gui.shared.formatters import formatPrice, text_styles
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
from account_helpers.AccountSettings import AccountSettings, CUSTOMIZATION_SECTION, CAROUSEL_ARROWS_HINT_SHOWN_FIELD
_logger = logging.getLogger(__name__)

class _ModalWindowsPopupHandler(IViewLifecycleHandler):
    service = dependency.descriptor(ICustomizationService)
    __SUB_VIEWS = (VIEW_ALIAS.SETTINGS_WINDOW, VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.LOBBY_MENU)
    __DIALOGS = (VIEW_ALIAS.SIMPLE_DIALOG, CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG)

    def __init__(self, onViewPopupCallback):
        super(_ModalWindowsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__SUB_VIEWS ] + [ ViewKeyDynamic(alias) for alias in self.__DIALOGS ])
        self.__viewStack = []
        self.__onViewPopupCallback = onViewPopupCallback

    def onViewCreated(self, view):
        self.__onViewPopupCallback()
        self.__viewStack.append(view.key)
        self.service.suspendHighlighter()

    def onViewDestroyed(self, _):
        if self.__viewStack:
            self.__viewStack.pop()
            if not self.__viewStack:
                self.service.resumeHighlighter()


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


class MainView(LobbySubView, CustomizationMainViewMeta):
    __background_alpha__ = 0.0
    _COMMON_SOUND_SPACE = C11N_SOUND_SPACE
    _ZOOM_ON_EMBLEM = 0.1
    _ZOOM_ON_INSCRIPTION = 0.1
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, viewCtx=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.__locatedOnEmbelem = False
        self.itemIsPicked = False
        self.__propertiesSheet = None
        self.__styleInfo = None
        self._seasonSoundAnimantion = None
        self._isPropertySheetShown = False
        self.__ctx = None
        self.__viewCtx = viewCtx or {}
        self.__renderEnv = None
        self.__needCheckDecalsAgainstGun = True
        self.__styleInfoActive = False
        return

    def showBuyWindow(self, ctx=None):
        if self.__ctx.isOnly1ChangedNumberInEditMode():
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.FINISH_BY_CLICK)
        elif self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        if not self.__ctx.numberEditModeActive:
            self.changeVisible(False)
            purchaseItems = self.__ctx.getPurchaseItems()
            cart = getTotalPurchaseInfo(purchaseItems)
            if cart.totalPrice == ITEM_PRICE_EMPTY:
                if containsVehicleBound(purchaseItems):
                    DialogsInterface.showI18nConfirmDialog(CUSTOMIZATION_DIALOGS.CUSTOMIZATION_INSTALL_BOUND_CHECK_NOTIFICATION, self.onBuyConfirmed)
                else:
                    self.__ctx.applyItems(purchaseItems)
            else:
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)

    def __onVehicleChanged(self):
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        self.__setHeaderInitData()
        self.__setSeasonData()
        BigWorld.callback(0.0, self.__updateAnchorsPositions)

    def __updateAnchorsPositions(self):
        vEntity = self.__ctx.c11CameraManager.vEntity
        if vEntity is not None:
            vEntity.appearance.updateSlotPositions(checkDecalsAgainstGun=True)
        self.__setAnchorsInitData()
        self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(updateTankCentralPoint=True)
        self.__needCheckDecalsAgainstGun = True
        return

    def onBuyConfirmed(self, isOk):
        if isOk:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.SELECT)
            self.__ctx.applyItems(self.__ctx.getPurchaseItems())
        else:
            self.changeVisible(True)

    def onPressClearBtn(self):
        self.__ctx.cancelChanges()

    def onPressEscBtn(self):
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_BY_ESC)
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
        self.__clearSelectedAnchor()
        self.as_hideS(value)

    def onReleaseItem(self):
        self.__ctx.caruselItemUnselected()
        self.__releaseItemSound()
        if not self.__propertiesSheet.isVisible:
            self.__clearSelectedAnchor()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET:
            self.__propertiesSheet = viewPy
        elif alias == VIEW_ALIAS.CUSTOMIZATION_STYLE_INFO:
            self.__styleInfo = viewPy

    def changeSeason(self, seasonIdx, needToKeepSelect):
        currentSelected = self.__ctx.selectedCarouselItem.intCD
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        if seasonIdx in SEASON_IDX_TO_TYPE:
            self.__ctx.changeSeason(SEASON_IDX_TO_TYPE[seasonIdx])
        else:
            _logger.error('Wrong season index %(seasonIdx)d', {'seasonIdx': seasonIdx})
        if self.__ctx.isAnyAnchorSelected() and not self.__styleInfoActive:
            self.__clearSelectionAndHidePropertySheet()
            self.__hidePropertiesSheet()
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
        self.__setAnchorsInitData()
        if self.__locatedOnEmbelem and self.__ctx.c11CameraManager is not None:
            self.__ctx.c11CameraManager.clearSelectedEmblemInfo()
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview(preserveAngles=True)
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
        self.__setHeaderInitData()
        self.__setNotificationCounters()
        return

    def __onItemsInstalled(self, item, component, slotId, limitReached):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        else:
            areaId, slotType, regionIdx = self.__ctx.selectedAnchor
            startNumberEditMode = item.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component is not None and not component.isFilled() and not self.__ctx.storedPersonalNumber
            if startNumberEditMode:
                self.__ctx.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_STARTED)
            else:
                self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                self.__showPropertiesSheet(areaId, slotType, regionIdx, forceUpdate=True)
        if limitReached:
            self.as_releaseItemS()
        return

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
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.FINISH_BY_CLICK)
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
        if self.__propertiesSheet.isVisible and not self.__ctx.numberEditModeActive:
            if self.__ctx.currentTab == C11nTabs.STYLE:
                self.__ctx.removeStyle(self.__ctx.modifiedStyle.intCD)
            else:
                self.__ctx.removeItemFromSlot(self.__ctx.currentSeason, self.__ctx.selectedSlot)

    def onSelectAnchor(self, areaId, slotType, regionIdx):
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        if not self.__ctx.isCaruselItemSelected():
            self.as_enableDNDS(False)
        anchorSelected = self.__ctx.isAnchorSelected(slotType=slotType, areaId=areaId, regionIdx=regionIdx)
        itemInstalled = self.__ctx.anchorSelected(slotType, areaId, regionIdx)
        if self.__ctx.isSlotFilled(self.__ctx.selectedAnchor):
            selectedItem = self.__ctx.getItemFromSelectedRegion()
            if self.__ctx.isCaruselItemSelected():
                if anchorSelected and not itemInstalled:
                    self.__locateCameraOnAnchor(areaId, slotType, regionIdx, False)
                    self.__showPropertiesSheet(areaId, slotType, regionIdx)
                else:
                    component = self.__ctx.getComponentFromSelectedRegion()
                    startNumberEditMode = selectedItem.itemTypeID == GUI_ITEM_TYPE.PERSONAL_NUMBER and component is not None and not component.isFilled()
                    if startNumberEditMode:
                        self.__ctx.onPersonalNumberEditModeChanged(PersonalNumEditStatuses.EDIT_MODE_STARTED)
            else:
                self.__locateCameraOnAnchor(areaId, slotType, regionIdx, False)
                self.__showPropertiesSheet(areaId, slotType, regionIdx)
        else:
            self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            self.__locateCameraOnAnchor(areaId, slotType, regionIdx, False)
            self.__hidePropertiesSheet()
        self.__ctx.onSlotSelected(areaId, slotType, regionIdx)
        return

    def onLockedAnchor(self):
        self.__hidePropertiesSheet()

    def resetC11nItemsNovelty(self, itemsList):
        self.__ctx.resetC11nItemsNovelty(itemsList)

    def __locateCameraOnAnchor(self, areaId, slotType, regionIdx, disableMovement=False, forceRotate=False):
        if self.__ctx.c11CameraManager is None:
            return
        else:
            if self.__needCheckDecalsAgainstGun:
                self.__checkDecalsAgainstGun()
            self.__updateAnchorsData()
            anchorParams = self.service.getAnchorParams(areaId, slotType, regionIdx)
            turretYaw = anchorParams.turretYaw
            if slotType in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
                if slotType == GUI_ITEM_TYPE.EMBLEM:
                    emblemType = 'player'
                    zoom = MainView._ZOOM_ON_EMBLEM
                else:
                    emblemType = 'inscription'
                    zoom = MainView._ZOOM_ON_INSCRIPTION
                self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnEmblem(onHull=areaId == Area.HULL, emblemType=emblemType, emblemIdx=regionIdx, relativeSize=zoom, disableMovementByMouse=disableMovement, turretYaw=turretYaw, forceRotate=forceRotate)
            elif slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
                normal = anchorParams.normal
                if normal.dot((0.0, 1.0, 0.0)) > 0.99:
                    localPYR = anchorParams.slotDescriptor.rotation
                    worldRotation = Matrix()
                    worldRotation.setRotateYPR((localPYR.y, localPYR.x, localPYR.z))
                    vehicleMatrix = self.hangarSpace.getVehicleEntity().model.matrix
                    worldRotation.postMultiply(vehicleMatrix)
                    normal.setPitchYaw(anchorParams.normal.pitch, worldRotation.yaw)
                self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnAnchor(anchorParams.pos, normal, disableMovement, turretYaw)
            else:
                self.__locatedOnEmbelem = self.__ctx.c11CameraManager.locateCameraOnAnchor(anchorParams.pos, None, disableMovement, turretYaw)
            return

    def __checkDecalsAgainstGun(self):
        vEntity = self.__ctx.c11CameraManager.vEntity
        if vEntity is not None:
            vEntity.appearance.updateSlotPositions(checkDecalsAgainstGun=self.__needCheckDecalsAgainstGun)
            self.__needCheckDecalsAgainstGun = False
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
            propertiesSheetSlot = self.__propertiesSheet.attachedSlot if self.__propertiesSheet.isVisible else C11nId()
            self.__ctx.vehicleAnchorsUpdater.setAnchors(anchors, propertiesSheetSlot)
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
        self.__ctx.onCustomizationItemDataChanged += self.__onItemDataChanged
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
        self.__ctx.onPersonalNumberEditModeChanged += self.__onNumberEditModeChanged
        self.__ctx.onResetC11nItemsNovelty += self.__onResetC11nItemsNovelty
        self.__ctx.c11CameraManager.onTurretRotated += self.__onTurretRotated
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_ModalWindowsPopupHandler(self.__clearSelectionAndHidePropertySheet)])
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
        self._invalidate(self.__viewCtx)
        if self.__ctx.mode == C11nMode.STYLE:
            BigWorld.callback(0.0, lambda : self.__ctx.tabChanged(C11nTabs.STYLE))
        return

    def _invalidate(self, *args, **kwargs):
        super(MainView, self)._invalidate()
        callback = (args[0] or {}).get('callback')
        if callback is not None:
            callback()
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
        self.__ctx.onCustomizationItemDataChanged -= self.__onItemDataChanged
        self.__ctx.onCustomizationTabChanged -= self.__onTabChanged
        self.__ctx.onCustomizationModeChanged -= self.__onModeChanged
        self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
        self.__ctx.onClearItem -= self.__onClearItem
        self.__ctx.onProlongStyleRent -= self.__onProlongStyleRent
        self.__ctx.onShowStyleInfo -= self.__onShowStyleInfo
        self.__ctx.onStyleInfoHidden -= self.__onStyleInfoHidden
        self.__ctx.onPersonalNumberEditModeChanged -= self.__onNumberEditModeChanged
        self.__ctx.onResetC11nItemsNovelty -= self.__onResetC11nItemsNovelty
        self.__ctx.c11CameraManager.onTurretRotated -= self.__onTurretRotated
        g_currentVehicle.onChanged -= self.__onVehicleChanged
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
                self.__ctx.removeItems(True, itemIntCD)
            else:
                self.__ctx.removeStyle(itemIntCD)

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
        else:
            self.__hidePropertiesSheet()
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
                        self.__showPropertiesSheet(areaId, slotType, regionIdx)
                    else:
                        self.service.selectRegions(ApplyArea.NONE)
                        self.__hidePropertiesSheet()
                else:
                    if slotFilled:
                        self.__locateCameraOnAnchor(areaId, slotType, regionIdx)
                        self.__showPropertiesSheet(areaId, slotType, regionIdx)
                    else:
                        self.soundManager.playInstantSound(SOUNDS.CHOOSE)
                        self.__resetCameraFocus()
                        self.__hidePropertiesSheet()
                    self.service.selectRegions(applyArea)
                self.__ctx.onSlotSelected(areaId, slotType, regionIdx)
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
        self.__setNotificationCounters()

    def __onChangesCanceled(self):
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)
        self.__hidePropertiesSheet()
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

    def __onPropertySheetShown(self):
        self._isPropertySheetShown = True
        self.__updateDnd()
        if self.__ctx.currentTab in (C11nTabs.INSCRIPTION, C11nTabs.EMBLEM):
            self.__setAnchorsInitData()

    def __onPropertySheetHidden(self):
        tabIndex = self.__ctx.currentTab
        if tabIndex in C11nTabs.REGIONS:
            self.service.resetHighlighting()
        self._isPropertySheetShown = False
        self.__updateDnd()
        if self.__ctx.currentTab in (C11nTabs.INSCRIPTION, C11nTabs.EMBLEM):
            self.__setAnchorsInitData()

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
        newItems = g_currentVehicle.item.getNewC11nItems(g_currentVehicle.itemsCache.items)
        seasonCounters = {season:0 for season in SEASONS_ORDER}
        if self.__ctx.mode == C11nMode.STYLE:
            itemTypes = (GUI_ITEM_TYPE.STYLE,)
        else:
            itemTypes = GUI_ITEM_TYPE.CUSTOMIZATIONS_WITHOUT_STYLE
        for item in newItems:
            if item.season != SeasonType.ALL and item.itemTypeID in itemTypes and not item.season & currentSeason:
                seasonCounters[item.season] += 1

        self.as_setNotificationCountersS([ seasonCounters[season] for season in SEASONS_ORDER ])

    def __setAnchorsInitData(self, update=False):

        def customizationSlotIdToUid(customizationSlotIdVO):
            s = struct.pack('bbh', customizationSlotIdVO.areaId, customizationSlotIdVO.slotId, customizationSlotIdVO.regionId)
            return struct.unpack('I', s)[0]

        if not g_currentVehicle.isPresent():
            return
        else:
            tabIndex = self.__ctx.currentTab
            anchorVOs = []
            slotType = TABS_SLOT_TYPE_MAPPING[tabIndex]
            maxItemsReached = False
            visibleAnchors = self.__getVisibleAnchors(slotType)
            if tabIndex == C11nTabs.STYLE:
                anchorId = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.STYLE, 0)
                uid = customizationSlotIdToUid(anchorId)
                anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), self.__ctx.modifiedStyle.intCD if self.__ctx.modifiedStyle is not None else 0, uid, None)._asdict())
            else:
                potentialPlaceTooltip = None
                if slotType in QUANTITY_LIMITED_CUSTOMIZATION_TYPES:
                    outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
                    if self.__ctx.isC11nItemsQuantityLimitReached(outfit, slotType):
                        maxItemsReached = True
                        potentialPlaceTooltip = makeTooltip(body=VEHICLE_CUSTOMIZATION.CUSTOMIZATION_TOOLTIP_POTENTIALPROJDECALPLACE_TOLTIP_TEXT)
                for areaId in Area.ALL:
                    slot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(slotType)
                    for regionIdx, anchor in g_currentVehicle.item.getAnchors(slotType, areaId).iteritems():
                        if anchor.slotId not in visibleAnchors:
                            continue
                        anchorId = CustomizationSlotIdVO(areaId, slotType, regionIdx)
                        slotId = self.__ctx.getSlotIdByAnchorId(C11nId(areaId=areaId, slotType=slotType, regionIdx=regionIdx))
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
                        tooltip = None
                        if not itemIntCD:
                            tooltip = potentialPlaceTooltip
                        uid = customizationSlotIdToUid(anchorId)
                        anchorVOs.append(CustomizationSlotUpdateVO(anchorId._asdict(), itemIntCD, uid, tooltip)._asdict())

            isRegions = tabIndex in C11nTabs.REGIONS
            if isRegions:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_REGION
            elif tabIndex == C11nTabs.PROJECTION_DECAL:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_PROJECTION_DECAL
            else:
                typeRegions = CUSTOMIZATION_ALIASES.ANCHOR_TYPE_DECAL
            if update and isRegions:
                self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, typeRegions, maxItemsReached)._asdict())
            else:
                self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, typeRegions, maxItemsReached)._asdict())
                if self.__propertiesSheet.isVisible:
                    self.__ctx.vehicleAnchorsUpdater.changeAnchorParams(self.__ctx.selectedAnchor, isDisplayed=isRegions, isAutoScalable=False)
            return

    def __getVisibleAnchors(self, slotType):
        visibleAnchorsIds = set()
        currentVehicle = g_currentVehicle.item
        if slotType == GUI_ITEM_TYPE.PROJECTION_DECAL:
            for anchor in currentVehicle.getAnchors(GUI_ITEM_TYPE.PROJECTION_DECAL, Area.MISC).itervalues():
                if anchor.isParent:
                    visibleAnchorsIds.add(anchor.slotId)

            outfit = self.__ctx.getModifiedOutfit(self.__ctx.currentSeason)
            multySlot = outfit.getContainer(Area.MISC).slotFor(GUI_ITEM_TYPE.PROJECTION_DECAL)
            if multySlot is not None:
                for regionIdx in range(multySlot.capacity()):
                    slotData = multySlot.getSlotData(regionIdx)
                    if slotData.item is not None:
                        anchor = g_currentVehicle.item.getAnchorById(slotData.component.slotId)
                        if anchor.isParent:
                            parent = anchor
                        else:
                            parent = g_currentVehicle.item.getAnchorById(anchor.parentSlotId)
                        visibleAnchorsIds.discard(parent.slotId)
                        visibleAnchorsIds.add(anchor.slotId)

        else:
            for area in Area.ALL:
                for anchor in currentVehicle.getAnchors(slotType, area).itervalues():
                    visibleAnchorsIds.add(anchor.slotId)

        return visibleAnchorsIds

    def __onItemDataChanged(self, areaId, slotId, regionIdx, changeAnchor, updatePropertiesSheet, refreshCarousel):
        self.__setAnchorsInitData(True)
        if self._isPropertySheetShown:
            if updatePropertiesSheet:
                self.__showPropertiesSheet(areaId, slotId, regionIdx, forceUpdate=True)
            if changeAnchor:
                self.__locateCameraOnAnchor(areaId, slotId, regionIdx)
                slotIdVO = CustomizationSlotIdVO(areaId, slotId, self.__ctx.selectedAnchor.regionIdx)._asdict()
                self.as_updateSelectedRegionsS(slotIdVO)

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

    def __showPropertiesSheet(self, areaId, slotType, regionIdx, forceUpdate=False):
        if self.__propertiesSheet:
            if self.__ctx.vehicleAnchorsUpdater is not None:
                self.__ctx.vehicleAnchorsUpdater.attachMenuToAnchor(self.__ctx.selectedAnchor)
            tabIndex = self.__ctx.currentTab
            self.__propertiesSheet.show(areaId, slotType, regionIdx, tabIndex not in C11nTabs.REGIONS, tabIndex == C11nTabs.EMBLEM, forceUpdate)
            custSett = AccountSettings.getSettings(CUSTOMIZATION_SECTION)
            if not custSett.get(CAROUSEL_ARROWS_HINT_SHOWN_FIELD, False) and not self.__ctx.numberEditModeActive:
                self.as_showCarouselsArrowsNotificationS(VEHICLE_CUSTOMIZATION.PROPERTYSHEET_KEYBOARD_HINT)
                custSett[CAROUSEL_ARROWS_HINT_SHOWN_FIELD] = True
                AccountSettings.setSettings(CUSTOMIZATION_SECTION, custSett)
        return

    def __hidePropertiesSheet(self):
        if self.__propertiesSheet:
            self.__propertiesSheet.hide()

    @async
    @adisp_process
    def __confirmHeaderNavigation(self, callback):
        if self._isPropertySheetShown:
            if self.__ctx.numberEditModeActive:
                self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
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
        self.__clearSelectedAnchor()
        self.__resetUIFocus()
        self.as_releaseItemS()

    def __clearSelectedAnchor(self):
        _, slotType, _ = self.__ctx.selectedAnchor
        self.__ctx.anchorSelected(slotType, -1, -1)

    def clearSelectionAndHidePropertySheet(self):
        self.__clearSelectionAndHidePropertySheet()

    def __clearSelectionAndHidePropertySheet(self):
        if self.__ctx.numberEditModeActive:
            self.__ctx.sendNumberEditModeCommand(PersonalNumEditCommands.CANCEL_EDIT_MODE)
        if self._isPropertySheetShown:
            self.__hidePropertiesSheet()
        self.__clearItem()

    def __onProlongStyleRent(self):
        ctx = {'prolongStyleRent': True}
        self.showBuyWindow(ctx=ctx)

    def __onShowStyleInfo(self):
        if self.__styleInfo is None:
            return
        else:
            self.service.suspendHighlighter()
            self.__styleInfo.show()
            self.__ctx.c11CameraManager.locateCameraToStyleInfoPreview()
            self.__styleInfoActive = True
            return

    def __onStyleInfoHidden(self, resumeHighlighter=True):
        if self.__styleInfo is None:
            return
        else:
            if resumeHighlighter:
                self.service.resumeHighlighter()
            self.__styleInfo.hide()
            self.__ctx.c11CameraManager.locateCameraToCustomizationPreview()
            return

    def __onNumberEditModeChanged(self, state, showPropSheetAfter=True):
        slotId = self.__ctx.selectedSlot
        if state is PersonalNumEditStatuses.EDIT_MODE_STARTED:
            self.__ctx.numberEditModeActive = True
            self.__locateCameraOnAnchor(slotId.areaId, slotId.slotType, slotId.regionIdx, forceRotate=True)
            self.__showPropertiesSheet(slotId.areaId, slotId.slotType, slotId.regionIdx, forceUpdate=True)
        elif state is PersonalNumEditStatuses.EDIT_MODE_FINISHED:
            self.soundManager.playInstantSound(SOUNDS.CUST_CHOICE_ENTER)
            self.__ctx.numberEditModeActive = False
            self.__locateCameraOnAnchor(slotId.areaId, slotId.slotType, slotId.regionIdx)
            if showPropSheetAfter:
                self.__showPropertiesSheet(slotId.areaId, slotId.slotType, slotId.regionIdx, forceUpdate=True)
        elif state is PersonalNumEditStatuses.EDIT_MODE_CANCELLED:
            selectedItem = self.__ctx.getItemFromSelectedRegion()
            if self.__ctx.isAnyAnchorSelected and selectedItem and showPropSheetAfter:
                self.__showPropertiesSheet(slotId.areaId, slotId.slotType, slotId.regionIdx, forceUpdate=True)
            else:
                self.__hidePropertiesSheet()
                self.__clearItem()

    def __onResetC11nItemsNovelty(self):
        self.__setNotificationCounters()

    def __onTurretRotated(self):
        self.__setAnchorsInitData()
        tabIndex = self.__ctx.currentTab
        if tabIndex in C11nTabs.REGIONS:
            self.service.restartHighlighter()
        selectedAnchor = self.__ctx.selectedAnchor
        if selectedAnchor.regionIdx != -1:
            self.__locateCameraOnAnchor(selectedAnchor.areaId, selectedAnchor.slotType, selectedAnchor.regionIdx)
        self.__ctx.refreshOutfit()
