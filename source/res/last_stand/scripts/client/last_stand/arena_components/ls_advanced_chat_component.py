# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/arena_components/ls_advanced_chat_component.py
from __future__ import absolute_import
from functools import partial
import BigWorld
from future.utils import viewitems
from arena_components.advanced_chat_component import AdvancedChatComponent, EMPTY_CHAT_CMD_FLAG, ChatCommandChange, EMPTY_STATE
from battleground.location_point_manager import g_locationPointManager
from gui.battle_control import avatar_getter
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from last_stand_common.last_stand_constants import LSMarkerComponentNames, LS_BATTLE_CHAT_COMMANDS, LS_OBELISK_ACTIVE_TIME
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.gui.battle_session import IBattleSessionProvider
_actionMarkerByComponents = {LSMarkerComponentNames.CAMP: 'eventCamp',
 LSMarkerComponentNames.MAGNUS: 'eventCollector'}

class LSAdvancedChatComponent(AdvancedChatComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, componentSystem):
        super(LSAdvancedChatComponent, self).__init__(componentSystem)
        self._obeliskCommandCallbacks = {}

    @property
    def lsBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def _removeEventListenersAndClear(self):
        for callbackID in self._obeliskCommandCallbacks.values():
            BigWorld.cancelCallback(callbackID)

        self._obeliskCommandCallbacks.clear()
        super(LSAdvancedChatComponent, self)._removeEventListenersAndClear()

    def cleanup(self):
        chatCommands = self.sessionProvider.shared.chatCommands
        arenaDP = self.sessionProvider.getArenaDP()
        if not chatCommands:
            return
        if arenaDP:
            for vInfo in arenaDP.getVehiclesInfoIterator():
                if not arenaDP.isAlly(vInfo.vehicleID) or avatar_getter.getPlayerVehicleID() == vInfo.vehicleID:
                    continue
                chatCommands.sendClearChatCommandsFromTarget(vInfo.vehicleID, MarkerType.VEHICLE_MARKER_TYPE.name)

        self._removeReplyContributionFromPlayer(avatar_getter.getPlayerVehicleID(), MarkerType.INVALID_MARKER_TYPE, -1)
        markedAreas = g_locationPointManager.markedAreas
        removeIDs = markedAreas.keys()
        for targetID in removeIDs:
            markerData = markedAreas[targetID]
            action = _ACTIONS.battleChatCommandFromActionID(markerData.commandID).name
            if action == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE:
                chatCommands.sendCancelReplyChatCommand(targetID, action)
            self._tryRemovingCommandFromMarker(markerData.commandID, targetID, forceRemove=True)

        self._cleanObeliskCommands()

    def _getActionMarker(self, cmdID, cmdTargetID):
        command = _ACTIONS.battleChatCommandFromActionID(cmdID)
        if command.name in (BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT):
            entity = BigWorld.entities.get(cmdTargetID)
            for componentName, marker in viewitems(_actionMarkerByComponents):
                if componentName in entity.dynamicComponents:
                    return marker

            return None
        else:
            return _ACTIONS.battleChatCommandFromActionID(cmdID).vehMarker

    def _handleRegularCommand(self, cmd):
        cmdID = cmd.getID()
        battleChatCommand = _ACTIONS.battleChatCommandFromActionID(cmdID)
        if battleChatCommand.name == LS_BATTLE_CHAT_COMMANDS.LS_OBELISK:
            senderID = self._getCommandCreatorVehID(cmd)
            self._removeReplyContributionFromPlayer(senderID, MarkerType.VEHICLE_MARKER_TYPE, senderID)
            feedbackCtrl = self.sessionProvider.shared.feedback
            if feedbackCtrl is not None:
                feedbackCtrl.showActionMarker(senderID, cmd.getVehMarker(), '', 0, False, False)
            if senderID in self._obeliskCommandCallbacks:
                self._cleanObeliskCommandVehicle(senderID)
            componentSystem = self._componentSystem()
            arena = componentSystem.arena() if componentSystem is not None else None
            if arena is not None:
                arena.onChatCommandTargetUpdate(True, {senderID: (battleChatCommand.vehMarker, EMPTY_CHAT_CMD_FLAG)})
            self._obeliskCommandCallbacks[senderID] = BigWorld.callback(LS_OBELISK_ACTIVE_TIME, partial(self._cleanObeliskCommandVehicle, senderID))
            return
        else:
            super(LSAdvancedChatComponent, self)._handleRegularCommand(cmd)
            return

    def _chatCommandsUpdated(self, cmdMarkerType, cmdTargetID, cmdID, senderVehID, typeOfUpdate):
        super(LSAdvancedChatComponent, self)._chatCommandsUpdated(cmdMarkerType, cmdTargetID, cmdID, senderVehID, typeOfUpdate)
        commandData = self._chatCommands[cmdMarkerType][cmdTargetID][cmdID]
        playerVehID = avatar_getter.getPlayerVehicleID()
        isOneShot = typeOfUpdate == ChatCommandChange.CHAT_CMD_TRIGGERED or playerVehID not in commandData.owners
        isPlayerSender = senderVehID == playerVehID
        if typeOfUpdate == ChatCommandChange.CHAT_CMD_WAS_REPLIED and not isPlayerSender and cmdTargetID == playerVehID:
            isOneShot = False
        if not isOneShot:
            callbackID = self._obeliskCommandCallbacks.pop(senderVehID, None)
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)
        return

    def _cleanObeliskCommandVehicle(self, senderID):
        componentSystem = self._componentSystem()
        arena = componentSystem.arena() if componentSystem is not None else None
        if arena is not None:
            arena.onChatCommandTargetUpdate(True, {senderID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)})
            callbackID = self._obeliskCommandCallbacks.pop(senderID, None)
            if callbackID:
                BigWorld.cancelCallback(callbackID)
        return

    def _cleanObeliskCommands(self):
        lsBattleGuiCtrl = self.lsBattleGuiCtrl
        componentSystem = self._componentSystem()
        arena = componentSystem.arena() if componentSystem is not None else None
        for senderID, callbackID in self._obeliskCommandCallbacks.items():
            BigWorld.cancelCallback(callbackID)
            if lsBattleGuiCtrl is not None:
                lsBattleGuiCtrl.onClearObeliskVehicleMarker(senderID)
            if arena is not None:
                arena.onChatCommandTargetUpdate(True, {senderID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)})

        self._obeliskCommandCallbacks.clear()
        return
