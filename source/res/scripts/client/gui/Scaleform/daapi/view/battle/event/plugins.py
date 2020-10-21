# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import BigWorld
import Math
from gui.impl import backport
from gui.impl.gen import R
from game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.battle.event.markers import EventBaseMarker, EventVehicleMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings, plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
from helpers import isPlayerAvatar
from gui.Scaleform.daapi.view.battle.event.components import EventGoalUpdateComponent, EventECPUpdateComponent
from constants import AOI
from arena_components.advanced_chat_component import TARGET_CHAT_CMD_FLAG
_STUN_EFFECT_DURATION = 1000
_STUN_STATE = 0
_DESTROYED_PREFIX = 'Destroyed'
_SHOW_ENEMY_ROLE_MARKER = 'showEnemyRoleMarker'
_STATIC_MARKER_CULL_DISTANCE = 2000
_CAMP_MARKER_MIN_SCALE = 100
_COLLECTOR_MARKER_MIN_SCALE = 0
_COLLECTOR_MARKER_BOUNDS = Math.Vector4(36, 36, 36, 36)
_CAMP_MARKER_BOUNDS = Math.Vector4(10, 10, 20, 10)
_INNER_BASE_MARKER_BOUNDS = Math.Vector4(17, 17, 18, 18)
_BASE_MARKER_BOUND_MIN_SCALE = Math.Vector2(1.0, 1.0)
_CAMP_MARKER_RADIUS_SCALE = 0.54

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
                if player.isBoss(vehicleID):
                    self._invokeMarker(markerID, 'setBossMode')
            else:
                self._setMarkerActive(markerID, False)

    def __showEnemiesRoleMarkers(self):
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.__showEnemyRoleMarker(vInfo, isDead=not vInfo.isAlive)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self._markers:
            if eventID == _EVENT_ID.VEHICLE_SHOW_MESSAGE:
                handle = self._markers[vehicleID].getMarkerID()
                self.__showActionMassage(handle, *value)
            elif eventID == _EVENT_ID.VEHICLE_DEAD:
                arenaDP = self.sessionProvider.getArenaDP()
                vInfo = arenaDP.getVehicleInfo(vehicleID)
                self.__showEnemyRoleMarker(vInfo, isDead=True)
                self.__removeBotRole(vehicleID)

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


class EventCampsOrControlsPointsPlugin(plugins.TeamsOrControlsPointsPlugin, EventGoalUpdateComponent, EventECPUpdateComponent):

    def __init__(self, parentObj):
        super(EventCampsOrControlsPointsPlugin, self).__init__(parentObj, EventBaseMarker)

    def start(self):
        super(EventCampsOrControlsPointsPlugin, self).start()
        EventECPUpdateComponent.start(self)
        EventGoalUpdateComponent.start(self)

    def stop(self):
        EventGoalUpdateComponent.stop(self)
        EventECPUpdateComponent.stop(self)
        super(EventCampsOrControlsPointsPlugin, self).stop()

    def _restart(self):
        self._personalTeam = self.sessionProvider.getArenaDP().getNumberOfTeam()
        EventECPUpdateComponent._restart(self)
        EventGoalUpdateComponent._restart(self)

    def _setMarkerRepliesAndCheckState(self, marker, count, isTargetForPlayer, checkState=True):
        oldReplyCount = marker.getReplyCount()
        if isTargetForPlayer:
            if marker.getIsRepliedByPlayer():
                isRepliedByPlayer = count >= oldReplyCount
            else:
                isRepliedByPlayer = count > oldReplyCount
            marker.setIsRepliedByPlayer(isRepliedByPlayer)
        if oldReplyCount != count and (oldReplyCount == 0 or count == 0):
            self._setMarkerReplied(marker, count > 0)
        self._setMarkerReplyCount(marker, count)
        if checkState:
            self._checkNextState(marker)

    def _addCampOrControlPointMarker(self, symbol, position, ecpID):
        minimapSymbol = EventBaseMarker.MARKER_SYMBOLS[symbol]
        player = BigWorld.player()
        position = self._getTerrainHeightAt(player.spaceID, position[0], position[2]) + settings.MARKER_POSITION_ADJUSTMENT
        distance = (position - player.getOwnVehiclePosition()).length
        if EventBaseMarker.MARKER_OWNERS[minimapSymbol] == 'ally':
            markerID = self.__setupSoulsCollectorMarker(minimapSymbol, position, distance)
        else:
            markerID = self.__setupCampMarker(minimapSymbol, position, distance)
        if markerID < 0:
            return
        marker = self._clazz(markerID, True, EventBaseMarker.MARKER_OWNERS[minimapSymbol])
        marker.setSymbol(minimapSymbol)
        marker.setPosition(position)
        self._markers[ecpID] = marker
        marker.setState(plugins.ReplyStateForMarker.NO_ACTION)
        self._setActiveState(marker, marker.getState())

    def _setMarkerSticky(self, markerID, isSticky):
        if markerID == self._getCollectorMarkerID():
            return
        super(EventCampsOrControlsPointsPlugin, self)._setMarkerSticky(markerID, isSticky)

    def __setupSoulsCollectorMarker(self, symbol, position, distance):
        markerID = self._createMarkerWithPosition(symbol, position, active=True)
        if markerID < 0:
            return markerID
        self._setMarkerRenderInfo(markerID, _COLLECTOR_MARKER_MIN_SCALE, _COLLECTOR_MARKER_BOUNDS, _INNER_BASE_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _BASE_MARKER_BOUND_MIN_SCALE)
        super(EventCampsOrControlsPointsPlugin, self)._setMarkerSticky(markerID, True)
        self._setMarkerActive(markerID, False)
        self._invokeMarker(markerID, 'setLocales', backport.text(R.strings.ingame_gui.marker.meters()))
        self._invokeMarker(markerID, 'setDistance', distance)
        self._invokeMarker(markerID, 'setIconActive', True)
        self._setMarkerBoundEnabled(markerID, True)
        return markerID

    def __setupCampMarker(self, symbol, position, distance):
        markerID = self._createMarkerWithPosition(symbol, position, active=True)
        if markerID < 0:
            return markerID
        self._setMarkerRenderInfo(markerID, _CAMP_MARKER_MIN_SCALE, _CAMP_MARKER_BOUNDS, _INNER_BASE_MARKER_BOUNDS, _STATIC_MARKER_CULL_DISTANCE, _BASE_MARKER_BOUND_MIN_SCALE)
        self._setMarkerSticky(markerID, False)
        self._markerSetCustomStickyRadiusScale(markerID, _CAMP_MARKER_RADIUS_SCALE)
        self._setMarkerActive(markerID, distance <= AOI.VEHICLE_CIRCULAR_AOI_RADIUS)
        self._invokeMarker(markerID, 'init', EventBaseMarker.CAMP_SHAPE, 0, _STATIC_MARKER_CULL_DISTANCE, distance, backport.text(R.strings.ingame_gui.marker.meters()), EventBaseMarker.CAMP_COLOR)
        self._setMarkerBoundEnabled(markerID, True)
        return markerID
