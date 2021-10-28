# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import logging
import BigWorld
import Math
from Avatar import enableIfAvatarHasComponent
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EquipmentsMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import ReplyStateForMarker
from gui.impl import backport
from gui.impl.gen import R
from game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.battle.event.markers import EventBaseMarker, EventVehicleMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from helpers import isPlayerAvatar
from gui.Scaleform.daapi.view.battle.event.components import EventChatCommunicationComponent, EventGoalUpdateComponent, EventECPUpdateComponent
from constants import AOI, EventStorageModifiers
from arena_components.advanced_chat_component import TARGET_CHAT_CMD_FLAG
from chat_commands_consts import INVALID_MARKER_SUBTYPE, INVALID_MARKER_ID, MarkerType, DefaultMarkerSubType
from gui.battle_control.avatar_getter import isVehicleAlive
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from constants import CollisionFlags
_STUN_EFFECT_DURATION = 1000
_STUN_STATE = 0
_DESTROYED_PREFIX = 'Destroyed'
_SHOW_ENEMY_ROLE_MARKER = 'showEnemyRoleMarker'
_STATIC_MARKER_CULL_DISTANCE = 2000
_MAP_MAX_HEIGHT = 1000.0
_CAMP_MARKER_MIN_SCALE = 100
_COLLECTOR_MARKER_MIN_SCALE = 0
_COLLECTOR_MARKER_BOUNDS = Math.Vector4(36, 36, 36, 36)
_CAMP_MARKER_BOUNDS = Math.Vector4(10, 10, 20, 10)
_INNER_BASE_MARKER_BOUNDS = Math.Vector4(17, 17, 18, 18)
_BASE_MARKER_BOUND_MIN_SCALE = Math.Vector2(1.0, 1.0)
_CAMP_MARKER_RADIUS_SCALE = 0.54
logger = logging.getLogger(__name__)

def getArenaInfoBossHealthBarComponent():
    arenaInfo = BigWorld.player().arena.arenaInfo
    return getattr(arenaInfo, 'hwBossHealthBarComponent', None)


def getVehicleMarkerHealth(vehicleID, health):
    component = getArenaInfoBossHealthBarComponent()
    if not component:
        return health
    if vehicleID != component.bossId:
        return health
    currentHealth, _ = component.getVehicleMarkerHealthValues(health)
    return currentHealth


