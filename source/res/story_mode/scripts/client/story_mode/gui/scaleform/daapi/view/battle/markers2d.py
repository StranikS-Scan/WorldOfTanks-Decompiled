# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/markers2d.py
from logging import getLogger
import BigWorld
import CGF
from BunkerLogicComponent import BunkerLogicComponent
from Math import Vector4, Vector2, Matrix
from constants import VEHICLE_HIT_FLAGS
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager, settings
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import MarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, PLAYER_GUI_PROPS
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from story_mode.skeletons.voiceover_controller import IVoiceoverManager
from story_mode_common.story_mode_constants import LOGGER_NAME
_MARKER_CRITICAL_HIT_STATES = {FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_DAMAGE,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED}
_logger = getLogger(LOGGER_NAME)
_MEDIUM_MARKER_MIN_SCALE = 100
_MAX_CULL_DISTANCE = 1000000.0
_BUNKER_BOUNDS_MIN_SCALE = Vector2(1.0, 0.8)
_BUNKER_BOUNDS = Vector4(50, 50, 30, 65)
_INNER_BUNKER_BOUNDS = Vector4(17, 17, 18, 25)
_BUNKER_OWNER = 'enemy'
BUNKER_SYMBOL = 'BunkerMarkerUI'

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


class StoryModeVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    __slots__ = ()
    _voiceoverManager = dependency.descriptor(IVoiceoverManager)

    def start(self):
        super(StoryModeVehicleMarkerPlugin, self).start()
        self._hiddenEvents = _MARKER_CRITICAL_HIT_STATES
        self._voiceoverManager.onStarted += self._voiceoverHandler
        self._voiceoverManager.onStopped += self._voiceoverHandler
        if self._voiceoverManager.isPlaying:
            self._voiceoverHandler()

    def stop(self):
        self._voiceoverManager.onStarted -= self._voiceoverHandler
        self._voiceoverManager.onStopped -= self._voiceoverHandler
        super(StoryModeVehicleMarkerPlugin, self).stop()

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


class BunkersPlugin(MarkerPlugin):
    __slots__ = ('_markers', '__clazz', '__entitiesDamageType', '_distanceUpdateCallback')
    _DISTANCE_UPDATE_TIME = 1

    def __init__(self, parentObj, clazz=BaseMarker):
        super(BunkersPlugin, self).__init__(parentObj)
        self._markers = {}
        self.__clazz = clazz
        self.__entitiesDamageType = {}
        self._distanceUpdateCallback = None
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
        if self._distanceUpdateCallback is not None:
            BigWorld.cancelCallback(self._distanceUpdateCallback)
            self._distanceUpdateCallback = None
        super(BunkersPlugin, self).stop()
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
        if guiNode is not None:
            return guiNode
        else:
            m = Matrix()
            m.translation = destructibleEntity.position + settings.MARKER_POSITION_ADJUSTMENT
            return m

    def __onDestructibleEntityHealthChanged(self, entityId, newHealth, maxHealth, attackerID, attackReason, hitFlags):
        marker = self._markers.get(entityId, None)
        if marker is None:
            return
        else:
            aInfo = self.sessionProvider.getArenaDP().getVehicleInfo(attackerID)
            self.__entitiesDamageType[entityId] = self.__getVehicleDamageType(aInfo)
            self._invokeMarker(marker.getMarkerID(), 'setHealth', newHealth, self.__entitiesDamageType[entityId], hitFlags & VEHICLE_HIT_FLAGS.IS_ANY_PIERCING_MASK)
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
            return settings.DAMAGE_TYPE.FROM_UNKNOWN
        attackerID = attackerInfo.vehicleID
        if attackerID == BigWorld.player().playerVehicleID:
            return settings.DAMAGE_TYPE.FROM_PLAYER
        entityName = self.sessionProvider.getCtx().getPlayerGuiProps(attackerID, attackerInfo.team)
        if entityName == PLAYER_GUI_PROPS.squadman:
            return settings.DAMAGE_TYPE.FROM_SQUAD
        if entityName == PLAYER_GUI_PROPS.ally:
            return settings.DAMAGE_TYPE.FROM_ALLY
        return settings.DAMAGE_TYPE.FROM_ENEMY if entityName == PLAYER_GUI_PROPS.enemy else settings.DAMAGE_TYPE.FROM_UNKNOWN
