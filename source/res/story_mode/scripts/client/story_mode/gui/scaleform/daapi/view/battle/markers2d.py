# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/markers2d.py
import math
from logging import getLogger
import BigWorld
import CGF
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.aih_global_binding import BINDING_ID
from BunkerLogicComponent import BunkerLogicComponent
from Math import Vector4, Vector2, Matrix, Vector3
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker, VehicleMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, MARKER_EMPTY_HIT_STATE, PLAYER_GUI_PROPS
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.skeletons.voiceover_controller import IVoiceoverManager
from story_mode_common.story_mode_constants import LOGGER_NAME
from vehicle_systems.tankStructure import TankNodeNames, TankPartIndexes
_MARKER_CRITICAL_HIT_STATES = {FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT, FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS, FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED}
_logger = getLogger(LOGGER_NAME)
_MEDIUM_MARKER_MIN_SCALE = 100
_MAX_CULL_DISTANCE = 1000000.0
_BUNKER_BOUNDS_MIN_SCALE = Vector2(1.0, 0.8)
_BUNKER_BOUNDS = Vector4(50, 50, 30, 65)
_INNER_BUNKER_BOUNDS = Vector4(17, 17, 18, 25)
_BUNKER_OWNER = 'enemy'
_BUNKER_ALIVE_STATE = 'alive'
BUNKER_SYMBOL = 'BunkerMarkerUI'
_MIN_TURRET_OFFSET = 0.2
_WITHOUT_ZOOM = 1
_ZOOM_x2 = 2
_ZOOM_REDUCER = 1.8

def _calculateVehicleTurretOffset(vehicle):
    gunJoint = vehicle.model.node(TankNodeNames.GUN_JOINT)
    turretJoint = vehicle.model.node(TankNodeNames.TURRET_JOINT)
    _, hullTop, __ = vehicle.getBounds(TankPartIndexes.HULL)
    _, gunTop, __ = vehicle.getBounds(TankPartIndexes.GUN)
    _, turretTop, __ = vehicle.getBounds(TankPartIndexes.TURRET)
    turretY = turretJoint.localMatrix.translation.y if turretJoint else 0
    gunY = turretY + gunJoint.localMatrix.translation.y if gunJoint else 0
    return max(hullTop.y, gunTop.y + gunY, turretTop.y + turretY) + _MIN_TURRET_OFFSET


def _getZoomLevel(sessionProvider):
    inputHandler = avatar_getter.getInputHandler()
    if inputHandler is not None and inputHandler.ctrlModeName == CTRL_MODE_NAME.SNIPER:
        crosshairController = sessionProvider.shared.crosshair
        if crosshairController is not None:
            return crosshairController.getZoomFactor()
    return _WITHOUT_ZOOM


def _getReducedY(y, zoom, turretOffset):
    reducer = math.pow(_ZOOM_REDUCER, math.log(zoom, _ZOOM_x2))
    return turretOffset + (y - turretOffset) / reducer


class StoryModeMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'story_mode|storyModeBattleVehicleMarkersApp.swf'
    __slots__ = ()

    def _setupPlugins(self, arenaVisitor):
        setup = super(StoryModeMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = StoryModeVehicleMarkerPlugin
        if arenaVisitor.hasDestructibleEntities():
            setup['bunkers'] = BunkersPlugin
        return setup

    @property
    def _isMarkerHoveringEnabled(self):
        return False


class MarkerPluginWithOffsetInZoom(MarkerPlugin):
    __slots__ = ()

    def start(self):
        super(MarkerPluginWithOffsetInZoom, self).start()
        crosshairController = self.sessionProvider.shared.crosshair
        if crosshairController is not None:
            crosshairController.onCrosshairZoomFactorChanged += self._updateMatrixProviders
        aih_global_binding.subscribe(BINDING_ID.CTRL_MODE_NAME, self._updateMatrixProviders)
        return

    def stop(self):
        crosshairController = self.sessionProvider.shared.crosshair
        if crosshairController is not None:
            crosshairController.onCrosshairZoomFactorChanged -= self._updateMatrixProviders
        aih_global_binding.unsubscribe(BINDING_ID.CTRL_MODE_NAME, self._updateMatrixProviders)
        super(MarkerPluginWithOffsetInZoom, self).stop()
        return

    def _updateMatrixProviders(self, *args):
        pass


class StoryModeVehicleMarker(VehicleMarker):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _vehicleOffsetCache = {}

    @classmethod
    def _calculateGuiOffset(cls, vProxy):
        offset = super(StoryModeVehicleMarker, cls)._calculateGuiOffset(vProxy)
        zoom = _getZoomLevel(cls.sessionProvider)
        if zoom >= _ZOOM_x2:
            offset.y = _getReducedY(offset.y, zoom, cls._getVehicleTurretOffset(vProxy))
        return offset

    @classmethod
    def _getVehicleTurretOffset(cls, vProxy):
        if vProxy.id not in cls._vehicleOffsetCache:
            cls._vehicleOffsetCache[vProxy.id] = _calculateVehicleTurretOffset(vProxy)
        return cls._vehicleOffsetCache[vProxy.id]

    @classmethod
    def clearCache(cls):
        cls._vehicleOffsetCache.clear()


class StoryModeVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin, MarkerPluginWithOffsetInZoom):
    __slots__ = ()
    _voiceoverManager = dependency.descriptor(IVoiceoverManager)

    def __init__(self, parentObj, clazz=StoryModeVehicleMarker):
        super(StoryModeVehicleMarkerPlugin, self).__init__(parentObj, clazz)

    def start(self):
        super(StoryModeVehicleMarkerPlugin, self).start()
        self._voiceoverManager.onStarted += self._voiceoverHandler
        self._voiceoverManager.onStopped += self._voiceoverHandler
        if self._voiceoverManager.isPlaying:
            self._voiceoverHandler()

    def stop(self):
        self._voiceoverManager.onStarted -= self._voiceoverHandler
        self._voiceoverManager.onStopped -= self._voiceoverHandler
        StoryModeVehicleMarker.clearCache()
        super(StoryModeVehicleMarkerPlugin, self).stop()

    def _getHitState(self, eventID):
        return MARKER_EMPTY_HIT_STATE if eventID in _MARKER_CRITICAL_HIT_STATES else super(StoryModeVehicleMarkerPlugin, self)._getHitState(eventID)

    def _voiceoverHandler(self):
        ctx = self._voiceoverManager.currentCtx
        if ctx is None:
            return
        else:
            vehicleId = ctx.get('vehicleId', None)
            if not vehicleId:
                return
            if vehicleId not in self._markers:
                return
            marker = self._markers[vehicleId]
            markerId = marker.getMarkerID()
            flag = self._voiceoverManager.isPlaying
            if marker.setSpeaking(flag):
                self._invokeMarker(markerId, 'setSpeaking', flag)
            return

    def _updateMatrixProviders(self, *args):
        for marker in self._markers.values():
            if marker.isActive():
                self._setMarkerMatrix(marker.getMarkerID(), marker.getMatrixProvider())


