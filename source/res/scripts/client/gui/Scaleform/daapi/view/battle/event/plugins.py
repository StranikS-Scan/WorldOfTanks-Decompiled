# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/plugins.py
import BigWorld
from constants import WT_TAGS
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EventBusPlugin, AreaMarkerPlugin, ChatCommunicationComponent
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker, ReplyStateForMarker
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions, EventKeys
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from chat_commands_consts import INVALID_MARKER_SUBTYPE, INVALID_MARKER_ID, MarkerType, DefaultMarkerSubType
from messenger.proto.bw_chat2.battle_chat_cmd import AUTOCOMMIT_COMMAND_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.wt_event.wt_event_helpers import isBossTeam

class EventVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def start(self):
        super(EventVehicleMarkerPlugin, self).start()
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def stop(self):
        super(EventVehicleMarkerPlugin, self).stop()
        vehicleStateCtrl = self.sessionProvider.shared.vehicleState
        if vehicleStateCtrl is not None:
            vehicleStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        return

    def _getMarkerSymbol(self, vehicleID):
        return MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.WT_INSPIRE:
            vehicleID = value[0]
            inspireVisible = value[1]
            if vehicleID not in self._markers:
                return
            markerID = self._markers[vehicleID].getMarkerID()
            self._invokeMarker(markerID, 'showInspireAura', inspireVisible)

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(EventVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if vehicleID not in self._markers:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_SHOW_MESSAGE:
            self._showActionMessage(markerID, *value)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self._invokeMarker(markerID, 'setPlasmaBuffValue', 0)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DISCRETE_DAMAGE_RECEIVED:
            attackerID, plasmaDamage = value
            plasmaDamage = round(plasmaDamage)
            arenaDP = self.sessionProvider.getArenaDP()
            isAlly = arenaDP.isAlly(vehicleID)
            if avatar_getter.getPlayerVehicleID() == attackerID and plasmaDamage > 0 and not isAlly:
                self._invokeMarker(markerID, 'showPlasmaDamage', plasmaDamage)

    def _showActionMessage(self, markerID, message, isAlly):
        self._invokeMarker(markerID, 'showActionMessage', message, isAlly)

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        vehId = vInfo.vehicleID
        if avatar_getter.isVehiclesColorized():
            guiPropsName = 'team{}'.format(vInfo.team)
        else:
            if avatar_getter.isObserver():
                arenaDP = self.sessionProvider.getArenaDP()
                obsVehId = BigWorld.player().observedVehicleID
                if vehId == obsVehId or arenaDP.isSquadMan(vehId, arenaDP.getVehicleInfo(obsVehId).prebattleID):
                    guiProps = PLAYER_GUI_PROPS.squadman
            guiPropsName = guiProps.name()
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        classTag = vType.classTag
        if WT_TAGS.BOSS in vType.tags:
            classTag = 'wtboss'
        if WT_TAGS.MINIBOSS in vType.tags:
            classTag = 'miniboss'
        canShowPlasma = not isBossTeam(vInfo.team)
        self._invokeMarker(markerID, 'showPlasmaBuff', canShowPlasma)
        if canShowPlasma:
            plasmaBuffValue = vInfo.gameModeSpecific.getValue(EventKeys.PLASMA_COUNT.value)
            if plasmaBuffValue is not None:
                self._invokeMarker(markerID, 'setPlasmaBuffValue', plasmaBuffValue)
        self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')
        return


class EventEventBusPlugin(EventBusPlugin):

    def start(self):
        super(EventEventBusPlugin, self).start()
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onShowSpawnPoints += self._onShowSpawnPoints
            teleport.onCloseSpawnPoints += self._onCloseSpawnPoints
        return

    def stop(self):
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onShowSpawnPoints -= self._onShowSpawnPoints
            teleport.onCloseSpawnPoints -= self._onCloseSpawnPoints
        super(EventEventBusPlugin, self).stop()
        return

    def _onShowSpawnPoints(self, *_):
        self._parentObj.setVisible(False)

    def _onCloseSpawnPoints(self, *_):
        self._parentObj.setVisible(True)


class EventBaseAreaMarkerPlugin(AreaMarkerPlugin, ChatCommunicationComponent):
    __slots__ = ('__markers', '__entityMap', '__clazz')

    def __init__(self, parentObj, clazz=BaseMarker):
        super(EventBaseAreaMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__clazz = clazz
        self.__entityMap = {}
        ChatCommunicationComponent.__init__(self, parentObj)

    def start(self):
        super(EventBaseAreaMarkerPlugin, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
        ChatCommunicationComponent.start(self)
        return

    def stop(self):
        self.__markers = {}
        ChatCommunicationComponent.stop(self)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
        super(EventBaseAreaMarkerPlugin, self).stop()
        return

    def createMarker(self, uniqueID, targetID, symbol, matrixProvider, active, bcMarkerType, guiMarkerType):
        if uniqueID in self.__markers:
            return False
        markerID = self._createMarkerWithMatrix(symbol, matrixProvider, active=active)
        marker = self.__clazz(markerID, True)
        self.__markers[uniqueID] = marker
        marker.setState(ReplyStateForMarker.NO_ACTION)
        self._setActiveState(marker, marker.getState())
        return True

    def mapCustomEntityID(self, componentID, generatorIndex):
        self.__entityMap[componentID] = generatorIndex
        self.__addActiveCommandsOnMarker(generatorIndex)

    def deleteCustomEntityID(self, generatorIndex):
        if generatorIndex in self.__entityMap:
            self.__entityMap.pop(generatorIndex)

    def resetMarkerReplyCnt(self, generatorIndex):
        if generatorIndex in self.__entityMap:
            self.__removeCommandReceived(generatorIndex)

    def deleteMarker(self, uniqueID):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is not None:
            self._destroyMarker(markerID.getMarkerID())
            return True
        else:
            return False

    def setupMarker(self, uniqueID, shape, minDistance, maxDistance, distance, metersString, distanceFieldColor):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID].getMarkerID(), 'init', shape, minDistance, maxDistance, distance, metersString, distanceFieldColor)

    def markerSetDistance(self, uniqueID, distance):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID].getMarkerID(), 'setDistance', distance)

    def setMarkerMatrix(self, uniqueID, matrix):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is None:
            return
        else:
            self._parentObj.setMarkerMatrix(markerID, matrix)
            return

    def setMarkerActive(self, uniqueID, active):
        marker = self.__markers.get(uniqueID)
        if marker:
            self._setMarkerActive(marker.getMarkerID(), active)
            marker.setActive(active)

    def invokeMarker(self, uniqueID, name, *args):
        if uniqueID in self.__markers:
            self._setActiveState(self.__markers[uniqueID], ReplyStateForMarker.CREATE_STATE)
            self._invokeMarker(self.__markers[uniqueID].getMarkerID(), name, *args)

    def setMarkerRenderInfo(self, uniqueID, minScale, offset, innerOffset, cullDistance, boundsMinScale):
        if uniqueID in self.__markers:
            self._setMarkerRenderInfo(self.__markers[uniqueID].getMarkerID(), minScale, offset, innerOffset, cullDistance, boundsMinScale)

    def setMarkerSticky(self, uniqueID, isSticky):
        if uniqueID in self.__markers:
            self._setMarkerSticky(self.__markers[uniqueID].getMarkerID(), isSticky)

    def setMarkerLocationOffset(self, uniqueID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
        if uniqueID in self.__markers:
            self._setMarkerLocationOffset(self.__markers[uniqueID].getMarkerID(), minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)

    def setMarkerBoundEnabled(self, uniqueID, isBoundEnabled):
        if uniqueID in self.__markers:
            self._setMarkerBoundEnabled(self.__markers[uniqueID].getMarkerID(), isBoundEnabled)

    def getMarkerType(self, markerID=INVALID_MARKER_ID):
        return MarkerType.BASE_MARKER_TYPE

    def getMarkerIdFormEntityID(self, generatorIndex):
        for uniqueID in self.__entityMap:
            if self.__entityMap[uniqueID] == generatorIndex:
                return uniqueID

        return INVALID_MARKER_ID

    def getTargetIDFromMarkerID(self, markerID):
        for uniqueID, marker in self.__markers.iteritems():
            if marker.getMarkerID() == markerID:
                return self.__entityMap[uniqueID]

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        return INVALID_MARKER_SUBTYPE if targetID == INVALID_MARKER_ID else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _getMarkerFromTargetID(self, generatorIndex, markerType):
        componentID = self.getMarkerIdFormEntityID(generatorIndex)
        return None if componentID not in self.__markers or markerType != self.getMarkerType() else self.__markers[componentID]

    def __addActiveCommandsOnMarker(self, generatorIndex):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            cmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(generatorIndex, MarkerType.BASE_MARKER_TYPE)
            componentID = self.getMarkerIdFormEntityID(generatorIndex)
            if cmdData:
                marker = self.__markers[componentID]
                isPlayerSender = avatar_getter.getPlayerVehicleID() in cmdData.owners
                countNumber = len(cmdData.owners)
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, countNumber, isPlayerSender)
            return

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, generatorIndex):
        componentID = self.getMarkerIdFormEntityID(generatorIndex)
        if markerType != self.getMarkerType() or componentID not in self.__markers:
            return
        marker = self.__markers[componentID]
        marker.setState(ReplyStateForMarker.CREATE_STATE)
        marker.setActiveCommandID(commandID)
        if _ACTIONS.battleChatCommandFromActionID(commandID).name in AUTOCOMMIT_COMMAND_NAMES:
            isPlayerSender = senderID == avatar_getter.getPlayerVehicleID()
            marker.setIsSticky(isPlayerSender)
            self._setMarkerRepliesAndCheckState(marker, 1, isPlayerSender)
        else:
            self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(False)
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)

    def __onRemoveCommandReceived(self, generatorIndex, markerType):
        componentID = self.getMarkerIdFormEntityID(generatorIndex)
        if markerType != MarkerType.BASE_MARKER_TYPE or componentID not in self.__markers:
            return
        self.__removeCommandReceived(componentID)

    def __removeCommandReceived(self, componentID):
        marker = self.__markers[componentID]
        marker.setActiveCommandID(ReplyStateForMarker.NO_ACTION)
        if marker.getReplyCount() != 0:
            marker.setIsRepliedByPlayer(False)
            marker.setIsReplied(False)
            self._setMarkerReplied(marker, False)
            self._setMarkerReplyCount(marker, 0)
            commands = self.sessionProvider.shared.chatCommands
            commands.sendClearChatCommandsFromTarget(self.__entityMap[componentID], MarkerType.BASE_MARKER_TYPE.name)
        self._checkNextState(marker)
        if marker.getState() == ReplyStateForMarker.NO_ACTION and not marker.getBoundCheckEnabled():
            marker.setBoundCheckEnabled(True)
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)
