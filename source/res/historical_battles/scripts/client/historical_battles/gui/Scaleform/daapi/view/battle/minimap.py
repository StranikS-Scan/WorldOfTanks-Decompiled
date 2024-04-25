# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/minimap.py
import logging
from typing import TYPE_CHECKING, Dict
from collections import namedtuple
from functools import partial
import BigWorld
import GUI
import Math
import math_utils
from HBAttackDirectionMarkerComponent import HBAttackDirectionMarkerComponent
from constants import EventMarkerBlinkingParams
from helpers import CallbackDelayer
from HBVehicleRoleComponent import HBVehicleRoleComponent
from gui.Scaleform.daapi.view.battle.epic.minimap import MINIMAP_SCALE_TYPES, CenteredPersonalEntriesPlugin, makeMousePositionToEpicWorldPosition
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, MinimapPingPlugin, EquipmentsPlugin
from gui.Scaleform.daapi.view.battle.classic.minimap import TeamsOrControlsPointsPlugin, GlobalSettingsPlugin
from gui.Scaleform.daapi.view.meta.HBMinimapMeta import HBMinimapMeta
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.battle_control import minimap_utils, matrix_factory, avatar_getter
from gui.battle_control.battle_constants import VEHICLE_LOCATION
from battle_royale.gui.battle_control.controllers.radar_ctrl import IRadarListener
from chat_commands_consts import MarkerType, INVALID_TARGET_ID, LocationMarkerSubType
from historical_battles.gui.Scaleform.daapi.view.battle.mini_map_background import MiniMapBackground
from historical_battles.gui.battle_control.hb_battle_constants import FEEDBACK_EVENT_ID
from historical_battles.gui.Scaleform.daapi.view.battle.markers import HBObjectivesMinimapEntry
from historical_battles.gui.Scaleform.daapi.view.battle.components import HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent, sendPlayerReplyForMarker
from TeamBase import CAPTURE_POINTS_LIMIT
if TYPE_CHECKING:
    from gui.battle_control.controllers.feedback_adaptor import BattleFeedbackAdaptor
    from HBVehiclePositionsComponent import HBVehiclePositionsComponent
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_LOOT_AMMO_SYMBOL_NAME = 'TutorialTargetMinimapEntryUI'
_HB_ARTY_MARKER = 'HistoricalAirstrikeMarkerMinimapEntry'
_HB_BOMBER_CAS_MARKER = 'BomberCasEntry'
_HB_MINEFIELD_MARKER = 'MineEntry'
_HISTORICAL_BATTLE_BASE_ID = 8
_FULLMAP_ZOOM = 1.0
_MINIMAP_ZOOM = 0.666
_MINIMAP_1M_IN_PX = 0.21
_FULL_MAP_PATH = '_level0.root.{}.main.fullMap.mapContainer.entriesContainer'.format(LAYER_NAMES.VIEWS)
_logger = logging.getLogger(__name__)

class EventScalableEntriesPlugin(EntriesPlugin):

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        entryID = super(EventScalableEntriesPlugin, self)._addEntry(symbol, container, matrix, active, transformProps)
        self._parentObj.setEntryParameters(entryID)
        return entryID


