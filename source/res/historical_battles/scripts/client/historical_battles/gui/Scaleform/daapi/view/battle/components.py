# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/components.py
import BigWorld
from helpers import isPlayerAvatar
from gui.shared.utils.plugins import IPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import ChatCommunicationComponent, ReplyStateForMarker
from gui.battle_control import avatar_getter, matrix_factory
from messenger.proto.bw_chat2.battle_chat_cmd import AUTOCOMMIT_COMMAND_NAMES
from chat_commands_consts import MarkerType, LocationMarkerSubType, INVALID_COMMAND_ID, INVALID_TARGET_ID, BATTLE_CHAT_COMMAND_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS, messageArgs

def getArenaChatCommandData(sessionProvider, targetID, markerType):
    advChatCmp = getattr(sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
    return advChatCmp.getCommandDataForTargetIDAndMarkerType(targetID, markerType)


def cancelPlayerReplyForMarker(sessionProvider, targetID, markerType):
    chatCmdData = getArenaChatCommandData(sessionProvider, targetID, markerType)
    if chatCmdData is not None and avatar_getter.getPlayerVehicleID() in chatCmdData.owners:
        commands = sessionProvider.shared.chatCommands
        if commands is not None:
            commands.sendCancelReplyChatCommand(targetID, _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).name)
    return


def sendPlayerReplyForMarker(sessionProvider, targetID, markerType):
    commands = sessionProvider.shared.chatCommands
    if commands is not None:
        chatCmdData = getArenaChatCommandData(sessionProvider, targetID, markerType)
        if chatCmdData is not None:
            if avatar_getter.getPlayerVehicleID() in chatCmdData.owners:
                commands.sendCancelReplyChatCommand(targetID, _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID()).name)
        elif markerType == MarkerType.VEHICLE_MARKER_TYPE:
            commands.sendTargetedCommand(BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY if sessionProvider.getArenaDP().isAlly(targetID) else BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, targetID)
    return


def _extractIntFeatureIDFromText(markerText):
    try:
        featureID = int(markerText) if markerText else 0
    except ValueError:
        featureID = 0

    return featureID


class IPluginComponent(IPlugin):

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        return defaultMarker

    def _getTargetIDFromVehicleID(self, vehicleID):
        return INVALID_TARGET_ID

    def getMarkerType(self):
        raise NotImplementedError

    def getMarkerSubType(self):
        raise NotImplementedError

    def getTargetIDFromMarkerID(self, markerID):
        raise NotImplementedError

    def _addMarker(self, targetID, position, featureID):
        raise NotImplementedError

    def _removeMarker(self, targetID, markerType):
        raise NotImplementedError

    def _updateMarker(self, targetID, isReplied, replierVehicleID):
        raise NotImplementedError

    def invokeMarker(self, markerID, function, *args):
        raise NotImplementedError

    def _setMarkerActive(self, markerID, shouldNotHide):
        raise NotImplementedError

    def _setMarkerSticky(self, markerID, isSticky):
        raise NotImplementedError

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        raise NotImplementedError


