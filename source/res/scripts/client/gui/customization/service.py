# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/service.py
import math
import logging
from itertools import chain
import typing
import BigWorld
import CGF
import Windowing
import Event
import adisp
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.server_events.events_helpers import getC11nQuestsConfig, isC11nQuest
from gui.shared.event_dispatcher import hideVehiclePreview
from helpers import dependency, time_utils
from customization_quests_common import CustQuestsCache, deserializeToken
from gui import SystemMessages, g_tankActiveCamouflage
from gui.Scaleform.daapi.view.lobby.customization.context.context import CustomizationContext
from gui.customization.shared import C11N_ITEM_TYPE_MAP, HighlightingMode, C11nId
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE, ItemsCollection
from gui.shared.gui_items.customization.c11n_items import Customization
from items import vehicles
from items.customizations import createNationalEmblemComponents
from serializable_types.customizations import CustomizationOutfit
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from vehicle_outfit.outfit import Outfit, Area
from gui.shared.gui_items.processors.common import CustomizationsBuyer, CustomizationsSeller
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.decorators import adisp_process
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from items.vehicles import makeIntCompactDescrByID, VehicleDescr
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared.utils import IHangarSpace
from items.components.c11n_constants import SeasonType, ApplyArea, CUSTOM_STYLE_POOL_ID, OUTFIT_POOL_EMPTY_STUB
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.camouflages import getStyleProgressionOutfit
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from cgf_components.hangar_camera_manager import HangarCameraManager
if typing.TYPE_CHECKING:
    from gui.customization.constants import CustomizationModeSource
    from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationModes, CustomizationTabs
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