class BunkersPlugin(MarkerPluginWithOffsetInZoom):
    __slots__ = ('_markers', '__clazz', '__entitiesDamageType', '_distanceUpdateCallback', '__offsetCache')
    _DISTANCE_UPDATE_TIME = 1

    def __init__(self, parentObj, clazz=BaseMarker):
        super(BunkersPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__clazz = clazz
        self.__entitiesDamageType = {}
        self._distanceUpdateCallback = None
        self.__offsetCache = {}
        return

    def start(self):
        super(BunkersPlugin, self).start()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityRemoved += self.__onDestructibleEntityRemoved
            destructibleComponent.onDestructibleEntityStateChanged += self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            entities = destructibleComponent.destructibleEntities
            for entity in entities.itervalues():
                self.__onDestructibleEntityAdded(entity)

        return

    def stop(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityRemoved -= self.__onDestructibleEntityRemoved
            destructibleComponent.onDestructibleEntityStateChanged -= self.__onDestructibleEntityStateChanged
            destructibleComponent.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        for marker in self._markers.itervalues():
            self._destroyMarker(marker.getMarkerID())

        self._markers.clear()
        self.__entitiesDamageType.clear()
        self.__offsetCache.clear()
        if self._distanceUpdateCallback is not None:
            BigWorld.cancelCallback(self._distanceUpdateCallback)
            self._distanceUpdateCallback = None
        super(BunkersPlugin, self).stop()
        return

    def _updateMatrixProviders(self, *args):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            return
        else:
            for entityId, marker in self._markers.iteritems():
                if marker.isActive():
                    self._setMarkerMatrix(marker.getMarkerID(), self.__getMarkerMatrix(destructibleComponent.getDestructibleEntity(entityId)))

            return

    def __onDestructibleEntityAdded(self, entity):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            _logger.error('Expected DestructibleEntityComponent not present!')
            return
        elif entity is None:
            _logger.error('Expected DestructibleEntity not present!')
            return
        else:
            handle = self._createMarkerWithMatrix(BUNKER_SYMBOL, self.__getMarkerMatrix(entity))
            if handle is None:
                return
            isDead = False
            if entity.health <= 0:
                isDead = True
            self._updateDistanceToEntity(handle, entity)
            if self._distanceUpdateCallback is None:
                self._distanceUpdateCallback = BigWorld.callback(self._DISTANCE_UPDATE_TIME, self._distanceUpdate)
            self._setMarkerActive(handle, entity.isActive)
            self._setMarkerRenderInfo(handle, _MEDIUM_MARKER_MIN_SCALE, _BUNKER_BOUNDS, _INNER_BUNKER_BOUNDS, _MAX_CULL_DISTANCE, _BUNKER_BOUNDS_MIN_SCALE)
            self._invokeMarker(handle, 'setDead', isDead)
            self._invokeMarker(handle, 'setName', backport.text(R.strings.sm_battle.bunker()))
            self._invokeMarker(handle, 'setMaxHealth', entity.maxHealth)
            self._invokeMarker(handle, 'setHealth', int(entity.health))
            marker = self.__clazz(handle, True, _BUNKER_OWNER)
            self._markers[entity.destructibleEntityID] = marker
            self._setMarkerSticky(handle, False)
            if isDead:
                self._setMarkerBoundEnabled(handle, False)
            return

    def __onDestructibleEntityRemoved(self, entityId):
        marker = self._markers.pop(entityId, None)
        if marker is not None:
            self._destroyMarker(marker.getMarkerID())
        return

    def __onDestructibleEntityStateChanged(self, entityId):
        marker = self._markers.get(entityId, None)
        if marker is not None:
            destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
            if destructibleComponent is None:
                _logger.error('Expected DestructibleEntityComponent not present!')
                return
            entity = destructibleComponent.getDestructibleEntity(entityId)
            if entity is None:
                _logger.error('Expected DestructibleEntity not present! Id: ' + str(entityId))
                return
            markerID = marker.getMarkerID()
            self._setMarkerMatrix(markerID, self.__getMarkerMatrix(entity))
            if not entity.isAlive():
                self._invokeMarker(markerID, 'setHealth', 0, self.__entitiesDamageType.get(entityId))
                self._invokeMarker(markerID, 'setDead', True)
                self._setMarkerBoundEnabled(markerID, False)
        return

    def __getMarkerMatrix(self, destructibleEntity):
        guiNode = destructibleEntity.getGuiNode()
        offset = Vector3(settings.MARKER_POSITION_ADJUSTMENT if guiNode is None else guiNode.localMatrix.translation)
        zoom = _getZoomLevel(self.sessionProvider)
        if zoom >= _ZOOM_x2:
            turretOffset = self.__getBunkerOffset(destructibleEntity)
            if turretOffset > 0:
                offset.y = _getReducedY(offset.y, zoom, turretOffset)
        m = Matrix()
        m.translation = destructibleEntity.position + offset
        return m

    def __getBunkerOffset(self, destructibleEntity):
        if destructibleEntity.id not in self.__offsetCache:
            topY, turretsSpotted = self.__calculateBunkerOffset(destructibleEntity)
            if not turretsSpotted:
                return topY
            self.__offsetCache[destructibleEntity.id] = topY
        return self.__offsetCache[destructibleEntity.id]

    @staticmethod
    def __calculateBunkerOffset(destructibleEntity):
        _, top, __ = destructibleEntity.getStateBounds(_BUNKER_ALIVE_STATE, 0)
        topY = top.y + _MIN_TURRET_OFFSET if top.y > 0 else 0
        vehOffsets = []
        bunkerQuery = CGF.Query(BigWorld.player().spaceID, (CGF.GameObject, BunkerLogicComponent))
        bunkerLogic = next((bunker for _, bunker in bunkerQuery if bunker.destructibleEntityId == destructibleEntity.destructibleEntityID), None)
        turretsSpotted = False
        if bunkerLogic:
            vehOffsets = list([ _calculateVehicleTurretOffset(v) + v.position.y - destructibleEntity.position.y for v in BigWorld.player().vehicles if v.id in bunkerLogic.vehicleIDs and v.isAlive ])
            turretsSpotted = len(bunkerLogic.vehicleIDs) == len(vehOffsets)
        return (max(topY, *vehOffsets) if vehOffsets else topY, turretsSpotted)

    def __onDestructibleEntityHealthChanged(self, entityId, newHealth, maxHealth, attackerID, attackReason, hitFlags):
        marker = self._markers.get(entityId, None)
        if marker is None:
            return
        else:
            hasImpactMask = True
            battleSpamCtrl = self.sessionProvider.shared.battleSpamCtrl
            aInfo = self.sessionProvider.getArenaDP().getVehicleInfo(attackerID)
            if battleSpamCtrl is not None and aInfo and aInfo.isAutoShootGunVehicle():
                hasImpactMask = battleSpamCtrl.filterMarkersHitState(entityId, 'impact{}'.format(attackerID))
            self.__entitiesDamageType[entityId] = self.__getVehicleDamageType(aInfo)
            self._invokeMarker(marker.getMarkerID(), 'setHealth', newHealth, self.__entitiesDamageType[entityId], hasImpactMask)
            return

    def _updateDistanceToEntity(self, entityId, entity):
        if entity.isActive:
            bunkerQuery = CGF.Query(BigWorld.player().spaceID, (CGF.GameObject, BunkerLogicComponent))
            bunkerLogic = next((bunker for _, bunker in bunkerQuery if bunker.destructibleEntityId == entity.destructibleEntityID), None)
            if bunkerLogic:
                distance = (entity.position - avatar_getter.getOwnVehiclePosition()).length
                self._setMarkerActive(entityId, distance < bunkerLogic.markerDistance)
        else:
            self._setMarkerActive(entityId, False)
        return

    def _distanceUpdate(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            self._distanceUpdateCallback = None
            return
        else:
            for entityId in destructibleComponent.destructibleEntities:
                entity = destructibleComponent.getDestructibleEntity(entityId)
                if entity is None:
                    continue
                marker = self._markers.get(entityId, None)
                if marker:
                    self._updateDistanceToEntity(marker.getMarkerID(), entity)

            self._distanceUpdateCallback = BigWorld.callback(self._DISTANCE_UPDATE_TIME, self._distanceUpdate)
            return

    def __getVehicleDamageType(self, attackerInfo):
        if not attackerInfo:
            return settings.DamageType.FROM_OTHER
        attackerID = attackerInfo.vehicleID
        if attackerID == BigWorld.player().playerVehicleID:
            return settings.DamageType.FROM_PLAYER
        entityName = self.sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        return settings.DamageType.FROM_SQUAD if entityName == PLAYER_GUI_PROPS.squadman else settings.DamageType.FROM_OTHER