class HBChatCommunicationComponent(IPluginComponent, ChatCommunicationComponent):

    def start(self):
        super(HBChatCommunicationComponent, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer += self.__setInFocusForPlayer
            ctrl.onAddCommandReceived += self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.setInFocusForPlayer -= self.__setInFocusForPlayer
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        super(HBChatCommunicationComponent, self).stop()
        return

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, addID):
        marker = self._getMarkerFromTargetID(addID, markerType)
        if marker is not None:
            marker.setState(ReplyStateForMarker.CREATE_STATE)
            marker.setActiveCommandID(commandID)
            if _ACTIONS.battleChatCommandFromActionID(commandID).name in AUTOCOMMIT_COMMAND_NAMES:
                isPlayerSender = senderID == avatar_getter.getPlayerVehicleID()
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, 1, isPlayerSender)
            else:
                self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
            if not avatar_getter.isVehicleAlive() and marker.getBoundCheckEnabled():
                if hasattr(marker, 'setBoundCheckEnabled'):
                    marker.setBoundCheckEnabled(False)
                self._setMarkerBoundEnabled(marker.getMarkerID(), False)
        return

    def __onRemoveCommandReceived(self, removeID, markerType):
        marker = self._getMarkerFromTargetID(removeID, markerType)
        if marker is not None:
            marker.setActiveCommandID(INVALID_COMMAND_ID)
            if marker.getReplyCount() != 0:
                marker.setIsRepliedByPlayer(False)
                self._setMarkerReplied(marker, False)
                self._setMarkerReplyCount(marker, 0)
            self._checkNextState(marker)
            if marker.getState() == ReplyStateForMarker.NO_ACTION and not marker.getBoundCheckEnabled():
                if hasattr(marker, 'setBoundCheckEnabled'):
                    marker.setBoundCheckEnabled(True)
                self._setMarkerBoundEnabled(marker.getMarkerID(), True)
        return

    def __setInFocusForPlayer(self, oldTargetID, oldTargetType, newTargetID, newTargetType, oneShot):
        oldTargetMarker = self._getMarkerFromTargetID(oldTargetID, oldTargetType)
        newTargetMarker = self._getMarkerFromTargetID(newTargetID, newTargetType)
        if oldTargetMarker is not None:
            self.__makeMarkerSticky(oldTargetMarker, False)
        if newTargetMarker is not None:
            self.__makeMarkerSticky(newTargetMarker, True)
        return

    def __makeMarkerSticky(self, marker, setSticky):
        self._setMarkerSticky(marker.getMarkerID(), setSticky)
        marker.setIsSticky(setSticky)
        self._checkNextState(marker)

    def __onAddCommandReceived(self, addedID, markerType):
        chatCmdData = getArenaChatCommandData(self.sessionProvider, addedID, markerType)
        if chatCmdData is not None:
            marker = self._getMarkerFromTargetID(addedID, markerType)
            if marker is not None:
                marker.setState(ReplyStateForMarker.CREATE_STATE)
                marker.setActiveCommandID(chatCmdData.command.getID())
                self._setActiveState(marker, ReplyStateForMarker.CREATE_STATE)
        return


