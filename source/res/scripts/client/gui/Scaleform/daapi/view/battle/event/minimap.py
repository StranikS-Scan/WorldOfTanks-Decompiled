# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/minimap.py
import logging
import BigWorld
import GUI
from constants import MarkerTypes, SE20_USE_DEATH_ZONE_ON_MINI_MAP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.epic.minimap import CenteredPersonalEntriesPlugin, MINIMAP_SCALE_TYPES, makeMousePositionToEpicWorldPosition
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
import Math
from gui.Scaleform.daapi.view.meta.EventMinimapMeta import EventMinimapMeta
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin, AttentionToCellPlugin
from gui.battle_control import minimap_utils, avatar_getter
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, EquipmentsPlugin
from helpers import isPlayerAvatar
from constants import EventMarkerBlinkingParams
from PlayerEvents import g_playerEvents
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_MINIMAP_ZOOM = 0.666
_FULLMAP_ZOOM = 1.0
_MINIMAP_1M_IN_PX = 0.21
_FULL_MAP_PATH = '_level0.root.{}.main.fullMap.mapContainer.entriesContainer'.format(APP_CONTAINERS_NAMES.VIEWS)
_logger = logging.getLogger(__name__)

class EventScalableEntriesPlugin(EntriesPlugin):

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = super(EventScalableEntriesPlugin, self)._addEntry(symbol, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryID)
        return entryID