class BotAppearNotificationPlugin(EntriesPlugin):
    _ANIMATION_NAME = 'firstEnemy'
    _ENEMY_MARKER = 'enemy'
    _MARKER_CLEAR_EVENTS = {FEEDBACK_EVENT_ID.VEHICLE_DEAD, FEEDBACK_EVENT_ID.MINIMAP_SHOW_MARKER, FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY}

    def __init__(self, parent):
        super(BotAppearNotificationPlugin, self).__init__(parent, clazz=VehicleEntry)

    @classmethod
    def getHBVehiclePositions(cls):
        return BigWorld.player().arena.arenaInfo.hbVehiclePositionsComponent

    @classmethod
    def getBattleFeedback(cls):
        return cls.sessionProvider.shared.feedback

    def stop(self):
        ctrl = self.getBattleFeedback()
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if BigWorld.player() is not None:
            arena = BigWorld.player().arena
            if arena is not None:
                arena.arenaInfo.hbVehiclePositionsComponent.onReceive -= self.__onVehicleSpawnNotification
        super(BotAppearNotificationPlugin, self).stop()
        return

    def start(self):
        super(BotAppearNotificationPlugin, self).start()
        self.getHBVehiclePositions().onReceive += self.__onVehicleSpawnNotification
        ctrl = self.getBattleFeedback()
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def __onVehicleSpawnNotification(self, package):
        for entityID, position in package.iteritems():
            if self.getBattleFeedback().getVehicleProxy(entityID) is not None:
                continue
            matrix = minimap_utils.makePositionMatrix(position)
            model = self._addEntryEx(entityID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
            self._invoke(model.getID(), 'setVehicleInfo', '', '', '', self._ENEMY_MARKER, self._ANIMATION_NAME)

        return

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        self._delEntryEx(vInfo.vehicleID)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID in self._MARKER_CLEAR_EVENTS:
            self._delEntryEx(vehicleID)


class LootObjectsEntriesPlugin(EntriesPlugin):
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

    def _setLootHighlight(self, lootEntryID):
        self._invoke(lootEntryID, 'setHighlight', False)

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
            if minimapSymbol == _LOOT_AMMO_SYMBOL_NAME:
                self._setLootHighlight(lootEntryID)
        return


RadarEntryParams = namedtuple('RadarEntryParams', 'symbol container')
RadarPluginParams = namedtuple('RadarPluginParams', 'fadeIn fadeOut lifetime vehicleEntryParams')

class _RadarEntryData(object):

    def __init__(self, entryId, destroyMeCallback, lifeTime, typeId=None):
        super(_RadarEntryData, self).__init__()
        self.__entryId = entryId
        self.__lifeTime = lifeTime
        self.__destroyMeCallback = destroyMeCallback
        self.__typeId = typeId
        self.__timerId = None
        return

    @property
    def entryId(self):
        return self.__entryId

    def getTypeId(self):
        return self.__typeId

    def destroy(self):
        self.stopTimer()
        self.__timerId = None
        self.__destroyMeCallback = None
        return

    def upTimer(self):
        self.stopTimer()
        self.__timerId = BigWorld.callback(self.__lifeTime, partial(self.__destroyMeCallback, self.__entryId))

    def stopTimer(self):
        if self.__timerId is not None:
            BigWorld.cancelCallback(self.__timerId)
        return


class RadarPlugin(EntriesPlugin, IRadarListener):
    _NOTIFICATION_DURATION = 3
    _ANIMATION_NAME = 'firstEnemy'

    def __init__(self, parent):
        super(RadarPlugin, self).__init__(parent)
        self._vehicleEntries = {}
        self._params = RadarPluginParams(fadeIn=0.0, fadeOut=0.0, lifetime=0.0, vehicleEntryParams=RadarEntryParams(container='', symbol=''))
        self._callbackIDs = {}

    def init(self, arenaVisitor, arenaDP):
        super(RadarPlugin, self).init(arenaVisitor, arenaDP)
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.addRuntimeView(self)

    def fini(self):
        self._clearAllCallbacks()
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.removeRuntimeView(self)
        super(RadarPlugin, self).fini()

    def radarInfoReceived(self, duration, positions):
        for _id, _pos in positions:
            self._addVehicleEntry(_id, _pos, duration)

        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

    def _addVehicleEntry(self, vehicleID, position, duration):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(vehicleID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', vehicleID, '', '', '', self._ANIMATION_NAME)
        self._scheduleCleanup(vehicleID, duration)

    def _scheduleCleanup(self, vehicleID, interval):
        self._clearCallback(vehicleID)
        self._callbackIDs[vehicleID] = BigWorld.callback(interval, partial(self._clearCallback, vehicleID))

    def _clearCallback(self, vehicleID):
        callbackID = self._callbackIDs.pop(vehicleID, None)
        if callbackID is not None:
            self._delEntryEx(vehicleID)
            BigWorld.cancelCallback(callbackID)
        return

    def _clearAllCallbacks(self):
        for uniqueID, callbackID in self._callbackIDs.iteritems():
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)

        self._callbackIDs.clear()


class EventArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def start(self):
        super(EventArenaVehiclesPlugin, self).start()
        HBVehicleRoleComponent.onRoleUpdated += self._onRoleUpdated

    def stop(self):
        HBVehicleRoleComponent.onRoleUpdated -= self._onRoleUpdated
        super(EventArenaVehiclesPlugin, self).stop()

    def updateControlMode(self, mode, vehicleID):
        prevCtrlID = self._ctrlVehicleID
        super(EventArenaVehiclesPlugin, self).updateControlMode(mode, vehicleID)
        if self._isInRespawnDeath():
            self.eventSwitchToVehicle(prevCtrlID)

    def _getClassTag(self, vInfo):
        vehicle = BigWorld.entities.get(vInfo.vehicleID)
        if vehicle:
            if 'roleComponent' in vehicle.dynamicComponents and vehicle.roleComponent.vehicleRole:
                return vehicle.roleComponent.getRoleIconName()
        return super(EventArenaVehiclesPlugin, self)._getClassTag(vInfo)

    def _onRoleUpdated(self, component):
        vInfo = self._arenaDP.getVehicleInfo(component.entity.id)
        self.updateVehiclesInfo(((0, vInfo),), self._arenaDP)

    def updateVehiclePosition(self, vehicleID, position):
        entry = self._entries.get(vehicleID)
        self._setInAoI(entry, True)
        self._setActive(entry.getID(), True)
        matrix = entry.getMatrix()
        if matrix is None:
            matrix = matrix_factory.makePositionMP(position)
            entry.setMatrix(matrix)
            self._setMatrix(entry.getID(), matrix)
        else:
            matrix.source.setTranslate(position)
        entry.setLocation(VEHICLE_LOCATION.AOI)
        return


class HistoricalBattlesMinimapPingPlugin(MinimapPingPlugin):
    _LOCATION_PING_RANGE = 30

    def _getClickPosition(self, x, y):
        return makeMousePositionToEpicWorldPosition(x, y, self._parentObj.getVisualBounds())

    def _getIdByBaseNumber(self, team, number):
        pass

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        if avatar_getter.isVehicleAlive():
            vehicleID = self._getNearestVehicleIDForPosition(position, self._LOCATION_PING_RANGE)
            if vehicleID is not None:
                sendPlayerReplyForMarker(self.sessionProvider, vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
                return
            locationID = self._getNearestLocationIDForPosition(position, self._LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
        commands.sendAttentionToPosition3D(position, locationCommand)
        return

    def _getNearestVehicleIDForPosition(self, position, pRange):
        vehiclesIterator = (BigWorld.entities.get(vInfo.vehicleID) for vInfo in self.sessionProvider.getArenaDP().getVehiclesInfoIterator())
        closestVehicle = min((vehicle for vehicle in vehiclesIterator if vehicle is not None and vehicle.isStarted), key=lambda entity: Math.Vector3(entity.position).flatDistTo(Math.Vector3(position)))
        return closestVehicle.id if Math.Vector3(closestVehicle.position).flatDistTo(Math.Vector3(position)) < pRange else None


class HistoricalMinimapComponent(HBMinimapMeta):

    def __init__(self):
        super(HistoricalMinimapComponent, self).__init__()
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

    def _createFlashComponent(self):
        return GUI.WGScrollingMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _processMinimapSize(self, minSize, maxSize):
        mapWidthPx, mapHeightPx = self._calculateDimensions(minSize, maxSize)
        self._size = (mapWidthPx, mapHeightPx)
        self.as_setMapDimensionsS(mapWidthPx, mapHeightPx)

    def _setupPlugins(self, arenaVisitor):
        setup = super(HistoricalMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['bot_appear_notification'] = BotAppearNotificationPlugin
        setup['loot_objects'] = LootObjectsEntriesPlugin
        setup['vehicles'] = EventArenaVehiclesPlugin
        setup['personal'] = CenteredPersonalEntriesPlugin
        setup['pinging'] = HistoricalBattlesMinimapPingPlugin
        setup['equipments'] = HistoricalEquipmentsPlugin
        setup['minimap_background'] = MiniMapBackground
        setup['attack_direction'] = HistoricalAttackDirectionPlugin
        setup['objectives'] = HBObjectivesPointMarkerPlugin
        setup['points'] = HBTeamsOrControlsPointsPlugin
        setup['settings'] = HBGlobalSettingsPlugin
        return setup

    def _populate(self):
        super(HistoricalMinimapComponent, self)._populate()
        self.changeMinimapZoom(self._getZoom())

    def _getZoom(self):
        return _MINIMAP_ZOOM

    @staticmethod
    def _calculateDimensions(minSize, maxSize):
        mapWidthPx = abs(maxSize[0] - minSize[0]) * _MINIMAP_1M_IN_PX
        mapHeightPx = abs(maxSize[1] - minSize[1]) * _MINIMAP_1M_IN_PX
        return (mapWidthPx, mapHeightPx)


class HBObjectivesPointMarkerPlugin(EntriesPlugin, HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent):
    __slots__ = ('__delayer',)

    def __init__(self, parent):
        super(HBObjectivesPointMarkerPlugin, self).__init__(parent, clazz=HBObjectivesMinimapEntry)
        self.__delayer = CallbackDelayer.CallbacksSetByID()

    def stop(self):
        self.__delayer.clear()
        HBStaticObjectivesMarkerComponent.stop(self)
        HBVehicleObjectivesMarkerComponent.stop(self)
        super(HBObjectivesPointMarkerPlugin, self).stop()

    def start(self):
        super(HBObjectivesPointMarkerPlugin, self).start()
        HBStaticObjectivesMarkerComponent.start(self)
        HBVehicleObjectivesMarkerComponent.start(self)

    def getMarkerType(self):
        return MarkerType.LOCATION_MARKER_TYPE

    def getMarkerSubType(self):
        return LocationMarkerSubType.OBJECTIVES_POINT_SUBTYPE

    def getTargetIDFromMarkerID(self, markerID):
        return next((tID for tID, marker in self._entries.iteritems() if marker.getID() == markerID), INVALID_TARGET_ID)

    def _getTargetIDFromVehicleID(self, vehicleID):
        return next((tID for tID, marker in self._entries.iteritems() if marker.ownVehicleID == vehicleID), INVALID_TARGET_ID)

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        return self._entries.get(markerID, defaultMarker) if markerType == self.getMarkerType() else defaultMarker

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._getMarker(targetID, markerType)

    def _playAnimation(self, targetID, animationName):
        marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
        if marker is not None:
            self._invoke(marker.getID(), 'setBlinking', True, self._clazz.ANIMATION_SPEED)
            marker.animationID = self._parentObj.addEntry(animationName, _C_NAME.EQUIPMENTS, matrix=marker.getMatrix(), active=True)
            self.__delayer.delayCallback(targetID, self._clazz.ANIMATION_LIFETIME, self._stopAnimation, targetID)
        return

    def _stopAnimation(self, targetID):
        if self.__delayer.hasDelayedCallbackID(targetID):
            self.__delayer.stopCallback(targetID)
            marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
            if marker is not None:
                self._invoke(marker.getID(), 'setBlinking', False, 0)
                if marker.animationID:
                    self._parentObj.delEntry(marker.animationID)
        return

    def _addMarker(self, targetID, position, featureID):
        matrix = matrix_factory.makePositionMP(position)
        isAlly = self.sessionProvider.getArenaDP().isAlly(featureID) if featureID else False
        marker = self._addEntryEx(targetID, self._clazz.FLASH_SYMBOL_NAME, _C_NAME.EQUIPMENTS, matrix=matrix, active=not isAlly)
        marker.setMatrix(matrix)
        marker.ownVehicleID = featureID
        marker.isAlly = isAlly
        marker.isGoalForPlayer = False
        self._parentObj.setEntryParameters(marker.getID(), doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE)
        self._invoke(marker.getID(), 'setIcon', self._clazz.GOAL_ICON)
        self._playAnimation(targetID, self._clazz.SPOTTED_ANIMATION)

    def _removeMarker(self, targetID, markerType):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is not None:
            self._stopAnimation(targetID)
            self._delEntryEx(targetID)
        return

    def _setMarkerMatrix(self, markerID, matrix):
        marker = self._getMarkerFromTargetID(self.getTargetIDFromMarkerID(markerID), self.getMarkerType())
        if marker is not None:
            marker.setMatrix(matrix)
            self._setMatrix(marker.getID(), matrix)
        return

    def _updateMarker(self, targetID, isReplied, replierVehicleID):
        marker = self._getMarkerFromTargetID(targetID, self.getMarkerType())
        if marker is not None:
            if replierVehicleID == self.sessionProvider.arenaVisitor.getArenaUniqueID():
                if marker.isGoalForPlayer:
                    self._playAnimation(targetID, self._clazz.ONCALL_ANIMATION)
            else:
                self._invoke(marker.getID(), 'setIcon', self._clazz.GOAL_REPLIED_ICON if isReplied else self._clazz.GOAL_ICON)
        return

    def _setMarkerActive(self, markerID, shouldNotHide):
        pass

    def invokeMarker(self, markerID, function, *args):
        pass

    def _setMarkerSticky(self, markerID, isSticky):
        pass

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        pass


class HistoricalEquipmentsPlugin(EquipmentsPlugin):
    _HB_EQ_MARKER_TO_SYMBOL = {'death': _HB_ARTY_MARKER,
     'bomberCas': _HB_BOMBER_CAS_MARKER,
     'minefield': _HB_MINEFIELD_MARKER}

    def _getMarkerSymbol(self, marker):
        symbol = self._HB_EQ_MARKER_TO_SYMBOL.get(marker)
        return symbol or super(HistoricalEquipmentsPlugin, self)._getMarkerSymbol(marker)


class FullMapEquipmentsPlugin(HistoricalEquipmentsPlugin, EventScalableEntriesPlugin):
    pass


class HistoricalFullMapComponent(HistoricalMinimapComponent):

    def __init__(self):
        super(HistoricalFullMapComponent, self).__init__()
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
        return GUI.WGScrollingMinimapGUIComponentAS3(self.app.movie, _FULL_MAP_PATH)

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
        setup = super(HistoricalFullMapComponent, self)._setupPlugins(arenaVisitor)
        setup['equipments'] = FullMapEquipmentsPlugin
        return setup

    def setEntryParameters(self, entryId, doClip=True, scaleType=MINIMAP_SCALE_TYPES.ADAPTED_SCALE):
        if scaleType != MINIMAP_SCALE_TYPES.REAL_SCALE:
            scaleType = MINIMAP_SCALE_TYPES.FULLMAP_SCALE
        super(HistoricalFullMapComponent, self).setEntryParameters(entryId, doClip, scaleType)


class HistoricalAttackDirectionPlugin(EventScalableEntriesPlugin):
    _SYMBOL = 'HBArrowMinimapEntryUI'

    def __init__(self, *args, **kwargs):
        super(HistoricalAttackDirectionPlugin, self).__init__(*args, **kwargs)
        self._displayedMarkers = {}
        self._blinkingCallbacks = {}

    def start(self):
        super(HistoricalAttackDirectionPlugin, self).start()
        HBAttackDirectionMarkerComponent.onMarkersUpdated += self.__onMarkersUpdated

    def fini(self):
        for callbackId in self._blinkingCallbacks.itervalues():
            BigWorld.cancelCallback(callbackId)

        self._blinkingCallbacks.clear()
        self._displayedMarkers.clear()
        HBAttackDirectionMarkerComponent.onMarkersUpdated -= self.__onMarkersUpdated
        super(HistoricalAttackDirectionPlugin, self).fini()

    def __onMarkersUpdated(self, currentMarkers):
        currentMarkersIds = [ marker['markerID'] for marker in currentMarkers ]
        addedMarkers = [ marker for marker in currentMarkers if marker['markerID'] not in self._displayedMarkers ]
        for marker in addedMarkers:
            self.__addMarker(**marker)

        removedMarkers = [ markerID for markerID in self._displayedMarkers if markerID not in currentMarkersIds ]
        for markerID in removedMarkers:
            self.__removeMarker(markerID)

    def __addMarker(self, markerID, markerType, position, yaw):
        matrix = math_utils.createRTMatrix(Math.Vector3(yaw, 0.0, 0.0), position)
        markerEntryID = self._addEntry(self._SYMBOL, _C_NAME.ICONS, matrix=matrix, active=True)
        self._parentObj.setEntryParameters(markerEntryID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)
        self._invoke(markerEntryID, 'setIcon', markerType)
        self._invoke(markerEntryID, 'setBlinking', True, EventMarkerBlinkingParams.BLINKING_SPEED_ARROW_MARKER_MS.value)
        self._blinkingCallbacks[markerID] = BigWorld.callback(EventMarkerBlinkingParams.BLINKING_DURATION_ARROW_MARKER.value, partial(self.__stopBlinking, markerID))
        self._displayedMarkers[markerID] = markerEntryID

    def __removeMarker(self, markerID):
        self._delEntry(self._displayedMarkers[markerID])
        del self._displayedMarkers[markerID]

    def __stopBlinking(self, markerId):
        if markerId in self._blinkingCallbacks:
            self._invoke(self._displayedMarkers[markerId], 'setBlinking', False, 0)
            del self._blinkingCallbacks[markerId]


class HBTeamsOrControlsPointsPlugin(TeamsOrControlsPointsPlugin):

    def start(self):
        super(HBTeamsOrControlsPointsPlugin, self).start()
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.onBaseTeamChanged += self.__onBaseTeamChanged
            ctrl.onTeamBasePointsUpdated += self.__onTeamBasePointsUpdated
            ctrl.onBaseCapturingStopped += self.__onBaseCapturingStopped
        return

    def stop(self):
        super(HBTeamsOrControlsPointsPlugin, self).stop()
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.onBaseTeamChanged -= self.__onBaseTeamChanged
            ctrl.onTeamBasePointsUpdated -= self.__onTeamBasePointsUpdated
            ctrl.onBaseCapturingStopped -= self.__onBaseCapturingStopped
        return

    def _addTeamBasePositions(self):
        teamBases = self.sessionProvider.dynamic.teamBases.getTeamBases()
        for base in teamBases.itervalues():
            isPlayerTeam = base.team == self._personalTeam
            if isPlayerTeam:
                symbol = _S_NAME.EPIC_SECTOR_ALLY_BASE
            else:
                symbol = _S_NAME.EPIC_SECTOR_ENEMY_BASE
            model = self._addEntryEx(base.baseID, symbol, _C_NAME.TEAM_POINTS, matrix=base.matrix, active=True)
            if model is not None:
                self._markerIDs[base.baseID] = model
                self._invoke(model.getID(), 'setOwningTeam', isPlayerTeam)
                self._invoke(model.getID(), 'setIdentifier', _HISTORICAL_BATTLE_BASE_ID)
                self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)

        return

    def __onTeamBasePointsUpdated(self, baseID, points):
        model = self._markerIDs.get(baseID)
        if model is not None:
            self._invoke(model.getID(), 'setCapturePoints', points / CAPTURE_POINTS_LIMIT)
        return

    def __onBaseTeamChanged(self, baseID, team):
        model = self._markerIDs.get(baseID)
        if model is not None:
            self._invoke(model.getID(), 'setCapturePoints', 0)
            self._invoke(model.getID(), 'setOwningTeam', team == self._personalTeam)
        return

    def __onBaseCapturingStopped(self, baseID, team):
        model = self._markerIDs.get(baseID)
        if model is not None:
            self._invoke(model.getID(), 'setCapturePoints', 0)
        return


class HBGlobalSettingsPlugin(GlobalSettingsPlugin):

    def _toogleVisible(self):
        pass