class HBStaticObjectivesMarkerComponent(IPluginComponent):

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addLocation
            ctrl.onStaticMarkerRemoved -= self.__removeLocation
            ctrl.onReplyFeedbackReceived -= self.__updateLocation
        super(HBStaticObjectivesMarkerComponent, self).stop()
        return

    def start(self):
        super(HBStaticObjectivesMarkerComponent, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addLocation
            ctrl.onStaticMarkerRemoved += self.__removeLocation
            ctrl.onReplyFeedbackReceived += self.__updateLocation
        return

    def _getMarkerText(self):
        pass

    def __addLocation(self, areaID, creatorID, position, locationMarkerSubtype, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        if locationMarkerSubtype == LocationMarkerSubType.OBJECTIVES_POINT_SUBTYPE and creatorID == self.sessionProvider.arenaVisitor.getArenaUniqueID():
            self._addMarker(areaID, position, _extractIntFeatureIDFromText(markerText))

    def __updateLocation(self, targetID, replierVehicleID, markerType, oldReplyCount, newReplyCount):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is None:
            return
        else:
            if replierVehicleID == self.sessionProvider.arenaVisitor.getArenaUniqueID():
                marker.isGoalForPlayer = oldReplyCount < newReplyCount
                self._updateMarker(targetID, oldReplyCount < newReplyCount, replierVehicleID)
            elif replierVehicleID == avatar_getter.getPlayerVehicleID():
                if oldReplyCount < newReplyCount:
                    msgText = self._getMarkerText()
                    if msgText:
                        chatCmdData = getArenaChatCommandData(self.sessionProvider, targetID, markerType)
                        if chatCmdData is not None and chatCmdData.command.isServerCommand():
                            player = BigWorld.player()
                            if player is not None:
                                mapsCtrl = self.sessionProvider.dynamic.maps
                                if mapsCtrl and mapsCtrl.hasMinimapGrid():
                                    cellId = mapsCtrl.getMinimapCellIdByPosition(marker.getPosition())
                                    if cellId is not None:
                                        msgText = msgText + mapsCtrl.getMinimapCellNameById(cellId)
                                player.base.messenger_onActionByClient_chat2(_ACTIONS.BROADCAST_BATTLE_MESSAGE, 0, messageArgs(strArg1=msgText))
                self._updateMarker(targetID, oldReplyCount < newReplyCount, replierVehicleID)
            return

    def __removeLocation(self, targetID):
        marker = self._getMarkerFromTargetID(targetID, MarkerType.LOCATION_MARKER_TYPE)
        if marker is not None:
            cancelPlayerReplyForMarker(self.sessionProvider, targetID, MarkerType.LOCATION_MARKER_TYPE)
            self._removeMarker(targetID, MarkerType.LOCATION_MARKER_TYPE)
        return


class HBVehicleObjectivesMarkerComponent(IPluginComponent):

    def start(self):
        super(HBVehicleObjectivesMarkerComponent, self).start()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved += self.__onMinimapVehicleRemoved
            ctrl.onVehicleMarkerRemoved += self._onVehicleMarkerRemoved
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved -= self.__onMinimapVehicleRemoved
            ctrl.onVehicleMarkerRemoved -= self._onVehicleMarkerRemoved
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled -= self.__onArenaVehicleKilled
        super(HBVehicleObjectivesMarkerComponent, self).stop()
        return

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        if vProxy.isAlive():
            self.__switchVehicleVisualState(vInfo.vehicleID, True)

    def __onMinimapVehicleRemoved(self, vehicleID):
        self.__switchVehicleVisualState(vehicleID, False)

    def __switchVehicleVisualState(self, vehicleID, isActive):
        targetID = self._getTargetIDFromVehicleID(vehicleID)
        marker = self._getMarkerFromTargetID(targetID, MarkerType.LOCATION_MARKER_TYPE)
        if marker is not None:
            marker.setActive(not isActive)
            marker.isInAOI = isActive
            self._setVehicleMatrixAndLocation(marker, vehicleID)
            cancelPlayerReplyForMarker(self.sessionProvider, targetID, MarkerType.LOCATION_MARKER_TYPE)
        cancelPlayerReplyForMarker(self.sessionProvider, vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        return

    def _setVehicleMatrixAndLocation(self, marker, vehicleID):
        matrix, _ = matrix_factory.getVehicleMPAndLocation(vehicleID, self.sessionProvider.arenaVisitor.getArenaPositions())
        if matrix is not None:
            marker.setMatrix(matrix)
            if self.getMarkerType() == MarkerType.LOCATION_MARKER_TYPE:
                self._setMarkerMatrix(marker.getMarkerID(), matrix)
                self._setMarkerActive(marker.getMarkerID(), not marker.isInAOI)
        return

    def _onVehicleMarkerRemoved(self, vehicleID):
        cancelPlayerReplyForMarker(self.sessionProvider, vehicleID, MarkerType.VEHICLE_MARKER_TYPE)

    def __onArenaVehicleKilled(self, victimID, attackerID, equipmentID, reason, numVehiclesAffected):
        targetID = self._getTargetIDFromVehicleID(victimID)
        marker = self._getMarkerFromTargetID(targetID, MarkerType.LOCATION_MARKER_TYPE)
        if marker is not None:
            self._removeMarker(targetID, MarkerType.LOCATION_MARKER_TYPE)
        cancelPlayerReplyForMarker(self.sessionProvider, victimID, MarkerType.VEHICLE_MARKER_TYPE)
        return