class _ServiceItemShopMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def getItems(self, itemTypeID, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        if vehicle:
            criteria |= REQ_CRITERIA.CUSTOMIZATION.FOR_VEHICLE(vehicle)
        return self.itemsCache.items.getItems(itemTypeID, criteria)

    def getPaints(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.PAINT, vehicle, criteria)

    def getCamouflages(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.CAMOUFLAGE, vehicle, criteria)

    def getStyles(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.STYLE, vehicle, criteria)

    def getItemByID(self, itemTypeID, itemID):
        intCD = makeIntCompactDescrByID('customizationItem', C11N_ITEM_TYPE_MAP.get(itemTypeID), itemID)
        return self.itemsCache.items.getItemByCD(intCD)

    def getItemByCD(self, itemCD):
        return self.itemsCache.items.getItemByCD(itemCD)


class _ServiceHelpersMixin(object):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    itemsCache = dependency.descriptor(IItemsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)
    eventsCache = dependency.descriptor(IEventsCache)

    def getEmptyOutfit(self, vehicleCD=''):
        vehicleCD = vehicleCD or self._getVehicleCD()
        return self.itemsFactory.createOutfit(vehicleCD=vehicleCD)

    def getEmptyOutfitWithNationalEmblems(self, vehicleCD):
        vehDesc = VehicleDescr(vehicleCD)
        decals = createNationalEmblemComponents(vehDesc)
        component = CustomizationOutfit(decals=decals)
        return self.itemsFactory.createOutfit(component=component, vehicleCD=vehicleCD)

    def tryOnOutfit(self, outfit):
        self.hangarSpace.updateVehicleOutfit(outfit)

    def getCurrentOutfit(self, season):
        return g_currentVehicle.item.getOutfit(season)

    def getStyledOutfit(self, season):
        if self.isStyleInstalled():
            return self.getCurrentOutfit(season)
        outfitsPool = self.itemsCache.items.inventory.getC11nOutfitsFromPool(g_currentVehicle.item.intCD)
        for styleId, outfitDiffs in outfitsPool:
            if styleId == CUSTOM_STYLE_POOL_ID:
                continue
            if (styleId, outfitDiffs) == OUTFIT_POOL_EMPTY_STUB:
                break
            style = self.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            outfit = style.getOutfit(season, vehicleCD=self._getVehicleCD(), diff=outfitDiffs.get(season))
            return outfit

        return self.getEmptyOutfit()

    def getCustomOutfit(self, season):
        outfitsPool = self.itemsCache.items.inventory.getC11nOutfitsFromPool(g_currentVehicle.item.intCD)
        if not outfitsPool:
            return self.getEmptyOutfit()
        styleId, outfits = outfitsPool[0]
        if styleId != CUSTOM_STYLE_POOL_ID:
            return self.getEmptyOutfit()
        outfit = self.itemsFactory.createOutfit(strCompactDescr=outfits.get(season, ''), vehicleCD=self._getVehicleCD())
        return outfit

    def getStyleComponentDiffs(self, style):
        outfitsPool = self.itemsCache.items.inventory.getC11nOutfitsFromPool(g_currentVehicle.item.intCD)
        for styleId, outfitDiffs in outfitsPool:
            if styleId == style.id:
                return outfitDiffs.copy()

        return {}

    def getStoredStyleDiffs(self):
        outfitsPool = self.itemsCache.items.inventory.getC11nOutfitsFromPool(g_currentVehicle.item.intCD)
        if outfitsPool and outfitsPool[0][0] == CUSTOM_STYLE_POOL_ID:
            outfitsPool.pop(0)
        if outfitsPool and not outfitsPool[0][1]:
            outfitsPool.pop(0)
        return outfitsPool[:]

    def isStyleInstalled(self):
        return g_currentVehicle.item.isStyleInstalled

    @adisp_process('buyItem')
    def buyItems(self, item, count, vehicle=None):
        result = yield CustomizationsBuyer(vehicle, item, count).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @adisp_process('sellItem')
    def sellItem(self, item, count, vehicle=None):
        result = yield CustomizationsSeller(vehicle, item, count).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _getVehicleCD(self):
        if g_currentVehicle.isPresent():
            vehicleData = self.itemsCache.items.inventory.getItemData(g_currentVehicle.item.intCD)
            vehicleCD = vehicleData.compDescr
        else:
            vehicleCD = ''
        return vehicleCD


class CustomizationService(_ServiceItemShopMixin, _ServiceHelpersMixin, ICustomizationService):
    hangarSpace = dependency.descriptor(IHangarSpace)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __FADE_OUT_DELAY = 0.15
    __TURRET_YAW_ANGLE = 0.0
    __GUN_PITCH_ANGLE = 0.0

    @property
    def isHighlighterActive(self):
        return self._helper is not None and self._isHighlighterActive

    @property
    def isOver3dScene(self):
        return self._isOver3dScene

    def __init__(self):
        super(CustomizationService, self).__init__()
        self._helper = None
        self._mode = HighlightingMode.PAINT_REGIONS
        self._eventsManager = Event.EventManager()
        self._needHelperRestart = False
        self._isOver3dScene = False
        self.onRegionHighlighted = Event.Event(self._eventsManager)
        self.onOutfitChanged = Event.Event(self._eventsManager)
        self.onCustomizationHelperRecreated = Event.Event(self._eventsManager)
        self.onVisibilityChanged = Event.Event(self._eventsManager)
        self.__customizationCtx = None
        self._suspendHighlighterCallbackID = None
        self._isDraggingInProcess = False
        self._notHandleHighlighterEvent = False
        self.__showCustomizationCallbackId = None
        self._selectedRegion = ApplyArea.NONE
        self._isHighlighterActive = False
        self.__showCustomizationKwargs = {}
        return

    def init(self):
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_eventBus.addListener(events.CustomizationEvent.SHOW, self.__onShowCustomization, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged += self.__onVehicleChanged
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreate
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        self._isOver3dScene = False
        self._isDraggingInProcess = False
        self._notHandleHighlighterEvent = False
        self.__progressionQuestCache = None
        self.__progressionQuestIDs = None
        return

    def fini(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_eventBus.removeListener(events.CustomizationEvent.SHOW, self.__onShowCustomization, scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.stopHighlighter()
        self._eventsManager.clear()
        self.__cleanupSuspendHighlighterCallback()
        self.__showCustomizationKwargs = None
        self.__progressionQuestCache = None
        self.__progressionQuestIDs = None
        if self.__showCustomizationCallbackId is not None:
            BigWorld.cancelCallback(self.__showCustomizationCallbackId)
            self.__showCustomizationCallbackId = None
        return

    @adisp.adisp_process
    def showCustomization(self, vehInvID=None, callback=None, season=None, modeId=None, tabId=None):
        if self.__customizationCtx is None:
            lobbyHeaderNavigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
            if not lobbyHeaderNavigationPossible:
                return
        elif self.__customizationCtx.isOutfitsModified() and g_currentVehicle.invID != vehInvID:
            result = yield self.__confirmClose()
            if not result:
                return
        self.__showCustomizationKwargs = {'vehInvID': vehInvID,
         'callback': callback,
         'season': season,
         'modeId': modeId,
         'tabId': tabId}
        shouldSelectVehicle = False
        if self.hangarSpace.space is not None:
            self.hangarSpace.space.turretAndGunAngles.set(gunPitch=self.__GUN_PITCH_ANGLE, turretYaw=self.__TURRET_YAW_ANGLE)
        if vehInvID is not None:
            vehGuiItem = self.itemsCache.items.getVehicle(vehInvID)
            if vehGuiItem is not None:
                if not vehGuiItem.isCustomizationEnabled():
                    _logger.error("Can't show customization view for currently non-customizable vehicle '%s'", vehGuiItem.name)
                    return
                if g_currentVehicle.invID != vehInvID:
                    shouldSelectVehicle = True
        if not self.hangarSpace.spaceInited or not self.hangarSpace.isModelLoaded or shouldSelectVehicle:
            if shouldSelectVehicle:
                if g_currentPreviewVehicle.isPresent():
                    hideVehiclePreview(back=False, close=True)
                    g_currentPreviewVehicle.selectNoVehicle()
                BigWorld.callback(0.0, makeCallbackWeak(g_currentVehicle.selectVehicle, vehInvID=vehInvID))
            _logger.info('Space or vehicle is not presented, customization view loading delayed')
            self.hangarSpace.onVehicleChanged += self.__delayedShowCustomization
            self.hangarSpace.onSpaceChanged += self.__delayedShowCustomization
            return
        else:
            if not shouldSelectVehicle and self.hangarSpace.space is not None:
                vEntity = self.hangarSpace.space.getVehicleEntity()
                if vEntity is not None:
                    vEntity.appearance.rotateTurretForAnchor(None, None)
                    vEntity.appearance.rotateGunToDefault()
            self.__delayedShowCustomization()
            return

    @adisp.adisp_async
    @adisp.adisp_process
    @dependency.replace_none_kwargs(appLoader=IAppLoader)
    def __confirmClose(self, appLoader=None, callback=None):
        result = True
        app = appLoader.getApp()
        customizationView = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
        if customizationView is not None:
            result = yield customizationView.showCloseConfirmator()
        callback(result)
        return

    def __delayedShowCustomization(self):
        self.hangarSpace.onVehicleChanged -= self.__delayedShowCustomization
        self.hangarSpace.onSpaceChanged -= self.__delayedShowCustomization
        season = self.__showCustomizationKwargs.get('season', None)
        modeId = self.__showCustomizationKwargs.get('modeId', None)
        tabId = self.__showCustomizationKwargs.get('tabId', None)
        vehInvID = self.__showCustomizationKwargs.get('vehInvID', None)
        callback = self.__showCustomizationKwargs.get('callback', None)
        loadCallback = lambda : self.__loadCustomization(vehInvID, callback, season, modeId, tabId)
        if self.__showCustomizationCallbackId is None:
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                cameraManager.switchByCameraName('Customization')
            ClientSelectableCameraObject.deselectAll()
            self.hangarSpace.space.getVehicleEntity().onSelect()
            self.__moveHangarVehicleToCustomizationRoom()
            self.__showCustomizationCallbackId = BigWorld.callback(0.0, lambda : self.__showCustomization(loadCallback))
        self.onVisibilityChanged(True)
        return

    def closeCustomization(self):
        if self.hangarSpace.space is not None:
            self.hangarSpace.space.turretAndGunAngles.reset()
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, HangarCameraManager)
            if cameraManager:
                cameraManager.switchToTank()
        self.__destroyCtx()
        self.onVisibilityChanged(False)
        return

    def getCtx(self):
        return self.__customizationCtx

    def __createCtx(self, season=None, modeId=None, tabId=None, source=None):
        if self.__customizationCtx is None:
            self.__customizationCtx = CustomizationContext()
            self.__customizationCtx.init(season, modeId, tabId)
            return
        else:
            if season is not None:
                self.__customizationCtx.changeSeason(season)
            if modeId is not None:
                self.__customizationCtx.changeMode(modeId, tabId, source)
            return

    def __destroyCtx(self):
        if self.__customizationCtx is not None:
            self.__customizationCtx.fini()
            self.__customizationCtx = None
        return

    def startHighlighter(self, mode=HighlightingMode.PAINT_REGIONS):
        if self._mode != mode:
            self._selectedRegion = ApplyArea.NONE
        self._mode = mode
        isLoaded = False
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
            isLoaded = entity.appearance.isLoaded()
        if not isLoaded:
            return False
        if self._helper:
            self._helper.setSelectionMode(self._mode)
        else:
            self._helper = BigWorld.PyCustomizationHelper(entity.model, self._mode, self._isOver3dScene, self.__onRegionHighlighted)
            self.onCustomizationHelperRecreated()
        self.selectRegions(self._selectedRegion)
        self._isHighlighterActive = True
        return True

    def restartHighlighter(self):
        self.stopHighlighter()
        self.startHighlighter(self._mode)

    def stopHighlighter(self):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)
        self._selectedRegion = ApplyArea.NONE
        self._helper = None
        self._isHighlighterActive = False
        return

    def suspendHighlighter(self):
        self._isHighlighterActive = False
        if self._helper is not None:
            self._helper.setSuspended(True)
        return

    def resumeHighlighter(self):
        if self._helper is not None:
            self._helper.setSelectionMode(self._mode)
            self.selectRegions(self._selectedRegion)
            self._isHighlighterActive = True
            self._helper.setSuspended(False)
        return

    def getSelectionMode(self):
        return self._mode

    def getPointForRegionLeaderLine(self, areaId):
        return self.hangarSpace.getCentralPointForArea(areaId)

    def getAnchorParams(self, areaId, slotId, regionId):
        return self.hangarSpace.getAnchorParams(slotId, areaId, regionId)

    def setSelectHighlighting(self, value):
        if self._helper:
            self._helper.setHighlightingEnabled(value)

    def resetHighlighting(self):
        if self._helper:
            self._helper.resetHighlighting()

    def highlightRegions(self, regionsMask):
        if not self._isHighlighterActive:
            return
        if self._helper:
            self._helper.highlightRegions(regionsMask)

    def selectRegions(self, regionsMask):
        if not self._isHighlighterActive:
            return
        if self._helper:
            self._helper.selectRegions(regionsMask)
        self._selectedRegion = regionsMask

    def isRegionSelected(self):
        return self._selectedRegion != ApplyArea.NONE and self._isHighlighterActive

    def getHightlighter(self):
        return self._helper

    def __moveHangarVehicleToCustomizationRoom(self):
        from gui.ClientHangarSpace import customizationHangarCFG
        cfg = customizationHangarCFG()
        targetPos = cfg['v_start_pos']
        yaw = math.radians(cfg['v_start_angles'][0])
        pitch = math.radians(cfg['v_start_angles'][1])
        roll = math.radians(cfg['v_start_angles'][2])
        shadowYOffset = cfg['shadow_forward_y_offset'] if BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1 else cfg['shadow_deferred_y_offset']
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, ctx={'targetPos': targetPos,
         'rotateYPR': (yaw, pitch, roll),
         'shadowYOffset': shadowYOffset}), scope=EVENT_BUS_SCOPE.LOBBY)

    def setSelectingRegionEnabled(self, enable):
        if self._helper:
            self._helper.setSelectingRegionEnabled(enable)

    def setDOFenabled(self, enable):
        if self._helper:
            self._helper.setDOFenabled(enable)

    def setDOFparams(self, params):
        if self._helper:
            self._helper.setDOFparams(*params)

    def __onRegionHighlighted(self, args):
        if self._notHandleHighlighterEvent:
            self._notHandleHighlighterEvent = False
            return
        areaID, regionID, highlightingType, highlightingResult = (-1,
         -1,
         True,
         False)
        if args:
            areaID, regionID, highlightingType, highlightingResult = args
        self.onRegionHighlighted(areaID, regionID, highlightingType, highlightingResult)

    def __onSpaceCreate(self):
        self.resumeHighlighter()

    def __onSpaceDestroy(self, _):
        self.suspendHighlighter()

    def __onNotifyCursorOver3dScene(self, event):
        self._isOver3dScene = event.ctx.get('isOver3dScene', False)
        if self._helper:
            self._helper.setSelectingEnabled(self._isOver3dScene)
        if not self._isOver3dScene:
            self.onRegionHighlighted(-1, -1, False, False)

    def __onNotifyCursorDragging(self, event):
        if self._helper:
            isDragging = event.ctx.get('isDragging', False)
            if isDragging:
                self.__cleanupSuspendHighlighterCallback()
                self._suspendHighlighterCallbackID = BigWorld.callback(self.__FADE_OUT_DELAY, makeCallbackWeak(self.__onSuspendHighlighter))
                self._isDraggingInProcess = False
                g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onSpaceMoving)
            else:
                g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onSpaceMoving)
                self._notHandleHighlighterEvent = False
                if self._suspendHighlighterCallbackID and self._isDraggingInProcess:
                    self._notHandleHighlighterEvent = True
                self._isDraggingInProcess = False
                self.__cleanupSuspendHighlighterCallback()
                self._helper.setSuspended(False)

    def __cleanupSuspendHighlighterCallback(self):
        if self._suspendHighlighterCallbackID:
            BigWorld.cancelCallback(self._suspendHighlighterCallbackID)
            self._suspendHighlighterCallbackID = None
        return

    def __onSuspendHighlighter(self):
        if self._helper:
            self._helper.setSuspended(True)
        self._suspendHighlighterCallbackID = None
        return

    def __onSpaceMoving(self, event):
        dx = event.ctx.get('dx', 0)
        dy = event.ctx.get('dy', 0)
        dz = event.ctx.get('dz', 0)
        if dx or dy or dz:
            self._isDraggingInProcess = True
            self.__cleanupSuspendHighlighterCallback()
            self.__onSuspendHighlighter()
            g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onSpaceMoving)

    def __showCustomization(self, callback=None):
        self.__showCustomizationCallbackId = None
        ctx = {}
        if callback is not None:
            ctx['callback'] = callback
            self.__customizationShownCallback = None
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_CUSTOMIZATION), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __loadCustomization(self, vehInvID=None, callback=None, season=None, modeId=None, tabId=None):
        self.__createCtx(season, modeId, tabId)
        if vehInvID is not None and vehInvID != g_currentVehicle.item.invID:
            return g_currentVehicle.selectVehicle(vehInvID, lambda : self.__loadCustomization(vehInvID, callback, season, modeId, tabId), True)
        else:
            if callback is not None:
                BigWorld.callback(0.0, callback)
            return

    def __onWindowAccessibilityChanged(self, isAccessible):
        if self._helper:
            self._helper.setSelectingEnabled(self._isOver3dScene)

    def __onVehicleLoadFinished(self):
        entity = self.hangarSpace.getVehicleEntity()
        if entity and entity.appearance and entity.appearance.isLoaded():
            self._helper = BigWorld.PyCustomizationHelper(entity.model, self._mode, self._isOver3dScene, self.__onRegionHighlighted)
            self.onCustomizationHelperRecreated()
            self._isHighlighterActive = True
            self.selectRegions(self._selectedRegion)
            if self.__customizationCtx is not None and self.__customizationCtx.c11nCameraManager.isStyleInfo():
                self.suspendHighlighter()
        return

    def __onVehicleLoadStarted(self):
        self._isHighlighterActive = False
        self._helper = None
        return

    def __onVehicleChanged(self):
        self._selectedRegion = ApplyArea.NONE

    def __onShowCustomization(self, event):
        self.showCustomization(**event.ctx)

    def changeStyleProgressionLevelPreview(self, level):
        entity = self.hangarSpace.getVehicleEntity()
        if not entity or not level or not entity.isVehicleLoaded:
            return 1
        else:
            outfit = entity.appearance.outfit
            if not outfit.style or not outfit.style.isProgression:
                return 1
            if g_currentPreviewVehicle.isPresent():
                vehicle = g_currentPreviewVehicle.item
                if vehicle:
                    season = g_tankActiveCamouflage.get(vehicle.intCD, vehicle.getAnyOutfitSeason())
                    resOutfit = getStyleProgressionOutfit(outfit, level, season)
                    self.tryOnOutfit(resOutfit)
                    if self.__customizationCtx is not None:
                        slotID = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
                        self.__customizationCtx.events.onComponentChanged(slotID, True)
                    return resOutfit.progressionLevel
            return 1

    def getCurrentProgressionStyleLevel(self):
        entity = self.hangarSpace.getVehicleEntity()
        if not entity:
            return None
        else:
            outfit = entity.appearance.outfit
            if not outfit.style or not outfit.style.isProgression:
                _logger.error('Could not find style progressions')
                return None
            return outfit.progressionLevel

    @staticmethod
    def removeAdditionalProgressionData(outfit, style, vehCD, season):
        if outfit and outfit.progressionLevel and style and vehCD:
            additionalOutfit = style.getAdditionalOutfit(outfit.progressionLevel, season, vehCD)
            if additionalOutfit is not None:
                return outfit.discard(additionalOutfit)
        return outfit

    def getQuestsForProgressionItem(self, itemCD):
        if self.__progressionQuestCache is None:
            self.__updateProgressionQuests()
        return self.__progressionQuestCache.get(itemCD, None)

    def getItemCDByQuestID(self, eventID):
        if self.__progressionQuestCache is None:
            self.__updateProgressionQuests()
        for itemCD, quests in self.__progressionQuestCache.iteritems():
            if eventID in (quest.getID() for quest in quests):
                return itemCD

        return

    def isProgressionQuests(self, eventID):
        if self.__progressionQuestIDs is None:
            self.__updateProgressionQuests()
        return eventID in self.__progressionQuestIDs

    def __updateProgressionQuests(self):
        cache = vehicles.g_cache.customization20()
        self.__progressionQuestCache = {}
        self.__progressionQuestIDs = set()
        questsConfig = getC11nQuestsConfig()
        if not questsConfig:
            return
        questIDs = set()
        for levels in questsConfig.itervalues():
            for level in levels:
                questIDs |= {idn for idn in chain(*level.get('questIds', {}).values())}

        self.__progressionQuestIDs = questIDs
        filterFunc = lambda quest: isC11nQuest(quest.getID()) and quest.getFinishTimeLeft()
        c11nQuests = self.eventsCache.getHiddenQuests(filterFunc)
        styles = cache.getQuestProgressionStyles()
        for token, level, _, finishTime, idn in CustQuestsCache(questsConfig):
            if idn in c11nQuests:
                styleId, __ = deserializeToken(token)
                if styleId in styles:
                    style = styles[styleId]
                    items = style.questsProgression.getItemsForGroup(token)
                    finishTimeLocal = time_utils.makeLocalServerTime(finishTime)
                    if time_utils.getServerTimeDiffInLocal(finishTimeLocal) == 0:
                        continue
                    for itemType, ids in items[level].iteritems():
                        for itemId in ids:
                            compactDescr = makeIntCompactDescrByID('customizationItem', itemType, itemId)
                            item = self.getItemByCD(compactDescr)
                            self.__progressionQuestCache.setdefault(item.intCD, []).append(c11nQuests[idn])

    def __onSyncCompleted(self):
        self.__updateProgressionQuests()
