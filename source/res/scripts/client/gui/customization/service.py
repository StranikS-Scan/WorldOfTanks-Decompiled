# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/service.py
import BigWorld
import Event
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui import SystemMessages
from gui.customization.shared import C11N_ITEM_TYPE_MAP, HighlightingMode, MODE_TO_C11N_TYPE
from gui.shared import g_eventBus, events
from gui.shared.gui_items import GUI_ITEM_TYPE, ItemsCollection
from gui.shared.gui_items.customization.c11n_items import Customization, Style
from gui.shared.gui_items.customization.outfit import Outfit
from gui.shared.gui_items.processors.common import OutfitApplier, StyleApplier, CustomizationsBuyer, CustomizationsSeller
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.decorators import process
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from gui.shared.utils.HangarSpace import g_hangarSpace
from items.vehicles import makeIntCompactDescrByID
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory

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

    def getModifications(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.MODIFICATION, vehicle, criteria)

    def getDecals(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.DECAL, vehicle, criteria)

    def getEmblems(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.EMBLEM, vehicle, criteria)

    def getInscriptions(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.INSCRIPTION, vehicle, criteria)

    def getStyles(self, vehicle=None, criteria=REQ_CRITERIA.EMPTY):
        return self.getItems(GUI_ITEM_TYPE.STYLE, vehicle, criteria)

    def getItemByID(self, itemTypeID, itemID):
        intCD = makeIntCompactDescrByID('customizationItem', C11N_ITEM_TYPE_MAP.get(itemTypeID), itemID)
        return self.itemsCache.items.getItemByCD(intCD)


class _ServiceHelpersMixin(object):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    itemsCache = dependency.descriptor(IItemsCache)

    def getEmptyOutfit(self):
        return self.itemsFactory.createOutfit()

    def tryOnOutfit(self, outfit):
        g_hangarSpace.updateVehicleOutfit(outfit)

    def getOutfit(self, season):
        return g_currentVehicle.item.getOutfit(season)

    def getCustomOutfit(self, season):
        return g_currentVehicle.item.getCustomOutfit(season)

    def getCurrentStyle(self):
        outfit = g_currentVehicle.item.getStyledOutfit(1)
        return self.getItemByID(GUI_ITEM_TYPE.STYLE, outfit.id) if outfit else None

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

    def __init__(self):
        super(CustomizationService, self).__init__()
        self._helper = None
        self._mode = HighlightingMode.PAINT_REGIONS
        self._eventsManager = Event.EventManager()
        self._anchorPositions = None
        self._needHelperRestart = False
        self.onRegionHighlighted = Event.Event(self._eventsManager)
        self.onRemoveItems = Event.Event(self._eventsManager)
        self.onCarouselFilter = Event.Event(self._eventsManager)
        self.onOutfitChanged = Event.Event(self._eventsManager)
        self.onPropertySheetShow = Event.Event(self._eventsManager)
        return

    def init(self):
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onNotifySpaceMoved)
        g_currentVehicle.onChangeStarted += self.__onVehicleEntityChange
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreate

    def fini(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, self.__onNotifySpaceMoved)
        g_currentVehicle.onChangeStarted -= self.__onVehicleEntityChange
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.stopHighlighter()
        self._eventsManager.clear()

    def startHighlighter(self, mode=HighlightingMode.PAINT_REGIONS):
        entity = g_hangarSpace.getVehicleEntity()
        self._mode = mode
        if self._helper:
            self._helper.setSelectionMode(self._mode)
        else:
            self._helper = BigWorld.PyCustomizationHelper(entity, self._mode, self.__onRegionHighlighted)

    def stopHighlighter(self):
        self._helper = None
        self._needHelperRestart = False
        self._anchorPositions = None
        return

    def suspendHighlighter(self):
        if self._helper is None and self._needHelperRestart:
            return
        else:
            self._needHelperRestart = self._helper is not None
            self._anchorPositions = None
            self._helper = None
            return

    def resumeHighlighter(self):
        if self._needHelperRestart:
            self.startHighlighter(self._mode)
        self._needHelperRestart = False

    def getSelectionMode(self):
        return self._mode

    def getPointForRegionLeaderLine(self, areaId):
        return g_hangarSpace.getCentralPointForArea(areaId)

    def getPointForAnchorLeaderLine(self, areaId, slotId, regionId):
        anchorPos = None
        if self._anchorPositions is None:
            self._anchorPositions = g_currentVehicle.hangarSpace.getSlotPositions()
        area = self._anchorPositions.get(areaId, {})
        slot = area.get(slotId, ())
        if regionId < len(slot):
            anchorPos = slot[regionId].pos
        return anchorPos

    def getNormalForAnchorLeaderLine(self, areaId, slotId, regionId):
        anchorNorm = None
        if self._anchorPositions is None:
            self._anchorPositions = g_currentVehicle.hangarSpace.getSlotPositions()
        area = self._anchorPositions.get(areaId, {})
        slot = area.get(slotId, ())
        if regionId < len(slot):
            anchorNorm = slot[regionId].normal
        return anchorNorm

    def setSelectHighlighting(self, value):
        if self._helper:
            self._helper.setHighlightingEnabled(value)

    def getHightlighter(self):
        return self._helper

    def __onRegionHighlighted(self, args):
        areaID, regionID, selected, hovered = (-1,
         -1,
         False,
         False)
        if args:
            areaID, regionID, selected, hovered = args
        self.onRegionHighlighted(MODE_TO_C11N_TYPE[self._mode], areaID, regionID, selected, hovered)

    def __onSpaceCreate(self):
        self.resumeHighlighter()

    def __onSpaceDestroy(self, _):
        self.__onVehicleEntityChange()

    def __onVehicleEntityChange(self):
        self.suspendHighlighter()

    def __onNotifyCursorOver3dScene(self, event):
        if self._helper:
            isOver3dScene = event.ctx.get('isOver3dScene', False)
            self._helper.setSelectingEnabled(isOver3dScene)

    def __onNotifyCursorDragging(self, event):
        if self._helper:
            isDragging = event.ctx.get('isDragging', False)
            if not isDragging:
                self._helper.setCursorDragging(False)

    def __onNotifySpaceMoved(self, event):
        if self._helper:
            dx = event.ctx.get('dx')
            dy = event.ctx.get('dy')
            if dx or dy:
                self._helper.setCursorDragging(True)
