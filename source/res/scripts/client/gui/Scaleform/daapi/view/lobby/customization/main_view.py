# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/main_view.py
import struct
from collections import namedtuple
import BigWorld
import GUI
import Math
from CurrentVehicle import g_currentVehicle
from adisp import async, process as adisp_process
from gui import DialogsInterface, g_tankActiveCamouflage, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nBuyMeta, ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.customization import CustomizationItemCMHandler
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationOptions
from gui.Scaleform.daapi.view.lobby.customization.shared import C11nMode, TABS_ITEM_MAPPING, DRAG_AND_DROP_INACTIVE_TABS, C11nTabs, SEASON_TYPE_TO_NAME, SEASONS_ORDER, getTotalPurchaseInfo
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS, C11N_SOUND_SPACE
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
from gui.customization.shared import chooseMode, getAppliedRegionsForCurrentHangarVehicle
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import formatPrice
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.utils.functions import makeTooltip
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from items.components.c11n_constants import SeasonType
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace

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
    __VIEWS = (VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER)

    def __init__(self, onViewPopupCallback):
        super(_C11ViewsPopupHandler, self).__init__([ ViewKey(alias) for alias in self.__VIEWS ])
        self.__onViewPopupCallback = onViewPopupCallback

    def onViewCreated(self, view):
        self.__onViewPopupCallback()


CustomizationAnchorInitVO = namedtuple('CustomizationAnchorInitVO', ('anchorUpdateVOs', 'doRegions'))
CustomizationSlotUpdateVO = namedtuple('CustomizationSlotUpdateVO', ('slotId', 'itemIntCD', 'uid'))
CustomizationSlotIdVO = namedtuple('CustomizationSlotIdVO', ('areaId', 'slotId', 'regionId'))
CustomizationAnchorsSetVO = namedtuple('CustomizationAnchorsSetVO', ('rendererList',))
CustomizationAnchorPositionVO = namedtuple('CustomizationAnchorPositionVO', ('zIndex', 'slotId'))
AnchorPositionData = namedtuple('AnchorPositionData', ('angleToCamera', 'clipSpacePos', 'slotId'))
_WAITING_MESSAGE = 'loadHangarSpace'

