# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/plugins.py
import BigWorld
from gui.battle_control import avatar_getter
from helpers import isPlayerAvatar
from chat_commands_consts import MarkerType
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from arena_components.advanced_chat_component import EMPTY_CHAT_CMD_FLAG, EMPTY_STATE
from historical_battles.gui.Scaleform.daapi.view.battle.markers import HBPlayerPanelMarker, HBVehiclePanelMarker
from historical_battles.gui.Scaleform.daapi.view.battle.components import HBChatCommunicationComponent, getArenaChatCommandData

class HBVehiclePanelMarkerPlugin(HBChatCommunicationComponent):

    def __init__(self, clazz):
        super(HBVehiclePanelMarkerPlugin, self).__init__(self)
        self._clazz = clazz
        self._markers = dict()
        self._vehCmds = dict()

    def start(self):
        super(HBVehiclePanelMarkerPlugin, self).start()
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled += self._onArenaVehicleKilled
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved += self._onVehicleMarkerRemoved
        return

    def stop(self):
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled -= self._onArenaVehicleKilled
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self._onVehicleMarkerRemoved
        self._markers.clear()
        self._vehCmds.clear()
        super(HBVehiclePanelMarkerPlugin, self).stop()
        return

    def _clearMarkers(self):
        self._markers.clear()

    def _clearChatCommandList(self):
        for vehicleID in self._vehCmds:
            self._onChatCommandUpdated(vehicleID, forceUpdate=True)

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        marker = defaultMarker
        if markerType in self._clazz.ALLOWED_MARKER_TYPES:
            if markerType not in self._markers:
                self._markers[markerType] = dict()
            markersByType = self._markers[markerType]
            marker = markersByType.get(markerID, defaultMarker)
            if marker is defaultMarker:
                marker = self._setupMarker(markerID, markerType, defaultMarker)
                if marker is not defaultMarker:
                    markersByType[markerID] = marker
        return marker

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._getMarker(targetID, markerType)

    def _setupMarker(self, markerID, markerType, defaultMarker):
        if markerType in self._clazz.ALLOWED_MARKER_TYPES:
            chatCmdData = getArenaChatCommandData(self.sessionProvider, markerID, markerType)
            if chatCmdData is not None:
                command = _ACTIONS.battleChatCommandFromActionID(chatCmdData.command.getID())
                if command.name in self._clazz.ALLOWED_MARKER_TYPES[markerType]:
                    return self._clazz(markerID=markerID, markerType=markerType, markerSymbolName=command.vehMarker)
        return defaultMarker

    def _onChatCommandUpdated(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        self._vehCmds[vehicleID] = (chatCommandName, chatCommandFlags)
        self._updateChatCommand(vehicleID, chatCommandName, chatCommandFlags, forceUpdate)

    def _updateMarkerOwners(self, marker):
        chatCmdData = getArenaChatCommandData(self.sessionProvider, marker.getMarkerID(), marker.getMarkerType())
        if chatCmdData is not None:
            marker.setMarkerOwners(set(chatCmdData.owners))
        return

    def _setActiveState(self, marker, state):
        super(HBVehiclePanelMarkerPlugin, self)._setActiveState(marker, state)
        self._updateMarkerOwners(marker)

    def _setMarkerReplyCount(self, marker, replyCount):
        super(HBVehiclePanelMarkerPlugin, self)._setMarkerReplyCount(marker, replyCount)
        self._updateMarkerOwners(marker)

    def _setVehicleHealth(self, vehicleID, health):
        if health <= 0:
            marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
            if marker is not None:
                del self._markers[MarkerType.VEHICLE_MARKER_TYPE][vehicleID]
        return

    def _onVehicleMarkerRemoved(self, vehicleID):
        marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        if marker is not None:
            del self._markers[MarkerType.VEHICLE_MARKER_TYPE][vehicleID]
        return

    def _onArenaVehicleKilled(self, vehicleID, *args):
        marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        if marker is not None:
            del self._markers[MarkerType.VEHICLE_MARKER_TYPE][vehicleID]
        return

    def _removeMarker(self, targetID, markerType):
        pass

    def _addMarker(self, markerID, function, *args):
        pass

    def invokeMarker(self, markerID, function, *args):
        pass

    def _setMarkerActive(self, markerID, shouldNotHide):
        pass

    def _setMarkerSticky(self, markerID, isSticky):
        pass

    def _setMarkerBoundEnabled(self, markerID, isEnabled):
        pass

    def _updateChatCommand(self, vehicleID, chatCommandName=EMPTY_STATE, chatCommandFlags=EMPTY_CHAT_CMD_FLAG, forceUpdate=False):
        raise NotImplementedError


class HBPlayerPanelChatCommunicationPlugin(HBVehiclePanelMarkerPlugin):

    def __init__(self):
        super(HBPlayerPanelChatCommunicationPlugin, self).__init__(clazz=HBPlayerPanelMarker)

    def _updateMarkerOwners(self, marker):
        chatCmdData = getArenaChatCommandData(self.sessionProvider, marker.getMarkerID(), marker.getMarkerType())
        if chatCmdData is not None:
            chatCommandName = marker.getMarkerSubtype()
            isOwners = set(chatCmdData.owners)
            wasOwners = marker.getMarkerOwners()
            for vehicleID in wasOwners - isOwners:
                self._onChatCommandUpdated(vehicleID)

            for vehicleID in isOwners - wasOwners:
                self._onChatCommandUpdated(vehicleID, chatCommandName, EMPTY_CHAT_CMD_FLAG)

        super(HBPlayerPanelChatCommunicationPlugin, self)._updateMarkerOwners(marker)
        return

    def _setVehicleHealth(self, vehicleID, health):
        if health <= 0:
            if not self.sessionProvider.getArenaDP().isAlly(vehicleID):
                marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
                if marker is not None:
                    for ownerID in marker.getMarkerOwners():
                        self._onChatCommandUpdated(ownerID, forceUpdate=True)

            else:
                chatCommandName, _ = self._vehCmds.pop(vehicleID, (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG))
                if chatCommandName != EMPTY_STATE:
                    self._onChatCommandUpdated(vehicleID, forceUpdate=True)
        super(HBPlayerPanelChatCommunicationPlugin, self)._setVehicleHealth(vehicleID, health)
        return

    def _onVehicleMarkerRemoved(self, vehicleID):
        marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        if marker is not None:
            playerVehicleID = avatar_getter.getPlayerVehicleID()
            if playerVehicleID in marker.getMarkerOwners():
                self._onChatCommandUpdated(playerVehicleID, forceUpdate=True)
        super(HBPlayerPanelChatCommunicationPlugin, self)._onVehicleMarkerRemoved(vehicleID)
        return

    def _onArenaVehicleKilled(self, vehicleID, *args):
        marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
        if marker is not None:
            for ownerID in marker.getMarkerOwners():
                self._onChatCommandUpdated(ownerID, forceUpdate=True)

            chatCmdData = getArenaChatCommandData(self.sessionProvider, marker.getMarkerID(), marker.getMarkerType())
            if chatCmdData is not None:
                for ownerID in chatCmdData.owners:
                    self._onChatCommandUpdated(ownerID, forceUpdate=True)

        super(HBPlayerPanelChatCommunicationPlugin, self)._onArenaVehicleKilled(vehicleID, *args)
        return


class HBEnemyPanelChatCommunicationPlugin(HBVehiclePanelMarkerPlugin):

    def __init__(self):
        super(HBEnemyPanelChatCommunicationPlugin, self).__init__(clazz=HBVehiclePanelMarker)

    def _updateMarkerOwners(self, marker):
        chatCmdData = getArenaChatCommandData(self.sessionProvider, marker.getMarkerID(), marker.getMarkerType())
        if chatCmdData is not None:
            self._onChatCommandUpdated(marker.getMarkerID(), marker.getMarkerSubtype() if chatCmdData.owners else EMPTY_STATE)
        super(HBEnemyPanelChatCommunicationPlugin, self)._updateMarkerOwners(marker)
        return

    def _setVehicleHealth(self, vehicleID, health):
        if health <= 0:
            if self.sessionProvider.getArenaDP().isAlly(vehicleID):
                markers = self._markers.get(MarkerType.VEHICLE_MARKER_TYPE) or {}
                for marker in markers.itervalues():
                    self._updateMarkerOwners(marker)

            else:
                chatCommandName, _ = self._vehCmds.pop(vehicleID, (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG))
                if chatCommandName != EMPTY_STATE:
                    self._onChatCommandUpdated(vehicleID, forceUpdate=True)
        super(HBEnemyPanelChatCommunicationPlugin, self)._setVehicleHealth(vehicleID, health)

    def _onVehicleMarkerRemoved(self, vehicleID):
        if not self.sessionProvider.getArenaDP().isAlly(vehicleID):
            marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
            if marker is not None:
                self._onChatCommandUpdated(vehicleID, forceUpdate=True)
        super(HBEnemyPanelChatCommunicationPlugin, self)._onVehicleMarkerRemoved(vehicleID)
        return

    def _onArenaVehicleKilled(self, vehicleID, *args):
        if self.sessionProvider.getArenaDP().isAlly(vehicleID):
            markers = self._markers.get(MarkerType.VEHICLE_MARKER_TYPE) or {}
            for marker in markers.itervalues():
                self._updateMarkerOwners(marker)

        else:
            marker = self._getMarkerFromTargetID(vehicleID, MarkerType.VEHICLE_MARKER_TYPE)
            if marker is not None:
                self._onChatCommandUpdated(vehicleID, forceUpdate=True)
        super(HBEnemyPanelChatCommunicationPlugin, self)._onArenaVehicleKilled(vehicleID, *args)
        return
