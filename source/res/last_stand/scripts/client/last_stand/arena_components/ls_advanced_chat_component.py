# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/arena_components/ls_advanced_chat_component.py
import BigWorld
from arena_components.advanced_chat_component import AdvancedChatComponent
from battleground.location_point_manager import g_locationPointManager
from gui.battle_control import avatar_getter
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType
from last_stand_common.last_stand_constants import LSMarkerComponentNames
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
_actionMarkerByComponents = {LSMarkerComponentNames.CAMP: 'eventCamp',
 LSMarkerComponentNames.MAGNUS: 'eventCollector'}

class LSAdvancedChatComponent(AdvancedChatComponent):

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

    def _getActionMarker(self, cmdID, cmdTargetID):
        command = _ACTIONS.battleChatCommandFromActionID(cmdID)
        if command.name in (BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT, BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT):
            entity = BigWorld.entities.get(cmdTargetID)
            for componentName in _actionMarkerByComponents:
                if componentName in entity.dynamicComponents:
                    return _actionMarkerByComponents[componentName]

            return None
        else:
            return _ACTIONS.battleChatCommandFromActionID(cmdID).vehMarker
