# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/service.py
import math
import logging
import typing
import BigWorld
import Windowing
import Event
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui import SystemMessages
from gui.customization.context import CustomizationContext
from gui.customization.shared import C11N_ITEM_TYPE_MAP, HighlightingMode, MODE_TO_C11N_TYPE
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE, ItemsCollection
from gui.shared.gui_items.customization.c11n_items import Customization, Style
from gui.shared.gui_items.customization.outfit import Outfit, Area
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsBuyer, CustomizationsSeller
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.decorators import process
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from items.vehicles import makeIntCompactDescrByID
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared.utils import IHangarSpace
from items.components.c11n_constants import SeasonType, ApplyArea
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
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

    def getEmptyOutfit(self):
        return self.itemsFactory.createOutfit()

    def tryOnOutfit(self, outfit):
        self.hangarSpace.updateVehicleOutfit(outfit)

    def getOutfit(self, season):
        return g_currentVehicle.item.getOutfit(season)

    def getCustomOutfit(self, season):
        return g_currentVehicle.item.getCustomOutfit(season)

    def getCurrentStyle(self):
        outfit = g_currentVehicle.item.getStyledOutfit(SeasonType.WINTER)
        return self.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id) if outfit else None

    def isCurrentStyleInstalled(self):
        outfit = g_currentVehicle.item.getStyledOutfit(SeasonType.WINTER)
        return outfit and outfit.isActive()

    @process('buyItem')
    def buyItems(self, item, count, vehicle=None):
        result = yield CustomizationsBuyer(vehicle, item, count).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @process('sellItem')
    def sellItem(self, item, count, vehicle=None):
        result = yield CustomizationsSeller(vehicle, item, count).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @process('buyAndInstall')
    def buyAndEquipOutfit(self, outfit, season, vehicle=None):
        result = yield OutfitApplier(vehicle or g_currentVehicle.item, outfit, season).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @process('buyAndInstall')
    def buyAndEquipStyle(self, style, vehicle=None):
        result = yield StyleApplier(vehicle or g_currentVehicle.item, style).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class CustomizationService(_ServiceItemShopMixin, _ServiceHelpersMixin, ICustomizationService):
    hangarSpace = dependency.descriptor(IHangarSpace)
    __FADE_OUT_DELAY = 0.15

    @property
    def isHighlighterActive(self):
        return self._helper is not None and self._isHighlighterActive

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
        self.__customizationCtx = None
        self._suspendHighlighterCallbackID = None
        self._isDraggingInProcess = False
        self._notHandleHighlighterEvent = False
        self.__showCustomizationCallbackId = None
        self._selectedRegion = ApplyArea.NONE
        self._isHighlighterActive = False
        return

    def init(self):
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreate
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        self._isOver3dScene = False
        self._isDraggingInProcess = False
        self._notHandleHighlighterEvent = False

    def fini(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        self.stopHighlighter()
        self._eventsManager.clear()
        self.__cleanupSuspendHighlighterCallback()
        if self.__showCustomizationCallbackId is not None:
            BigWorld.cancelCallback(self.__showCustomizationCallbackId)
            self.__showCustomizationCallbackId = None
        return

    def showCustomization(self, vehInvID=None, callback=None):
        if not self.hangarSpace.spaceInited or not self.hangarSpace.isModelLoaded:
            _logger.error('Space or vehicle is not presented, could not show customization view, return')
            return
        else:
            self.__createCtx()
            loadCallback = lambda : self.__loadCustomization(vehInvID, callback)
            if self.__showCustomizationCallbackId is None:
                self.__moveHangarVehicleToCustomizationRoom()
                self.__showCustomizationCallbackId = BigWorld.callback(0.0, lambda : self.__showCustomization(loadCallback))
            return

    def closeCustomization(self):
        self.__destroyCtx()

    def getCtx(self):
        return self.__customizationCtx

    def __createCtx(self):
        if self.__customizationCtx is None:
            self.__customizationCtx = CustomizationContext()
            self.__customizationCtx.init()
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
        if self._helper:
            self._helper.highlightRegions(regionsMask)

    def selectRegions(self, regionsMask):
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
        self.onRegionHighlighted(MODE_TO_C11N_TYPE[self._mode], areaID, regionID, highlightingType, highlightingResult)

    def __onSpaceCreate(self):
        self.resumeHighlighter()

    def __onSpaceDestroy(self, _):
        self.suspendHighlighter()

    def __onNotifyCursorOver3dScene(self, event):
        self._isOver3dScene = event.ctx.get('isOver3dScene', False)
        if self._helper:
            self._helper.setSelectingEnabled(self._isOver3dScene)
        if not self._isOver3dScene:
            self.onRegionHighlighted(MODE_TO_C11N_TYPE[self._mode], -1, -1, False, False)

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
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_CUSTOMIZATION, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __loadCustomization(self, vehInvID=None, callback=None):
        if vehInvID is not None and vehInvID != g_currentVehicle.item.invID:
            return g_currentVehicle.selectVehicle(vehInvID, lambda : self.__loadCustomization(vehInvID, callback), True)
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
            self.selectRegions(self._selectedRegion)
            self._isHighlighterActive = True
            if self.__customizationCtx is not None and self.__customizationCtx.c11CameraManager.isStyleInfo():
                self.suspendHighlighter()
        return

    def __onVehicleLoadStarted(self):
        self._selectedRegion = ApplyArea.NONE
        self._isHighlighterActive = False
        self._helper = None
        return