class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin, GameEventGetterMixin):

    def __init__(self, parentObj, clazz=EventVehicleMarker):
        super(EventVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        GameEventGetterMixin.__init__(self)

    def init(self, *args):
        super(EventVehicleMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        if isPlayerAvatar():
            player = BigWorld.player()
            hwDataStorage = getattr(player, 'hwGameplayDataStorage', None)
            if hwDataStorage is not None:
                hwDataStorage.onStorageDataAdded += self.__onAddedMarkerBuffComponent
            player.onBotRolesReceived += self.__showEnemiesRoleMarkers
            player.onAuraVictimMarkerIcon += self.__showAuraVictimMarkerIcon
        if self.souls is not None:
            self.souls.onSoulsChanged += self.__onSoulsChanged
        self.__showEnemiesRoleMarkers()
        return

    def fini(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if isPlayerAvatar():
            player = BigWorld.player()
            hwDataStorage = getattr(player, 'hwGameplayDataStorage', None)
            if hwDataStorage is not None:
                hwDataStorage.onStorageDataAdded -= self.__onAddedMarkerBuffComponent
            player.onBotRolesReceived -= self.__showEnemiesRoleMarkers
            player.onAuraVictimMarkerIcon -= self.__showAuraVictimMarkerIcon
        if self.souls is not None:
            self.souls.onSoulsChanged -= self.__onSoulsChanged
        super(EventVehicleMarkerPlugin, self).fini()
        return

    def _getMarkerSymbol(self, _):
        return settings.MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _setMarkerInitialState(self, marker, accountDBID=0):
        super(EventVehicleMarkerPlugin, self)._setMarkerInitialState(marker, accountDBID)
        if marker.isActive():
            vehicleID = marker.getVehicleID()
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.__showEnemyRoleMarker(vInfo, isDead=not vInfo.isAlive)
            self.__updateSouls(vInfo)

    def _onChatCommandTargetUpdate(self, isStatic, chatCommandStates):
        for vehicleID, state in chatCommandStates.iteritems():
            chatCommandName, chatCommandFlags = state
            if vehicleID in self._markers and chatCommandFlags & TARGET_CHAT_CMD_FLAG == 0:
                self._invokeMarker(self._markers[vehicleID].getMarkerID(), 'changeObjectiveActionMarker', self._markers[vehicleID].getOverride(chatCommandName))

    def _setHealthMarker(self, vehicleID, handle, newHealth):
        super(EventVehicleMarkerPlugin, self)._setHealthMarker(vehicleID, handle, newHealth)
        self.__updateBossMarkerHealth(vehicleID, handle, newHealth)

    def _updateHealthMarker(self, vehicleID, handle, newHealth, *args):
        newHealth = getVehicleMarkerHealth(vehicleID, newHealth)
        super(EventVehicleMarkerPlugin, self)._updateHealthMarker(vehicleID, handle, newHealth, *args)

    def _setVehicleInfoMarker(self, vehicleID, handle, *args):
        super(EventVehicleMarkerPlugin, self)._setVehicleInfoMarker(vehicleID, handle, *args)
        self.__updateBossMarkerHealth(vehicleID, handle)

    def __showEnemyRoleMarker(self, vInfo, isDead=False):
        vehicleID = vInfo.vehicleID
        player = BigWorld.player()
        botRole = player.getBotRole(vehicleID)
        isEnemy = vInfo.team != player.team
        if vehicleID in self._markers and isEnemy:
            markerID = self._markers[vehicleID].getMarkerID()
            if botRole:
                self._setMarkerActive(markerID, True)
                if isDead:
                    botRole += _DESTROYED_PREFIX
                self._invokeMarker(markerID, _SHOW_ENEMY_ROLE_MARKER, botRole)
                self.__updateMarkerBuff(vehicleID, markerID)
            else:
                self._setMarkerActive(markerID, False)

    def __showEnemiesRoleMarkers(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.__showEnemyRoleMarker(vInfo, isDead=not vInfo.isAlive)

    def __updateBossMarkerHealth(self, vehicleID, handle, health=None):
        component = getArenaInfoBossHealthBarComponent()
        if not component or not component.isActive or vehicleID != component.bossId:
            return
        else:
            if health is None:
                bossVehicle = BigWorld.entities.get(vehicleID)
                if not bossVehicle:
                    return
                health = bossVehicle.health
            currentHealth, maxHealth = component.getVehicleMarkerHealthValues(health)
            self._invokeMarker(handle, 'setMaxHealth', maxHealth)
            self._invokeMarker(handle, 'setHealth', currentHealth)
            return

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self._markers:
            if eventID == FEEDBACK_EVENT_ID.VEHICLE_SHOW_MESSAGE:
                handle = self._markers[vehicleID].getMarkerID()
                self.__showActionMassage(handle, *value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
                arenaDP = self.sessionProvider.getArenaDP()
                vInfo = arenaDP.getVehicleInfo(vehicleID)
                self.__showEnemyRoleMarker(vInfo, isDead=True)
                self.__removeBotRole(vehicleID)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_MARKER_HEALTH:
                self.__updateBossMarkerHealth(vehicleID, self._markers[vehicleID].getMarkerID(), value)

    def __removeBotRole(self, vehicleID):
        player = BigWorld.player()
        if player:
            player.removeBotRole(vehicleID)

    def __showActionMassage(self, handle, massage, isAlly):
        self._invokeMarker(handle, 'showActionMessage', massage, isAlly)

    def __showAuraVictimMarkerIcon(self, show, vehicleId):
        if vehicleId in self._markers:
            animated = True
            isSourceVehicle = True
            handle = self._markers[vehicleId].getMarkerID()
            self._updateStatusMarkerState(vehicleId, show, handle, _STUN_STATE, _STUN_EFFECT_DURATION, animated, isSourceVehicle)

    def __onSoulsChanged(self, diff):
        for vehID, (souls, _) in diff.iteritems():
            if vehID not in self._markers:
                continue
            handle = self._markers[vehID].getMarkerID()
            self._invokeMarker(handle, 'showSoulMark', souls)

    def __updateSouls(self, vInfo):
        if not self.souls:
            return
        player = BigWorld.player()
        vehID = vInfo.vehicleID
        if vInfo.team != player.team or vehID not in self._markers:
            return
        handle = self._markers[vehID].getMarkerID()
        self._invokeMarker(handle, 'showSoulMark', self.souls.getSouls(vehID))

    def __updateMarker(self, markerID, data):
        logger.debug('Update marker: markerID=%s, method=%s, args=%s', markerID, data['method'], data.get('args', []))
        self._invokeMarker(markerID, data['method'], *data.get('args', []))

    @enableIfAvatarHasComponent('hwGameplayDataStorage')
    def __updateMarkerBuff(self, vehicleID, markerID):
        invokeParams = BigWorld.player().hwGameplayDataStorage.getAllVehicleData(EventStorageModifiers.MARKER.value, vehicleID)
        for data in invokeParams:
            self.__updateMarker(markerID, data)

    def __onAddedMarkerBuffComponent(self, storageKey, vehicleID, data):
        if storageKey == EventStorageModifiers.MARKER.value:
            self.__updateMarker(self._markers[vehicleID].getMarkerID(), data)


class EventCampsOrControlsPointsPlugin(plugins.MarkerPlugin, EventChatCommunicationComponent, EventGoalUpdateComponent, EventECPUpdateComponent):
    __slots__ = ('_clazz', '_markers')

    def __init__(self, parentObj, clazz=EventBaseMarker):
        super(EventCampsOrControlsPointsPlugin, self).__init__(parentObj)
        EventGoalUpdateComponent.__init__(self, parentObj)
        self._clazz = clazz
        self._markers = dict()

    def start(self):
        super(EventCampsOrControlsPointsPlugin, self).start()
        EventECPUpdateComponent.start(self)
        EventGoalUpdateComponent.start(self)
        EventChatCommunicationComponent.start(self)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def stop(self):
        self._clearMarkers()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        EventECPUpdateComponent.stop(self)
        EventGoalUpdateComponent.stop(self)
        EventChatCommunicationComponent.stop(self)
        super(EventCampsOrControlsPointsPlugin, self).stop()
        return

    def getMarker(self, markerID, markerType, defaultMarker=None):
        return self._markers.get(markerID, defaultMarker) if markerType == self.getMarkerType() else defaultMarker

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def getTargetIDFromMarkerID(self, markerID):
        for baseID, marker in self._markers.iteritems():
            if markerID == marker.getMarkerID():
                return baseID

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        foundMarker = self._markers.get(targetID, None)
        if foundMarker is None:
            return INVALID_MARKER_SUBTYPE
        else:
            return DefaultMarkerSubType.ALLY_MARKER_SUBTYPE if foundMarker.getSymbol() == settings.MARKER_SYMBOL_NAME.EVENT_VOLOT_MARKER else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers or markerType != self.getMarkerType() else self._markers[targetID]

    def _onEnvironmentEventIDUpdate(self, eventEnvID):
        self._clearMarkers()
        EventECPUpdateComponent._onEnvironmentEventIDUpdate(self, eventEnvID)
        EventGoalUpdateComponent._onEnvironmentEventIDUpdate(self, eventEnvID)
        EventChatCommunicationComponent._onEnvironmentEventIDUpdate(self, eventEnvID)

    @staticmethod
    def _getTerrainHeightAt(spaceID, x, z):
        collisionWithTerrain = BigWorld.wg_collideSegment(spaceID, Math.Vector3(x, _MAP_MAX_HEIGHT, z), Math.Vector3(x, -_MAP_MAX_HEIGHT, z), CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE)
        return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)

    def _addMarker(self, symbol, position, ecpID):
        player = BigWorld.player()
        if player is None:
            return
        else:
            position = self._getTerrainHeightAt(player.spaceID, position[0], position[2]) + settings.MARKER_POSITION_ADJUSTMENT
            distance = (position - player.getOwnVehiclePosition()).length
            markerSymbol = EventBaseMarker.MARKER_SYMBOLS.get(symbol)
            if markerSymbol is not None:
                markerID = self.__setupSoulsCollectorMarker(markerSymbol, position, distance) if markerSymbol == settings.MARKER_SYMBOL_NAME.EVENT_VOLOT_MARKER else self.__setupCampMarker(markerSymbol, position, distance)
                if markerID != INVALID_MARKER_ID:
                    marker = self._clazz(markerID, active=True, symbol=markerSymbol, position=position)
                    marker.setState(plugins.ReplyStateForMarker.NO_ACTION)
                    self._setActiveState(marker, marker.getState())
                    self._markers[ecpID] = marker
                    if marker.isVolot():
                        self._onCollectorIDChanged()
            return

    def _removeMarker(self, ecpID):
        marker = self._markers.get(ecpID)
        if marker is not None:
            advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            if advChatCmp is not None:
                chatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(ecpID, self.getMarkerType())
                commands = self.sessionProvider.shared.chatCommands
                if chatCmdData is not None and commands is not None:
                    commands.sendCancelReplyChatCommand(ecpID, _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).name)
            self._destroyMarker(marker.getMarkerID())
            del self._markers[ecpID]
        return

    def _clearMarkers(self):
        for marker in self._markers.itervalues():
            self._destroyMarker(marker.getMarkerID())

        self._markers.clear()

    def _setMarkerSticky(self, markerID, isSticky):
        if markerID != self._getCollectorMarkerID():
            super(EventCampsOrControlsPointsPlugin, self)._setMarkerSticky(markerID, isSticky)

    def __setupSoulsCollectorMarker(self, symbol, position, distance):
        markerID = self._createMarkerWithPosition(symbol, position, active=True)
        if markerID < 0:
            return INVALID_MARKER_ID
        self._setMarkerRenderInfo(markerID, _COLLECTOR_MARKER_MIN_SCALE, _COLLECTOR_MARKER_BOUNDS, _INNER_BASE_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _BASE_MARKER_BOUND_MIN_SCALE)
        plugins.MarkerPlugin._setMarkerSticky(self, markerID, True)
        self._setMarkerActive(markerID, False)
        self._invokeMarker(markerID, 'setLocales', backport.text(R.strings.ingame_gui.marker.meters()))
        self._invokeMarker(markerID, 'setDistance', distance)
        self._invokeMarker(markerID, 'setIconActive', True)
        self._setMarkerBoundEnabled(markerID, True)
        return markerID

    def _invokeMarker(self, markerID, function, *args):
        if function not in self._clazz.UNSUPPORTED_INVOKE_FN:
            plugins.MarkerPlugin._invokeMarker(self, markerID, function, *args)

    def __setupCampMarker(self, symbol, position, distance):
        markerID = self._createMarkerWithPosition(symbol, position, active=True)
        if markerID < 0:
            return INVALID_MARKER_ID
        self._setMarkerRenderInfo(markerID, _CAMP_MARKER_MIN_SCALE, _CAMP_MARKER_BOUNDS, _INNER_BASE_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _BASE_MARKER_BOUND_MIN_SCALE)
        self._setMarkerSticky(markerID, False)
        self._markerSetCustomStickyRadiusScale(markerID, _CAMP_MARKER_RADIUS_SCALE)
        self._setMarkerActive(markerID, distance <= AOI.VEHICLE_CIRCULAR_AOI_RADIUS)
        self._invokeMarker(markerID, 'init', EventBaseMarker.CAMP_SHAPE, 0, _STATIC_MARKER_CULL_DISTANCE, distance, backport.text(R.strings.ingame_gui.marker.meters()), EventBaseMarker.CAMP_COLOR)
        self._setMarkerBoundEnabled(markerID, True)
        return markerID

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            for marker in self._markers.values():
                if marker.getState() != ReplyStateForMarker.NO_ACTION:
                    marker.setBoundCheckEnabled(False)
                    self._setMarkerBoundEnabled(marker.getMarkerID(), False)

        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.RESPAWNING):
            if not self.sessionProvider.getCtx().isPlayerObserver() and isVehicleAlive():
                for marker in self._markers.values():
                    if not marker.getBoundCheckEnabled():
                        marker.setBoundCheckEnabled(True)
                        self._setMarkerBoundEnabled(marker.getMarkerID(), True)


class EventEquipmentsMarkerPlugin(EquipmentsMarkerPlugin):

    def _getSymbolName(self):
        return settings.MARKER_SYMBOL_NAME.EVENT_DEATH_ZONE_MARKER