class _VehicleCustomizationAnchorsUpdater(object):

    def __init__(self, service):
        self.__service = service
        self.__vehicleCustomizationAnchors = None
        self.__processedAnchors = set()
        return

    def startUpdater(self, interfaceScale):
        if self.__vehicleCustomizationAnchors is None:
            self.__vehicleCustomizationAnchors = GUI.WGVehicleCustomizationAnchors(interfaceScale)
        return

    def stopUpdater(self):
        if self.__vehicleCustomizationAnchors is not None:
            self._delAllAnchors()
            self.__vehicleCustomizationAnchors = None
        return

    def setAnchors(self, displayObjects, isRegionObjects):

        def getRegionBySlotId(customSlotId):
            outfit = self.__service.getEmptyOutfit()
            area = outfit.getContainer(customSlotId.areaId)
            if area:
                slot = area.slotFor(customSlotId.slotId)
                if slot and slot.capacity() > customSlotId.regionId:
                    return slot.getRegions()[customSlotId.regionId]
            return None

        if self.__vehicleCustomizationAnchors is not None:
            processedObjectIds = set()
            for displayObject in displayObjects:
                if hasattr(displayObject, 'slotData'):
                    customSlotId = CustomizationSlotIdVO(displayObject.slotData.slotId.areaId, displayObject.slotData.slotId.slotId, displayObject.slotData.slotId.regionId)
                    normal = Math.Vector3(0, 0, 0)
                    if isRegionObjects:
                        region = getRegionBySlotId(customSlotId)
                        anchorWorldPos = self.__service.getPointForRegionLeaderLine(region)
                    else:
                        anchorWorldPos = self.__service.getPointForAnchorLeaderLine(customSlotId.areaId, customSlotId.slotId, customSlotId.regionId)
                        normal = self.__service.getNormalForAnchorLeaderLine(customSlotId.areaId, customSlotId.slotId, customSlotId.regionId)
                    if anchorWorldPos is not None:
                        uid = self.__vehicleCustomizationAnchors.addAnchor(anchorWorldPos, normal, displayObject, not isRegionObjects)
                        processedObjectIds.add(uid)

            delAnchors = self.__processedAnchors - processedObjectIds
            for anchorId in delAnchors:
                self.__vehicleCustomizationAnchors.delAnchor(anchorId)

            self.__processedAnchors = processedObjectIds
        return

    def setInterfaceScale(self, scale):
        self.__vehicleCustomizationAnchors.setInterfaceScale(scale)

    def _delAllAnchors(self):
        if self.__vehicleCustomizationAnchors is not None:
            for anchorId in self.__processedAnchors:
                self.__vehicleCustomizationAnchors.delAnchor(anchorId)

            self.__processedAnchors.clear()
        return


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
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, _=None):
        super(MainView, self).__init__()
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.fadeAnchorsOut = False
        self.__locatedOnEmbelem = False
        self.itemIsPicked = False
        self.__propertiesSheet = None
        self._seasonSoundAnimantion = None
        self._vehicleCustomizationAnchorsUpdater = None
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
        if self._isPropertySheetShown:
            self.__clearItem()
        else:
            self.onCloseWindow()

    def changeVisible(self, value):
        slotType, _, _ = self.__ctx.selectedRegion
        self.__ctx.regionSelected(slotType, -1, -1)
        self.as_hideS(value)

    def onReleaseItem(self):
        self.__ctx.caruselItemUnselected()
        self.__releaseItemSound()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET:
            self.__propertiesSheet = viewPy

    def changeSeason(self, seasonIdx):
        self.__ctx.changeSeason(seasonIdx)

    def __onSeasonChanged(self, seasonIdx):
        seasonName = SEASON_TYPE_TO_NAME.get(self.__ctx.currentSeason)
        self.soundManager.playInstantSound(SOUNDS.SEASON_SELECT.format(seasonName))
        self.__setAnchorsInitData(True)

    def __onTabChanged(self, tabIndex):
        self.soundManager.playInstantSound(SOUNDS.TAB_SWITCH)
        self.service.stopHighlighter()
        if tabIndex in C11nTabs.REGIONS:
            itemTypeID = TABS_ITEM_MAPPING[tabIndex]
            self.service.startHighlighter(chooseMode(itemTypeID, g_currentVehicle.item))
        self.__setAnchorsInitData()
        if self.__locatedOnEmbelem and self.hangarSpace.spaceInited:
            space = self.hangarSpace.space
            space.clearSelectedEmblemInfo()
            space.locateCameraToCustomizationPreview()
        self.__updateAnchorPositions()
        if tabIndex == C11nTabs.STYLE:
            slotIdVO = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)._asdict()
        elif tabIndex == C11nTabs.EFFECT:
            slotIdVO = CustomizationSlotIdVO(Area.MISC, GUI_ITEM_TYPE.MODIFICATION, 0)._asdict()
        else:
            slotIdVO = None
        self.as_updateSelectedRegionsS(slotIdVO)
        self.as_enableDNDS(tabIndex not in DRAG_AND_DROP_INACTIVE_TABS)
        self.__hidePropertiesSheet()
        return

    def __onItemsInstalled(self):
        if self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.APPLY)
        self.__setHeaderInitData()
        self.__setSeasonData()
        slotType, areaId, regionIdx = self.__ctx.selectedRegion
        self.__showPropertiesSheet(areaId, slotType, regionIdx)
        self.__setAnchorsInitData(True)

    def __onItemsRemoved(self):
        self.soundManager.playInstantSound(SOUNDS.REMOVE)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self.__setAnchorsInitData(True)

    def __onModeChanged(self, mode):
        self.__setHeaderInitData()
        self.__setSeasonData(True)

    def fadeOutAnchors(self, isFadeOut):
        self.fadeAnchorsOut = isFadeOut

    def onCloseWindow(self):
        if self.__ctx.isOutfitsModified():
            DialogsInterface.showDialog(I18nConfirmDialogMeta('customization/close'), self.__onCloseWindow)
        else:
            self.__onCloseWindow(proceed=True)

    def itemContextMenuDisplayed(self):
        cmHandler = self.app.contextMenuManager.getCurrentHandler()
        if isinstance(cmHandler, CustomizationItemCMHandler):
            cmHandler.onSelected += self._itemCtxMenuSelected

    def onLobbyClick(self):
        if self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            self.__clearItem()

    def onChangeSize(self):
        self.__updateAnchorPositions()

    def onSelectAnchor(self, areaId, slotType, regionIdx):
        if slotType not in (GUI_ITEM_TYPE.EMBLEM, GUI_ITEM_TYPE.INSCRIPTION):
            return
        if self.hangarSpace.spaceInited:
            self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            if slotType == GUI_ITEM_TYPE.EMBLEM:
                emblemType = 'player'
                zoom = MainView._ZOOM_ON_EMBLEM
            else:
                emblemType = 'inscription'
                zoom = MainView._ZOOM_ON_INSCRIPTION
            self.__updateAnchorPositions()
            self.__locatedOnEmbelem = self.hangarSpace.space.locateCameraOnEmblem(areaId == Area.HULL, emblemType, regionIdx, zoom)
            self.as_cameraAutoRotateChangedS(True)
            BigWorld.callback(5, self.__cameraRotationFinished)
        self.__ctx.regionSelected(slotType, areaId, regionIdx)
        self.__showPropertiesSheet(areaId, slotType, regionIdx)

    def __cameraRotationFinished(self):
        self.as_cameraAutoRotateChangedS(False)

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
        if self._vehicleCustomizationAnchorsUpdater is not None:
            self._vehicleCustomizationAnchorsUpdater.setAnchors(anchors, self.__ctx.currentTab in C11nTabs.REGIONS)
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
        self.__ctx.onCaruselItemSelected += self.__onCaruselItemSelected
        self.__ctx.onPropertySheetHidden += self.__onPropertySheetHidden
        self.__ctx.onPropertySheetShown += self.__onPropertySheetShown
        self.soundManager.playInstantSound(SOUNDS.ENTER)
        self.__viewLifecycleWatcher.start(self.app.containerManager, [_ModalWindowsPopupHandler(), _C11ViewsPopupHandler(self.__hidePropertiesSheet)])
        self.lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__onNotifyHangarCameraIdleStateChanged)
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreateHandler
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroyHandler
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefreshHandler
        self.service.onRegionHighlighted += self.__onRegionHighlighted
        self._seasonSoundAnimantion = _SeasonSoundAnimantion(len(SeasonType.COMMON_SEASONS), self.soundManager)
        self.__setHeaderInitData()
        self.__setSeasonData()
        self._vehicleCustomizationAnchorsUpdater = _VehicleCustomizationAnchorsUpdater(self.service)
        self._vehicleCustomizationAnchorsUpdater.startUpdater(self.settingsCore.interfaceScale.get())
        self.__ctx.refreshOutfit()
        self.settingsCore.interfaceScale.onScaleExactlyChanged += self.__onInterfaceScaleChanged
        self.as_eventLayoutS(g_currentVehicle.isOnlyForEventBattles())
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        if self.hangarSpace.spaceInited:
            self.hangarSpace.space.locateCameraToCustomizationPreview()
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        self.__renderEnv.enable(True)
        self._isPropertySheetShown = False

    def _dispose(self):
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        if g_appLoader.getSpaceID() != _SPACE_ID.LOGIN:
            self.__releaseItemSound()
            self.soundManager.playInstantSound(SOUNDS.EXIT)
        self.settingsCore.interfaceScale.onScaleExactlyChanged -= self.__onInterfaceScaleChanged
        self._vehicleCustomizationAnchorsUpdater.stopUpdater()
        self._vehicleCustomizationAnchorsUpdater = None
        if self.hangarSpace.spaceInited:
            space = self.hangarSpace.space
            if self.__locatedOnEmbelem:
                space.clearSelectedEmblemInfo()
            space.locateCameraToStartState()
        self._seasonSoundAnimantion = None
        self.__renderEnv.enable(False)
        self.__renderEnv = None
        self.__viewLifecycleWatcher.stop()
        self.service.stopHighlighter()
        self.lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__onNotifyHangarCameraIdleStateChanged)
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
        self.__ctx.onCaruselItemSelected -= self.__onCaruselItemSelected
        self.__ctx.onChangesCanceled -= self.__onChangesCanceled
        self.__ctx.onCacheResync -= self.__onCacheResync
        self.__ctx.onCustomizationItemsBought -= self.__onItemsBought
        self.__ctx.onCustomizationItemsRemoved -= self.__onItemsRemoved
        self.__ctx.onCustomizationItemInstalled -= self.__onItemsInstalled
        self.__ctx.onCustomizationTabChanged -= self.__onTabChanged
        self.__ctx.onCustomizationModeChanged -= self.__onModeChanged
        self.__ctx.onCustomizationSeasonChanged -= self.__onSeasonChanged
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
            slotId = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)
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

    def __updateAnchorPositions(self, _=None):
        self.as_setAnchorsDataS(self._getUpdatedAnchorsData())

    def __onRegionHighlighted(self, slotType, areaId, regionIdx, selected, hovered):
        region = None
        if hovered:
            self.soundManager.playInstantSound(SOUNDS.HOVER)
            return
        else:
            if self.__ctx.currentTab == C11nTabs.EFFECT:
                areaId = Area.MISC
                slotType = GUI_ITEM_TYPE.MODIFICATION
            if areaId != -1 and regionIdx != -1:
                region = CustomizationSlotIdVO(areaId, slotType, regionIdx)._asdict()
                if selected:
                    self.soundManager.playInstantSound(SOUNDS.CHOOSE)
            else:
                self.__hidePropertiesSheet()
            self.__ctx.regionSelected(slotType, areaId, regionIdx)
            if self.__ctx.isRegionSelected():
                self.as_onRegionHighlightedS(region)
                self.__showPropertiesSheet(areaId, slotType, regionIdx)
            else:
                self.__clearItem()
            return

    def __onSpaceCreateHandler(self):
        Waiting.hide(_WAITING_MESSAGE)
        self.__ctx.refreshOutfit()
        self.__updateAnchorPositions()

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
        self.__hidePropertiesSheet()

    def __onCaruselItemSelected(self, index, intCD):
        tabIndex = self.__ctx.currentTab
        if tabIndex == C11nTabs.STYLE or tabIndex == C11nTabs.EFFECT:
            slotType, areaId, regionIdx = self.__ctx.selectedRegion
            self.__onRegionHighlighted(slotType, areaId, regionIdx, True, False)
        if not self.__propertiesSheet.isVisible and not self.itemIsPicked:
            self.soundManager.playInstantSound(SOUNDS.PICK)
            self.itemIsPicked = True

    def __onServerSettingChanged(self, diff):
        if 'isCustomizationEnabled' in diff and not diff.get('isCustomizationEnabled', True):
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CUSTOMIZATION_UNAVAILABLE, type=SystemMessages.SM_TYPE.Warning)
            self.__onCloseWindow(proceed=True)

    def __onPropertySheetShown(self):
        self._isPropertySheetShown = True

    def __onPropertySheetHidden(self):
        self.service.resetHighlighting()
        self.__clearItem()
        self._isPropertySheetShown = False

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
             'isFilled': isFilled,
             'forceAnim': forceAnim})

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
        if tabIndex == C11nTabs.STYLE:
            slotId = CustomizationSlotIdVO(0, GUI_ITEM_TYPE.STYLE, 0)
            uid = customizationSlotIdToUid(slotId)
            anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), -1, uid)._asdict())
        else:
            for areaId in Area.ALL:
                regionsIndexes = getAppliedRegionsForCurrentHangarVehicle(areaId, cType)
                slot = self.__ctx.currentOutfit.getContainer(areaId).slotFor(cType)
                for regionsIndex in regionsIndexes:
                    slotId = CustomizationSlotIdVO(areaId, cType, regionsIndex)
                    item = slot.getItem(regionsIndex)
                    itemIntCD = item.intCD if item is not None else 0
                    uid = customizationSlotIdToUid(slotId)
                    anchorVOs.append(CustomizationSlotUpdateVO(slotId._asdict(), itemIntCD, uid)._asdict())

        doRegions = tabIndex in C11nTabs.REGIONS
        if update:
            self.as_updateAnchorDataS(CustomizationAnchorInitVO(anchorVOs, doRegions)._asdict())
        else:
            self.as_setAnchorInitS(CustomizationAnchorInitVO(anchorVOs, doRegions)._asdict())
        return

    def __setHeaderInitData(self):
        vehicle = g_currentVehicle.item
        if g_currentVehicle.isEvent():
            isElite = False
            tankLevel = ''
            tankType = vehicle.getFootballRole()
        else:
            isElite = vehicle.isElite
            tankLevel = str(int2roman(vehicle.level))
            tankType = vehicle.type
        self.as_setHeaderDataS({'tankTier': tankLevel,
         'tankName': vehicle.shortUserName,
         'tankType': '{}_elite'.format(tankType) if isElite else tankType,
         'isElite': isElite,
         'closeBtnTooltip': VEHICLE_CUSTOMIZATION.CUSTOMIZATION_HEADERCLOSEBTN})

    def __showPropertiesSheet(self, areaId, slotId, regionId):
        if self.__propertiesSheet:
            self.__propertiesSheet.show(areaId, slotId, regionId)

    def __hidePropertiesSheet(self):
        if self.__propertiesSheet:
            self.__propertiesSheet.hide()

    def getItemTabsData(self):
        data = []
        pluses = []
        for tabIdx in self.__ctx.visibleTabs:
            itemTypeID = TABS_ITEM_MAPPING[tabIdx]
            typeName = GUI_ITEM_TYPE_NAMES[itemTypeID]
            showPlus = not self.__ctx.checkSlotsFilling(itemTypeID, self.__ctx.currentSeason)
            data.append({'label': _ms(ITEM_TYPES.customizationPlural(typeName)),
             'tooltip': makeTooltip(ITEM_TYPES.customizationPlural(typeName), TOOLTIPS.customizationItemTab(typeName)),
             'id': tabIdx})
            pluses.append(showPlus)

        return (data, pluses)

    def __onNotifyHangarCameraIdleStateChanged(self, event):
        isIdle = event.ctx.get('started', False)
        self.as_cameraAutoRotateChangedS(isIdle)

    @async
    @adisp_process
    def __confirmHeaderNavigation(self, callback):
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

    def __onInterfaceScaleChanged(self, scale):
        if self._vehicleCustomizationAnchorsUpdater is not None:
            self._vehicleCustomizationAnchorsUpdater.setInterfaceScale(scale)
        return

    def __resetCameraFocus(self):
        if self.__locatedOnEmbelem and self.hangarSpace.spaceInited:
            space = self.hangarSpace.space
            space.clearSelectedEmblemInfo()
            space.locateCameraToCustomizationPreview()
            self.__updateAnchorPositions()
            self.__locatedOnEmbelem = False

    def __resetUIFocus(self):
        self.as_onRegionHighlightedS(-1)

    def __clearItem(self):
        self.__hidePropertiesSheet()
        if self.__ctx.currentTab in (C11nTabs.EMBLEM, C11nTabs.INSCRIPTION):
            self.__resetCameraFocus()
        slotType, _, _ = self.__ctx.selectedRegion
        self.__ctx.regionSelected(slotType, -1, -1)
        self.__resetUIFocus()
