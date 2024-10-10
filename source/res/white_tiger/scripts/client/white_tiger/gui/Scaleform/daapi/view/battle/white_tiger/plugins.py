# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/plugins.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EventBusPlugin, AreaMarkerPlugin, ChatCommunicationComponent
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker, ReplyStateForMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions, EventKeys
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS, FEEDBACK_EVENT_ID
from chat_commands_consts import INVALID_MARKER_SUBTYPE, INVALID_MARKER_ID, MarkerType, DefaultMarkerSubType
from gui.impl import backport
from gui.impl.gen import R
from gui.wt_event.wt_event_helpers import isBossTeam

class WhiteTigerVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):

    def _getMarkerSymbol(self, vehicleID):
        return MARKER_SYMBOL_NAME.EVENT_VEHICLE_MARKER

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(WhiteTigerVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
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
        if 'event_boss' in vType.tags:
            classTag = 'boss'
        canShowPlasma = not isBossTeam(vInfo.team)
        self._invokeMarker(markerID, 'showPlasmaBuff', canShowPlasma)
        if canShowPlasma:
            plasmaBuffValue = vInfo.gameModeSpecific.getValue(EventKeys.PLASMA_COUNT.value)
            if plasmaBuffValue is not None:
                self._invokeMarker(markerID, 'setPlasmaBuffValue', plasmaBuffValue)
        self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, nameParts.vehicleName, vType.level, nameParts.playerFullName, nameParts.playerName, nameParts.clanAbbrev, nameParts.regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')
        return


class WhiteTigerEventBusPlugin(EventBusPlugin):

    def start(self):
        super(WhiteTigerEventBusPlugin, self).start()
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
        super(WhiteTigerEventBusPlugin, self).stop()
        return

    def _onShowSpawnPoints(self, *_):
        self._parentObj.setVisible(False)

    def _onCloseSpawnPoints(self, *_):
        self._parentObj.setVisible(True)


class WhiteTigerBaseAreaMarkerPlugin(AreaMarkerPlugin, ChatCommunicationComponent):
    __slots__ = ('__markers', '__entityMap', '__clazz')

    def __init__(self, parentObj, clazz=BaseMarker):
        super(WhiteTigerBaseAreaMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__clazz = clazz
        self.__entityMap = {}
        ChatCommunicationComponent.__init__(self, parentObj)

    def start(self):
        super(WhiteTigerBaseAreaMarkerPlugin, self).start()
        ChatCommunicationComponent.start(self)

    def stop(self):
        self.__markers = {}
        ChatCommunicationComponent.stop(self)
        super(WhiteTigerBaseAreaMarkerPlugin, self).stop()

    def createMarker(self, uniqueID, matrixProvider, active, symbol=settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER):
        if uniqueID in self.__markers:
            return False
        markerID = self._createMarkerWithMatrix(symbol, matrixProvider, active=active)
        marker = self.__clazz(markerID, True)
        self.__markers[uniqueID] = marker
        marker.setState(ReplyStateForMarker.NO_ACTION)
        self._setActiveState(marker, marker.getState())
        self.__addActiveCommandsOnMarker(uniqueID)
        return True

    def mapCustomEntityID(self, uniqueID, entityID):
        self.__entityMap[uniqueID] = entityID

    def deleteCustomEntityID(self, uniqueID):
        if uniqueID in self.__entityMap:
            self.__entityMap.pop(uniqueID)

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

    def setMarkerBoundEnabled(self, markerID, isBoundEnabled):
        if markerID in self.__markers:
            self._setMarkerBoundEnabled(self.__markers[markerID].getMarkerID(), isBoundEnabled)

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def getMarkerIdFormEntityID(self, entityID):
        for entityIDEntry in self.__entityMap:
            if self.__entityMap[entityIDEntry] == entityID:
                return entityIDEntry

        return INVALID_MARKER_ID

    def getTargetIDFromMarkerID(self, markerID):
        for baseID, marker in self.__markers.iteritems():
            if marker.getMarkerID() == markerID:
                return self.__entityMap[baseID]

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        return INVALID_MARKER_SUBTYPE if targetID == INVALID_MARKER_ID else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _getMarkerFromTargetID(self, baseID, markerType):
        targetID = self.getMarkerIdFormEntityID(baseID)
        return None if targetID not in self.__markers or markerType != self.getMarkerType() else self.__markers[targetID]

    def __addActiveCommandsOnMarker(self, markerId):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            cmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(markerId, MarkerType.BASE_MARKER_TYPE)
            if cmdData:
                marker = self.__markers[markerId]
                isPlayerSender = avatar_getter.getPlayerVehicleID() in cmdData.owners
                countNumber = len(cmdData.owners)
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, countNumber, isPlayerSender)
            return