class BotAppearNotificationPlugin(EventScalableEntriesPlugin):
    __slots__ = ('__callbackIDs', '__idGenerator')
    _ANIMATION_NAME = 'firstEnemy'

    def __init__(self, parent):
        super(BotAppearNotificationPlugin, self).__init__(parent, clazz=VehicleEntry)
        self.__waveUID = []
        self.__ignoringID = []

    def stop(self):
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleSpawnNotification -= self.__onVehicleSpawnNotification
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        self.__waveUID = []
        self.__ignoringID = []
        super(BotAppearNotificationPlugin, self).stop()
        return

    def start(self):
        super(BotAppearNotificationPlugin, self).start()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleSpawnNotification += self.__onVehicleSpawnNotification
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def __onVehicleSpawnNotification(self, waveUID, **kwargs):
        botsWaveUID = kwargs.get('botsWaveUID', {})
        if not botsWaveUID:
            if not waveUID or waveUID in self.__waveUID:
                return
            self.__waveUID.append(waveUID)
        else:
            waveUIDNeedDel = []
            for vehID, data in botsWaveUID.iteritems():
                waveUID = data['wUID']
                if waveUID not in self.__waveUID or vehID in self.__ignoringID:
                    continue
                position = data['position']
                if waveUID not in waveUIDNeedDel:
                    waveUIDNeedDel.append(waveUID)
                matrix = minimap_utils.makePositionMatrix(position)
                model = self._addEntryEx(vehID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
                self._invoke(model.getID(), 'setVehicleInfo', '', '', '', 'enemy', self._ANIMATION_NAME)
                self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

            self.__waveUID = list(set(self.__waveUID) - set(waveUIDNeedDel))

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        self.__ignoringID.append(vInfo.vehicleID)
        self._delEntryEx(vInfo.vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == _EVENT_ID.VEHICLE_DEAD or eventID == _EVENT_ID.MINIMAP_SHOW_MARKER or eventID == _EVENT_ID.PLAYER_KILLED_ENEMY:
            if vehicleID in self.__ignoringID:
                self.__ignoringID.remove(vehicleID)
            self._delEntryEx(vehicleID)


class LootObjectsEntriesPlugin(EventScalableEntriesPlugin):
    __slots__ = ('_lootDict',)

    def __init__(self, parentObj):
        super(LootObjectsEntriesPlugin, self).__init__(parentObj)
        self._lootDict = {}

    def start(self):
        super(LootObjectsEntriesPlugin, self).start()
        self._updateCurrentOpacity()
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded += self.__onLootAdded
            lootComp.onLootRemoved += self.__onLootRemoved
            lootEntities = lootComp.getLootEntities()
            for loot in lootEntities.values():
                self.__onLootAdded(loot)

        return

    def fini(self):
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded -= self.__onLootAdded
            lootComp.onLootRemoved -= self.__onLootRemoved
        super(LootObjectsEntriesPlugin, self).fini()
        return

    def _updateCurrentOpacity(self):
        pass

    def __onLootRemoved(self, loot):
        if loot.id in self._lootDict:
            self._delEntry(self._lootDict[loot.id])
            del self._lootDict[loot.id]

    def __onLootAdded(self, loot):
        minimapSymbol = loot.gameObject.minimapSymbol
        if minimapSymbol is not None:
            matrix = Math.Matrix()
            matrix.setTranslate(loot.position)
            lootEntryID = self._addEntry(minimapSymbol, _C_NAME.ICONS, matrix=matrix, active=True)
            self._lootDict[loot.id] = lootEntryID
        return


class EventArenaVehiclesPlugin(ArenaVehiclesPlugin, EventScalableEntriesPlugin):
    __slots__ = ()

    def start(self):
        super(EventArenaVehiclesPlugin, self).start()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotRolesReceived += self.__onBotRolesReceived

    def stop(self):
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotRolesReceived -= self.__onBotRolesReceived
        super(EventArenaVehiclesPlugin, self).stop()

    def updateControlMode(self, mode, vehicleID):
        prevCtrlID = self._ctrlVehicleID
        super(EventArenaVehiclesPlugin, self).updateControlMode(mode, vehicleID)
        if self._isInRespawnDeath():
            self.eventSwitchToVehicle(prevCtrlID)

    def _getClassTag(self, vInfo):
        player = BigWorld.player()
        if player.team == vInfo.team:
            return super(EventArenaVehiclesPlugin, self)._getClassTag(vInfo)
        vehicleID = vInfo.vehicleID
        botMarkerType = player.getBotMarkerType(vehicleID)
        return botMarkerType

    def __onBotRolesReceived(self):
        player = BigWorld.player()
        updated = ((0, vInfo) for vInfo in self._arenaDP.getVehiclesInfoIterator() if player.team != vInfo.team)
        self.updateVehiclesInfo(updated, self._arenaDP)


class EventAreaPointMarkerEntriesPlugin(EventScalableEntriesPlugin):
    __slots__ = ('_pointDict',)
    _CUSTOM_SYMBOL_NAME = 'EventCustomMinimapEntryUI'
    _ARROW_SYMBOL_NAME = 'EventArrowMinimapEntryUI'
    _POSITION_SYMBOL_NAME = 'EventPositionFlashEntryUI'
    _ICON_NAME = 'controlPointBoss'

    def __init__(self, parentObj):
        super(EventAreaPointMarkerEntriesPlugin, self).__init__(parentObj)
        self._pointDict = {}

    def start(self):
        super(EventAreaPointMarkerEntriesPlugin, self).start()
        areaPointMarkerCtrl = self.sessionProvider.dynamic.areaPointMarker
        if areaPointMarkerCtrl is not None:
            areaPointMarkerCtrl.onMiniMapUpdated += self.__onMiniMapUpdated
            areaPointMarkerCtrl.onStopBlinking += self.__onStopBlinking
        areaVehicleMarkerCtrl = self.sessionProvider.dynamic.areaVehicleMarker
        if areaVehicleMarkerCtrl is not None:
            areaVehicleMarkerCtrl.onMiniMapUpdatedByPosition += self.__onMiniMapUpdatedByPosition
        return

    def fini(self):
        areaPointMarkerCtrl = self.sessionProvider.dynamic.areaPointMarker
        if areaPointMarkerCtrl is not None:
            areaPointMarkerCtrl.onMiniMapUpdated -= self.__onMiniMapUpdated
            areaPointMarkerCtrl.onStopBlinking -= self.__onStopBlinking
        areaVehicleMarkerCtrl = self.sessionProvider.dynamic.areaVehicleMarker
        if areaVehicleMarkerCtrl is not None:
            areaVehicleMarkerCtrl.onMiniMapUpdatedByPosition -= self.__onMiniMapUpdatedByPosition
        self._pointDict = {}
        super(EventAreaPointMarkerEntriesPlugin, self).fini()
        return

    def __onMiniMapUpdated(self, pointID, matrix, isShow, markerType=None, onlyUpdatePosition=False, blinking=False):
        if isShow:
            if pointID in self._pointDict:
                if onlyUpdatePosition:
                    self._setMatrix(self._pointDict[pointID], matrix)
                    self._setMatrixEx(pointID, matrix)
                else:
                    self.__onRemoved(pointID)
                    self.__onAdded(pointID, matrix, markerType)
            else:
                self.__onAdded(pointID, matrix, markerType, blinking=blinking)
        else:
            self.__onRemoved(pointID)

    def __onMiniMapUpdatedByPosition(self, pointID, position, isShow, markerType=None, blinking=False):
        matrix = None
        if position:
            matrix = minimap_utils.makePositionMatrix(position)
        self.__onMiniMapUpdated(pointID, matrix, isShow, markerType, onlyUpdatePosition=True, blinking=blinking)
        return

    def __onRemoved(self, pointID):
        if pointID in self._pointDict:
            self._delEntry(self._pointDict[pointID])
            self._delEntryEx(pointID)
            del self._pointDict[pointID]

    def __onAdded(self, pointID, matrix, markerType, blinking=False):
        if markerType is None:
            markerType = self._ICON_NAME
        symbol = self.__getSymbolName(markerType)
        markerEntryID = self._addEntry(symbol, _C_NAME.ICONS, matrix=matrix, active=True)
        scale = self.__getScale(markerType)
        self._parentObj.setEntryParameters(markerEntryID, doClip=False, scaleType=scale)
        self._pointDict[pointID] = markerEntryID
        self._invoke(markerEntryID, 'setIcon', markerType)
        blinkingSpeed = self.__getBlinkingSpeed(markerType)
        if blinking:
            self._invoke(markerEntryID, 'setBlinking', True, blinkingSpeed)
        if markerType not in MarkerTypes.ARROW_MINI_MAP_MARKER_LIST:
            model = self._addEntryEx(pointID, self._POSITION_SYMBOL_NAME, _C_NAME.PERSONAL, matrix=matrix, active=True)
            if model:
                self._invoke(model.getID(), 'playAnimation')
        return

    def __onStopBlinking(self, pointID):
        if pointID in self._pointDict:
            self._invoke(self._pointDict[pointID], 'setBlinking', False, 0)

    def __getSymbolName(self, markerType):
        return self._ARROW_SYMBOL_NAME if markerType in MarkerTypes.ARROW_MINI_MAP_MARKER_LIST else self._CUSTOM_SYMBOL_NAME

    def __getBlinkingSpeed(self, markerType):
        return EventMarkerBlinkingParams.BLINKING_SPEED_ARROW_MARKER_MS.value if markerType in MarkerTypes.ARROW_MINI_MAP_MARKER_LIST else EventMarkerBlinkingParams.BLINKING_SPEED_CUSTOM_MARKER_MS.value

    def __getScale(self, markerType):
        return MINIMAP_SCALE_TYPES.REAL_SCALE if markerType in MarkerTypes.ARROW_MINI_MAP_MARKER_LIST else MINIMAP_SCALE_TYPES.ADAPTED_SCALE


class EventHighlightMarkerEntriesPlugin(EventScalableEntriesPlugin):
    __slots__ = ('_dict',)
    _SYMBOL_NAME = 'EventHighlightMinimapEntryUI'
    _ANIMATION_NAME = 'firstEnemy'

    def __init__(self, parentObj):
        super(EventHighlightMarkerEntriesPlugin, self).__init__(parentObj)
        self._dict = {}

    def start(self):
        super(EventHighlightMarkerEntriesPlugin, self).start()
        markerCtrl = self.sessionProvider.dynamic.highlightMarker
        if markerCtrl is not None:
            markerCtrl.onMiniMapUpdated += self.__onMiniMapUpdated
        return

    def fini(self):
        markerCtrl = self.sessionProvider.dynamic.highlightMarker
        if markerCtrl is not None:
            markerCtrl.onMiniMapUpdated -= self.__onMiniMapUpdated
        self._dict = {}
        super(EventHighlightMarkerEntriesPlugin, self).fini()
        return

    def __onMiniMapUpdated(self, vehicleID, position, classTag='SPG'):
        if vehicleID not in self._dict:
            if position:
                self.__onAdded(vehicleID, position, classTag)
        else:
            self.__onRemoved(vehicleID)

    def __onRemoved(self, vehicleID):
        if vehicleID in self._dict:
            self._delEntry(self._dict[vehicleID])
            self._delEntryEx(vehicleID)
            del self._dict[vehicleID]

    def __onAdded(self, vehicleID, position, classTag):
        matrix = minimap_utils.makePositionMatrix(position)
        markerEntryID = self._addEntry(self._SYMBOL_NAME, _C_NAME.ICONS, matrix=matrix, active=True)
        self._dict[vehicleID] = markerEntryID
        model = self._addEntryEx(vehicleID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', vehicleID, classTag, '', '', self._ANIMATION_NAME)


class EventMarkPositionPlugin(AttentionToCellPlugin, EventScalableEntriesPlugin):
    __slots__ = ()

    def setAttentionToCell(self, x, y, isRightClick):
        finalPos = self._getPositionFromClick(x, y)
        if isRightClick:
            handler = avatar_getter.getInputHandler()
            if handler is not None:
                handler.onMinimapClicked(finalPos)
        else:
            commands = self.sessionProvider.shared.chatCommands
            if commands is not None:
                commands.sendAttentionToPosition(finalPos)
        return

    def _doAttention(self, index, duration):
        pass

    def _doAttentionAtPosition(self, senderID, position, duration):
        self._doAttentionToItem(position, _S_NAME.MARK_POSITION, duration)

    def _doAttentionToObjective(self, senderID, hqIdx, duration):
        pass

    def _doAttentionToBase(self, senderID, baseIdx, baseName, duration):
        pass

    def _doAttentionToItem(self, position, entryName, duration):
        uniqueID = position.tuple()
        if self._isCallbackExisting(uniqueID):
            self._clearCallback(uniqueID)
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        model = self._addEntryEx(uniqueID, entryName, _C_NAME.PERSONAL, matrix=matrix, active=True)
        if model:
            self._invoke(model.getID(), 'playAnimation')
            self._setCallback(uniqueID, duration)
            self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

    def _getPositionFromClick(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds())


class DeathZonesMinimapComponent(EntriesPlugin):
    __slots__ = ('_activeDeathZones',)
    _SYMBOL_NAME = 'EventDeathZoneMinimapEntryUI'

    def __init__(self, parentObj):
        super(DeathZonesMinimapComponent, self).__init__(parentObj)
        self._activeDeathZones = {}

    def start(self):
        super(DeathZonesMinimapComponent, self).start()
        g_playerEvents.onDeathZoneActivated += self._onDeathZoneActivated
        g_playerEvents.onDeathZoneDeactivated += self._onDeathZoneDeactivated

    def fini(self):
        g_playerEvents.onDeathZoneActivated -= self._onDeathZoneActivated
        g_playerEvents.onDeathZoneDeactivated -= self._onDeathZoneDeactivated
        super(DeathZonesMinimapComponent, self).fini()

    def _onDeathZoneActivated(self, zone):
        zoneId = zone.zoneId
        topLeft, bottomRight = zone.getCorners()
        if zoneId in self._activeDeathZones:
            return
        deathBox = (bottomRight - topLeft) * _MINIMAP_1M_IN_PX * 2
        matrix = Math.Matrix()
        matrix.setTranslate(topLeft)
        entryID = self._addEntry(self._SYMBOL_NAME, _C_NAME.ICONS, matrix=matrix, active=True)
        self._parentObj.setEntryParameters(entryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        self._activeDeathZones[zoneId] = entryID
        self._invoke(entryID, 'setZoneSize', abs(deathBox[0]), abs(deathBox[2]))

    def _onDeathZoneDeactivated(self, zoneId):
        entryID = self._activeDeathZones.pop(zoneId, None)
        if entryID:
            self._delEntry(entryID)
        return


class MiniMapBackground(EntriesPlugin, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _IMAGE_EVENT_PATH_FORMATTER = 'img://spaces/{}/event/{}.dds'
    _IMAGE_PATH_FORMATTER = 'img://spaces/{}/{}.dds'

    def __init__(self, parentObj):
        super(MiniMapBackground, self).__init__(parentObj)
        GameEventGetterMixin.__init__(self)

    def start(self):
        super(MiniMapBackground, self).start()
        self.minimapInfo.onUpdated += self.__updateMiniMapBackground
        self.__updateMiniMapBackground()

    def fini(self):
        self.minimapInfo.onUpdated -= self.__updateMiniMapBackground
        super(MiniMapBackground, self).fini()

    def _getMiniMapGeometryName(self):
        arenaVisitor = self.sessionProvider.arenaVisitor
        return arenaVisitor.type.getGeometryName() if arenaVisitor else None

    def _getMinimapInitialState(self, scenarioID):
        arenaVisitor = self.sessionProvider.arenaVisitor
        if arenaVisitor:
            initialMinimapIDs = arenaVisitor.type.getInitialMinimapIDs()
            return initialMinimapIDs.get(scenarioID, None)
        else:
            return None

    def __updateMiniMapBackground(self):
        geometryName = self._getMiniMapGeometryName()
        if not geometryName:
            return
        minimapID = self.minimapInfo.getMinimapId()
        if not minimapID:
            scenarioID = BigWorld.player().arena.extraData['activeScenarioName']
            minimapID = self._getMinimapInitialState(scenarioID)
            if not minimapID:
                return
        path = self._IMAGE_EVENT_PATH_FORMATTER.format(geometryName, minimapID) if minimapID != self.minimapInfo.DEFAULT_MINIMAP_ID else self._IMAGE_PATH_FORMATTER.format(geometryName, minimapID)
        if self._parentObj:
            self._parentObj.as_setBackgroundS(path)


class EventMinimapComponent(EventMinimapMeta):

    def __init__(self):
        super(EventMinimapComponent, self).__init__()
        self._size = minimap_utils.MINIMAP_SIZE

    def changeMinimapZoom(self, mode):
        self.getComponent().changeMinimapZoom(mode)

    def setEntryParameters(self, entryId, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        self.getComponent().setEntryParameters(entryId, doClip, scaleType)

    def setMinimapCenterEntry(self, entryID):
        self.getComponent().setMinimapCenterEntry(entryID)

    def onZoomModeChanged(self, change):
        pass

    def getVisualBounds(self):
        return self.getComponent().getVisualBound()

    def isModalViewShown(self):
        page = self.app.containerManager.getContainer(ViewTypes.DEFAULT).findView(ViewKey(VIEW_ALIAS.EVENT_BATTLE_PAGE))
        return True if page.hasFullScreenView() else super(EventMinimapComponent, self).isModalViewShown()

    def _createFlashComponent(self):
        return GUI.WGScrollingMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _processMinimapSize(self, minSize, maxSize):
        mapWidthPx, mapHeightPx = self._calculateDimensions(minSize, maxSize)
        self._size = (mapWidthPx, mapHeightPx)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['bot_appear_notification'] = BotAppearNotificationPlugin
        setup['loot_objects'] = LootObjectsEntriesPlugin
        setup['vehicles'] = EventArenaVehiclesPlugin
        setup['area_point_marker'] = EventAreaPointMarkerEntriesPlugin
        setup['highlight'] = EventHighlightMarkerEntriesPlugin
        if SE20_USE_DEATH_ZONE_ON_MINI_MAP:
            setup['deathzones'] = DeathZonesMinimapComponent
        setup['personal'] = CenteredPersonalEntriesPlugin
        setup['cells'] = EventMarkPositionPlugin
        setup['minimap_background'] = MiniMapBackground
        return setup

    def _populate(self):
        super(EventMinimapComponent, self)._populate()
        self.changeMinimapZoom(self._getZoom())

    def _getZoom(self):
        return _MINIMAP_ZOOM

    @staticmethod
    def _calculateDimensions(minSize, maxSize):
        mapWidthPx = abs(maxSize[0] - minSize[0]) * _MINIMAP_1M_IN_PX
        mapHeightPx = abs(maxSize[1] - minSize[1]) * _MINIMAP_1M_IN_PX
        return (mapWidthPx, mapHeightPx)


class FullMapEquipmentsPlugin(EquipmentsPlugin, EventScalableEntriesPlugin):
    pass


class EventFullMapComponent(EventMinimapComponent):

    def __init__(self):
        super(EventFullMapComponent, self).__init__()
        self._bounds = None
        return

    def _getFlashName(self):
        pass

    def getVisualBounds(self):
        if not self._bounds:
            return (0, 0, 0, 0)
        minSize, maxSize = self._bounds
        return (minSize[0],
         maxSize[1],
         maxSize[0],
         minSize[1])

    def _createFlashComponent(self):
        return GUI.WGFullMinimapGUIComponentAS3(self.app.movie, _FULL_MAP_PATH)

    def setMinimapCenterEntry(self, entryID):
        pass

    def changeMinimapZoom(self, mode):
        pass

    def _getMinimapSize(self):
        return self._size

    def _getZoom(self):
        return _FULLMAP_ZOOM

    def _processMinimapSize(self, minSize, maxSize):
        mapWidthPx, mapHeightPx = self._calculateDimensions(minSize, maxSize)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)
        self._size = (mapWidthPx, mapHeightPx)
        self._bounds = (minSize, maxSize)

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventFullMapComponent, self)._setupPlugins(arenaVisitor)
        setup['equipments'] = FullMapEquipmentsPlugin
        return setup

    def setEntryParameters(self, entryId, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        if scaleType != MINIMAP_SCALE_TYPES.REAL_SCALE:
            scaleType = MINIMAP_SCALE_TYPES.FULLMAP_SCALE
        super(EventFullMapComponent, self).setEntryParameters(entryId, doClip, scaleType)
