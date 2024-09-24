# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/advanced_chat_component.py
import logging
from collections import OrderedDict, defaultdict, namedtuple
from functools import partial
from enum import Enum
import BigWorld
from PlayerEvents import g_playerEvents
from arena_component_system.client_arena_component_system import ClientArenaComponent
from battleground.location_point_manager import g_locationPointManager
from chat_commands_consts import ReplyState, _COMMAND_NAME_TRANSFORM_MARKER_TYPE, BATTLE_CHAT_COMMAND_NAMES, _DEFAULT_ACTIVE_COMMAND_TIME, _DEFAULT_SPG_AREA_COMMAND_TIME, MarkerType, ONE_SHOT_COMMANDS_TO_REPLIES, COMMAND_RESPONDING_MAPPING
from constants import ARENA_BONUS_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency, i18n, CallbackDelayer
from messenger import MessengerEntry
from messenger.m_constants import MESSENGER_COMMAND_TYPE, USER_ACTION_ID
from messenger.proto.bw_chat2.battle_chat_cmd import BattleCommandFactory, AUTOCOMMIT_COMMAND_NAMES, LOCATION_CMD_NAMES
from messenger.proto.bw_chat2.chat_handlers import g_mutedMessages
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS_BY_NAMES, messageArgs
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.account_helpers.settings_core import IBattleCommunicationsSettings
from skeletons.gui.battle_session import IBattleSessionProvider
from shared_utils import first
EMPTY_STATE = ''
MARKER_ACTION_POSITIVE = 'positive'
MARKER_ACTION_SUPPORTING_YOU = 'supportingYou'
EMPTY_CHAT_CMD_FLAG = 0
TARGET_CHAT_CMD_FLAG = 1
PLAYER_IS_CHAT_CMD_TARGET_FLAG = 2
_CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_VEHICLES = {BATTLE_CHAT_COMMAND_NAMES.SOS: BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY: BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY}
_CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_BASES = {BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE}
_logger = logging.getLogger(__name__)

class ChatCommandChange(Enum):
    CHAT_CMD_WAS_REMOVED = 3
    CHAT_CMD_WAS_REPLIED = 2
    CHAT_CMD_TRIGGERED = 1


AdvancedChatCommandData = namedtuple('AdvancedChatCommandData', ('command', 'commandCreatorVehID', 'callbackID', 'owners'))

class MarkerInFocus(namedtuple('MarkerInFocus', ('commandID', 'targetID', 'markerType'))):

    def isFocused(self, targetID, markerType):
        return self.targetID == targetID and self.markerType == markerType


class AdvancedChatComponent(ClientArenaComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    battleCommunications = dependency.descriptor(IBattleCommunicationsSettings)

    def __init__(self, componentSystem):
        super(AdvancedChatComponent, self).__init__(componentSystem)
        self._chatCommands = defaultdict(dict)
        self._delayer = CallbackDelayer.CallbacksSetByID()
        self._callbackIDCounter = 0
        self._markerInFocus = None
        self._temporaryStickyCommands = defaultdict(dict)
        self._isEnabled = None
        return

    def activate(self):
        super(AdvancedChatComponent, self).activate()
        self.battleCommunications.onChanged += self._onBattleCommunicationsSettingsChanged
        self._isEnabled = self.battleCommunications.isEnabled
        player = BigWorld.player()
        if player is None:
            return
        elif player.isDestroyed:
            return
        elif not player.userSeesWorld():
            g_playerEvents.onAvatarReady += self._onAvatarReady
            return
        elif not self._isEnabled:
            return
        else:
            componentSystem = self._componentSystem()
            if componentSystem is not None:
                if player.isPlayer:
                    player.base.messenger_onActionByClient_chat2(_ACTIONS.REINIT_BATTLE_CHAT, 0, messageArgs())
            self._addEventListeners()
            return

    def deactivate(self):
        super(AdvancedChatComponent, self).deactivate()
        self.battleCommunications.onChanged -= self._onBattleCommunicationsSettingsChanged
        if self._isEnabled:
            self._removeEventListenersAndClear()
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self._onVehicleMarkerRemoved

    def _onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        self._isEnabled = bool(self.battleCommunications.isEnabled)
        if self._isEnabled:
            self._addEventListeners()

    def getReplyStateForTargetIDAndMarkerType(self, targetID, targetMarkerType):
        if targetMarkerType in self._chatCommands and targetID in self._chatCommands[targetMarkerType]:
            commands = self._chatCommands[targetMarkerType][targetID]
            for commandID, commandData in ((k, commands[k]) for k in reversed(commands)):
                commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
                if commandName not in BATTLE_CHAT_COMMANDS_BY_NAMES:
                    continue
                hasRepliedTo = avatar_getter.getPlayerVehicleID() in commandData.owners
                if hasRepliedTo:
                    return (ReplyState.CAN_CANCEL_REPLY, commandName)
                if commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                    return (ReplyState.CAN_CONFIRM, commandName)
                return (ReplyState.CAN_REPLY, commandName)

        playerVehicleID = avatar_getter.getPlayerVehicleID()
        if playerVehicleID in self._chatCommands[targetMarkerType]:
            commands = self._chatCommands[targetMarkerType][playerVehicleID]
            for commandID, commandData in ((k, commands[k]) for k in reversed(commands)):
                if targetID in commandData.owners and self._delayer.hasDelayedCallbackID(commandData.callbackID):
                    commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
                    if commandName not in BATTLE_CHAT_COMMANDS_BY_NAMES:
                        continue
                    if commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                        return (ReplyState.CAN_CONFIRM, commandName)
                    if commandName in COMMAND_RESPONDING_MAPPING.keys():
                        return (ReplyState.CAN_RESPOND, commandName)

        return (ReplyState.NO_REPLY, None)

    def getCommandDataForTargetIDAndMarkerType(self, targetID, targetMarkerType):
        if targetMarkerType not in self._chatCommands:
            return None
        else:
            return self._chatCommands[targetMarkerType][targetID].values()[-1] if targetID in self._chatCommands[targetMarkerType] else None

    def isTargetAllyCommittedToMe(self, targetID):
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY]
        if markerType != MarkerType.VEHICLE_MARKER_TYPE or markerType not in self._chatCommands or targetID == -1:
            return False
        cmdTargetID = avatar_getter.getPlayerVehicleID()
        if cmdTargetID in self._chatCommands[markerType]:
            commands = self._chatCommands[markerType][cmdTargetID]
            for _, commandData in ((k, commands[k]) for k in reversed(commands)):
                if targetID in commandData.owners:
                    return True

        return False

    def removeActualTargetIfDestroyed(self, targetID, markerType):
        commands = self.sessionProvider.shared.chatCommands
        playerVehID = avatar_getter.getPlayerVehicleID()
        self._removeActualTargetIfDestroyed(commands, playerVehID, targetID, markerType)

    def _addEventListeners(self):
        g_messengerEvents.channels.onCommandReceived += self._onCommandReceived
        g_messengerEvents.users.onBattleUserActionReceived += self._me_onBattleUserActionReceived
        componentSystem = self._componentSystem()
        if componentSystem is not None:
            arena = componentSystem.arena()
            if arena is not None:
                arena.onVehicleKilled += self._onArenaVehicleKilled
                if arena.bonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
                    self._addEpicBattleEventListeners()
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived += self._onCommandReceived
        g_playerEvents.onAvatarBecomePlayer += self._onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self._onAvatarBecomeNonPlayer
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def _addEpicBattleEventListeners(self):
        if self._componentSystem() is None:
            return
        else:
            sectorBaseComponent = self._componentSystem().sectorBaseComponent
            if sectorBaseComponent is not None:
                sectorBaseComponent.onSectorBaseCaptured += self._onSectorBaseCaptured
            destructibleComponent = self._componentSystem().destructibleEntityComponent
            if destructibleComponent is not None:
                destructibleComponent.onDestructibleEntityStateChanged += self._onDestructibleEntityStateChanged
            return

    def _removeEventListenersAndClear(self):
        g_messengerEvents.channels.onCommandReceived -= self._onCommandReceived
        g_messengerEvents.users.onBattleUserActionReceived -= self._me_onBattleUserActionReceived
        g_playerEvents.onAvatarBecomePlayer -= self._onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self._onAvatarBecomeNonPlayer
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        componentSystem = self._componentSystem()
        if componentSystem is not None:
            arena = componentSystem.arena()
            if arena is not None:
                arena.onVehicleKilled -= self._onArenaVehicleKilled
                if arena.bonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
                    self._removeEpicBattleEventsListeners()
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived -= self._onCommandReceived
        self._chatCommands.clear()
        self._delayer.clear()
        self._temporaryStickyCommands.clear()
        self._markerInFocus = None
        return

    def _removeEpicBattleEventsListeners(self):
        if self._componentSystem() is None:
            return
        else:
            sectorBaseComponent = self._componentSystem().sectorBaseComponent
            if sectorBaseComponent is not None:
                sectorBaseComponent.onSectorBaseCaptured -= self._onSectorBaseCaptured
            destructibleComponent = self._componentSystem().destructibleEntityComponent
            if destructibleComponent is not None:
                destructibleComponent.onDestructibleEntityStateChanged -= self._onDestructibleEntityStateChanged
            return

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING and avatar_getter.isObserver():
            self._removeActiveCommands()

    def _onServerCommandReceived(self, cmd):
        targetID = cmd.getFirstTargetID()
        if MarkerType.LOCATION_MARKER_TYPE not in self._chatCommands or targetID not in self._chatCommands[MarkerType.LOCATION_MARKER_TYPE]:
            if cmd.isLocationRelatedCommand():
                self._handleServerLocationCommand(cmd)
            return
        else:
            command = BATTLE_CHAT_COMMANDS_BY_NAMES.get(cmd.getRepliedToChatCommand())
            if command is None:
                return
            commandID = command.id
            commandData = cmd.getCommandData()
            commandCreatorID = commandData['int64Arg1']
            if cmd.isReply() or cmd.isCancelReply():
                self._notifyReplyCommandUpdate(targetID, commandCreatorID, commandID, int(cmd.isCancelReply()), int(cmd.isReply()))
            self._chatCommandsUpdated(MarkerType.LOCATION_MARKER_TYPE, targetID, commandID, commandCreatorID, ChatCommandChange.CHAT_CMD_WAS_REPLIED if cmd.isReply() else ChatCommandChange.CHAT_CMD_WAS_REMOVED)
            if cmd.isClearChatCommand():
                self._tryRemovingCommandFromMarker(commandID, targetID, True)
            return

    def _handleServerLocationCommand(self, cmd):
        targetID = cmd.getFirstTargetID()
        command = _ACTIONS.battleChatCommandFromActionID(cmd.getID())
        if command.name not in LOCATION_CMD_NAMES:
            return
        commandData = cmd.getCommandData()
        commandCreatorID = commandData['int64Arg1']
        commandGlobalName = commandData['strArg1']
        self._addCommandToList(command.id, command.name, commandCreatorID, targetID, cmd, 0.0)
        localizedName = i18n.makeString(commandGlobalName)
        position = cmd.getMarkedPosition()
        g_locationPointManager.addLocationPoint(position, targetID, commandCreatorID, command.id, 0.0, localizedName, 0, False)

    def _chatCommandsUpdated(self, cmdMarkerType, cmdTargetID, cmdID, senderVehID, typeOfUpdate):
        componentSystem = self._componentSystem()
        if componentSystem is None or componentSystem.arena() is None:
            return
        else:
            arena = componentSystem.arena()
            commandData = self._chatCommands[cmdMarkerType][cmdTargetID][cmdID]
            playerVehID = avatar_getter.getPlayerVehicleID()
            chatStats = None
            isOneShot = False
            isPlayerSender = senderVehID == playerVehID
            if typeOfUpdate == ChatCommandChange.CHAT_CMD_WAS_REMOVED:
                if playerVehID in commandData.owners or playerVehID == cmdTargetID or self._isLastPrebattleMarkerOwner(cmdMarkerType, cmdID, commandData) or not self._isAliveVehicle(senderVehID):
                    chatStats = {senderVehID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)}
                    if self._isPrebattleWaypoint(cmdMarkerType, cmdID):
                        if senderVehID in commandData.owners:
                            vehID = senderVehID
                        elif len(commandData.owners) == 1:
                            vehID = first(commandData.owners)
                        else:
                            _logger.debug('Prebattle waypoint command data is incorrect')
                            return
                        chatStats = {vehID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)}
                    elif isPlayerSender:
                        chatStats = dict(((vehID, (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)) for vehID in commandData.owners))
                        if cmdMarkerType == MarkerType.VEHICLE_MARKER_TYPE:
                            chatStats[cmdTargetID] = (EMPTY_STATE, TARGET_CHAT_CMD_FLAG)
                    elif cmdMarkerType == MarkerType.VEHICLE_MARKER_TYPE and self._markerInFocus is not None and senderVehID == self._markerInFocus.targetID:
                        if self._isAliveVehicle(senderVehID):
                            actionMarker = _ACTIONS.battleChatCommandFromActionID(self._markerInFocus.commandID).vehMarker
                            chatStats[senderVehID] = (actionMarker, TARGET_CHAT_CMD_FLAG)
            elif typeOfUpdate in (ChatCommandChange.CHAT_CMD_WAS_REPLIED, ChatCommandChange.CHAT_CMD_TRIGGERED):
                actionMarker = self._getActionMarker(cmdID, cmdTargetID)
                isOneShot = typeOfUpdate == ChatCommandChange.CHAT_CMD_TRIGGERED or playerVehID not in commandData.owners
                if not isOneShot:
                    chatStats = dict(((vehID, (actionMarker, EMPTY_CHAT_CMD_FLAG)) for vehID in commandData.owners))
                    if cmdMarkerType == MarkerType.VEHICLE_MARKER_TYPE and cmdTargetID != playerVehID:
                        chatStats[cmdTargetID] = (actionMarker, TARGET_CHAT_CMD_FLAG)
                elif typeOfUpdate == ChatCommandChange.CHAT_CMD_WAS_REPLIED and not isPlayerSender and cmdTargetID == playerVehID:
                    isOneShot = False
                    chatStats = {senderVehID: (actionMarker, PLAYER_IS_CHAT_CMD_TARGET_FLAG)}
                elif isOneShot and not isPlayerSender:
                    chatStats = {senderVehID: (actionMarker, EMPTY_CHAT_CMD_FLAG)}
            if cmdTargetID != -1 and self.isTargetAllyCommittedToMe(cmdTargetID) and not isOneShot and chatStats is not None and cmdTargetID in chatStats.keys() and chatStats[cmdTargetID][1] == TARGET_CHAT_CMD_FLAG:
                del chatStats[cmdTargetID]
            if chatStats is not None:
                if isOneShot:
                    arena.onChatCommandTriggered(chatStats)
                else:
                    arena.onChatCommandTargetUpdate(True, chatStats)
            return

    def _getActionMarker(self, cmdID, cmdTargetID):
        return _ACTIONS.battleChatCommandFromActionID(cmdID).vehMarker

    def _onDestructibleEntityStateChanged(self, entityID):
        if self._markerInFocus is None:
            return
        else:
            destructibleComponent = self.sessionProvider.arenaVisitor.getComponentSystem().destructibleEntityComponent
            if destructibleComponent is None:
                _logger.error('Expected DestructibleEntityComponent not present!')
                return
            hq = destructibleComponent.getDestructibleEntity(entityID)
            if hq is None:
                _logger.error('Expected DestructibleEntity not present! Id: ' + str(entityID))
                return
            if not hq.isAlive():
                playerVehID = avatar_getter.getPlayerVehicleID()
                commands = self.sessionProvider.shared.chatCommands
                self._removeActualTargetIfDestroyed(commands, playerVehID, entityID, MarkerType.HEADQUARTER_MARKER_TYPE)
            return

    def _onSectorBaseCaptured(self, baseId, _):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            playerVehID = avatar_getter.getPlayerVehicleID()
            commands = self.sessionProvider.shared.chatCommands
            self._removeActualTargetIfDestroyed(commands, playerVehID, baseId, MarkerType.BASE_MARKER_TYPE)
        return

    def _onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        if not self.sessionProvider.shared.chatCommands:
            return
        else:
            playerVehID = avatar_getter.getPlayerVehicleID()
            commands = self.sessionProvider.shared.chatCommands
            self._removeActualTargetIfDestroyed(commands, playerVehID, targetID, MarkerType.VEHICLE_MARKER_TYPE)
            if self._markerInFocus is None:
                return
            if playerVehID == targetID:
                commands.sendClearChatCommandsFromTarget(targetID, self._markerInFocus.markerType.name)
            return

    def _removeActualTargetIfDestroyed(self, commands, playerVehID, targetID, markerType):
        if self._markerInFocus and self._markerInFocus.isFocused(targetID, markerType):
            listOfCommands = self._chatCommands[markerType].get(targetID, {})
            for _, commandData in listOfCommands.iteritems():
                if playerVehID == commandData.commandCreatorVehID or playerVehID in commandData.owners:
                    commands.sendClearChatCommandsFromTarget(targetID, markerType.name)

        elif markerType == MarkerType.VEHICLE_MARKER_TYPE:
            for cmdTargetID, listOfCommands in self._chatCommands[markerType].iteritems():
                if not self._isAliveVehicle(cmdTargetID):
                    commands.sendClearChatCommandsFromTarget(cmdTargetID, markerType.name)

    def _isAliveVehicle(self, vehicleID):
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP and vehicleID:
            vehicleInfo = arenaDP.getVehicleInfo(vehicleID)
            if vehicleInfo:
                return vehicleInfo.isAlive()
        return False

    def _onAvatarBecomePlayer(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved += self._onVehicleMarkerRemoved
        self.battleCommunications.onChanged += self._onBattleCommunicationsSettingsChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def _onAvatarBecomeNonPlayer(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self._onVehicleMarkerRemoved
        self.battleCommunications.onChanged -= self._onBattleCommunicationsSettingsChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        return

    def _onVehicleMarkerRemoved(self, vehicleID):
        if self._markerInFocus is None or not self.sessionProvider.shared.chatCommands:
            return
        else:
            commands = self.sessionProvider.shared.chatCommands
            if self._markerInFocus.isFocused(vehicleID, MarkerType.VEHICLE_MARKER_TYPE):
                commands.sendCancelReplyChatCommand(self._markerInFocus.targetID, _ACTIONS.battleChatCommandFromActionID(self._markerInFocus.commandID).name)
            return

    def _getTargetIDForCommandName(self, commandName, cmd, allowDeadVehInfo=False):
        return self._getCommandCreatorVehID(cmd, allowDeadVehInfo) if commandName in (BATTLE_CHAT_COMMAND_NAMES.SOS,
         BATTLE_CHAT_COMMAND_NAMES.HELPME,
         BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
         BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
         BATTLE_CHAT_COMMAND_NAMES.THANKS) else cmd.getFirstTargetID()

    def _getUniqueCallbackID(self):
        self._callbackIDCounter += 1
        return self._callbackIDCounter

    def _removeActiveCommands(self):
        commands = self.sessionProvider.shared.chatCommands
        fbCtrl = self.sessionProvider.shared.feedback
        if self._markerInFocus:
            action = _ACTIONS.battleChatCommandFromActionID(self._markerInFocus.commandID)
            if action is None:
                _logger.debug('Action in removeActiveCommands was None, %s', self._markerInFocus.commandID)
            else:
                commands.sendCancelReplyChatCommand(self._markerInFocus.targetID, action.name)
                self._removeReplyContributionFromPlayer(avatar_getter.getPlayerVehicleID(), MarkerType.INVALID_MARKER_TYPE, -1)
            fbCtrl.setInFocusForPlayer(self._markerInFocus.targetID, self._markerInFocus.markerType, -1, MarkerType.INVALID_MARKER_TYPE, False)
            self._markerInFocus = None
        for markerType in self._chatCommands.keys():
            for targetIC in self._chatCommands[markerType].keys():
                for commandID in self._chatCommands[markerType][targetIC]:
                    self._tryRemovingCommandFromMarker(commandID, targetIC, forceRemove=True)

        return

    def _onCommandReceived(self, cmd):
        if cmd.getCommandType() != MESSENGER_COMMAND_TYPE.BATTLE:
            return
        else:
            controller = MessengerEntry.g_instance.gui.channelsCtrl.getController(cmd.getClientID())
            if controller is None:
                _logger.error('Controller not found %s', cmd)
                return
            if not controller.filterMessage(cmd):
                return
            if cmd.isServerCommand():
                self._onServerCommandReceived(cmd)
                return
            commandName = _ACTIONS.battleChatCommandFromActionID(cmd.getID()).name
            if commandName in _COMMAND_NAME_TRANSFORM_MARKER_TYPE or commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                self._handleRegularCommand(cmd)
            elif cmd.isReply():
                self._handleReply(cmd)
            elif cmd.isCancelReply():
                self._handleCancelReply(cmd)
            elif cmd.isClearChatCommand():
                self._handleClearChatCommands(cmd)
            return

    def _getCommandCreatorVehID(self, cmd, allowDeadVehInfo=False):
        result = None
        arenaDP = self.sessionProvider.getCtx().getArenaDP()
        if arenaDP is None:
            return result
        else:
            vehicleID = arenaDP.getVehIDBySessionID(cmd.getSenderID())
            isValidVehicle = False
            if vehicleID:
                vehicleInfo = arenaDP.getVehicleInfo(vehicleID)
                if vehicleInfo.isAlive() and not vehicleInfo.isObserver() or allowDeadVehInfo:
                    isValidVehicle = True
            return vehicleID if isValidVehicle else 0

    def _addCommandToList(self, commandID, commandName, commandCreatorID, commandTargetID, command, activeTime=_DEFAULT_ACTIVE_COMMAND_TIME):
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
        if markerType not in self._chatCommands:
            self._chatCommands[markerType] = dict()
        owners = []
        uniqueCBID = None
        if not command.isServerCommand():
            self._tryRemovalOfPreviousLocationCommands(commandCreatorID)
            if commandName in AUTOCOMMIT_COMMAND_NAMES:
                self._removeReplyContributionFromPlayer(commandCreatorID, markerType, commandTargetID)
            uniqueCBID = self._getUniqueCallbackID()
            self._delayer.delayCallback(uniqueCBID, activeTime, self._removeCommandMarkerCB, commandID, commandTargetID)
            if commandName in AUTOCOMMIT_COMMAND_NAMES:
                owners.append(commandCreatorID)
        if commandTargetID not in self._chatCommands[markerType]:
            self._chatCommands[markerType][commandTargetID] = OrderedDict()
        self._chatCommands[markerType][commandTargetID].update({commandID: AdvancedChatCommandData(command=command, commandCreatorVehID=commandCreatorID, callbackID=uniqueCBID, owners=owners)})
        if self.sessionProvider.shared.feedback:
            self.sessionProvider.shared.feedback.onCommandAdded(commandTargetID, markerType)
        updateCmdType = ChatCommandChange.CHAT_CMD_WAS_REPLIED if commandName in AUTOCOMMIT_COMMAND_NAMES else ChatCommandChange.CHAT_CMD_TRIGGERED
        self._chatCommandsUpdated(markerType, commandTargetID, commandID, commandCreatorID, updateCmdType)
        isTemporarySticky = command and not command.isInSilentMode() and command.isTemporarySticky() and not commandCreatorID == avatar_getter.getPlayerVehicleID()
        if isTemporarySticky:
            self._temporaryStickyCommands[commandID][commandTargetID] = (commandTargetID, markerType)
        if commandCreatorID == avatar_getter.getPlayerVehicleID() and commandName in AUTOCOMMIT_COMMAND_NAMES or isTemporarySticky:
            BigWorld.callback(0.1, partial(self._setInFocusCB, commandID, commandTargetID, markerType, commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys(), isTemporarySticky))
        return

    def _addPositiveMarkerAboveCreator(self, vehicleMarkerID):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.showActionMarker(vehicleMarkerID, vMarker=MARKER_ACTION_POSITIVE, mMarker=MARKER_ACTION_POSITIVE, isPermanent=False)

    def _handleMark3DPosition(self, commandTargetID, creatorVehicleID, commandID, commandName, commandDuration, cmd):
        if commandName == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE:
            self._addPositiveMarkerAboveCreator(creatorVehicleID)
        position = cmd.getMarkedPosition()
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
        commandData = self._chatCommands[markerType][commandTargetID][commandID]
        numberOfReplies = len(commandData.owners)
        isTargetForPlayer = avatar_getter.getPlayerVehicleID() in commandData.owners
        g_locationPointManager.addLocationPoint(position, commandTargetID, creatorVehicleID, commandID, commandDuration, None, numberOfReplies, isTargetForPlayer)
        return

    def _handleVehicleCommand(self, targetID, senderID, commandID, cmd):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl:
            return
        commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
        if targetID in self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE] and commandID in self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE][targetID]:
            commandData = self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE][targetID][commandID]
            numberOfReplies = len(commandData.owners)
            isTargetForPlayer = avatar_getter.getPlayerVehicleID() in commandData.owners
        else:
            numberOfReplies = 0
            isTargetForPlayer = False
        isPermanent = commandName not in (BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
         BATTLE_CHAT_COMMAND_NAMES.THANKS,
         BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
         BATTLE_CHAT_COMMAND_NAMES.CONFIRM,
         BATTLE_CHAT_COMMAND_NAMES.POSITIVE,
         BATTLE_CHAT_COMMAND_NAMES.SOS,
         BATTLE_CHAT_COMMAND_NAMES.HELPME)
        if cmd.isPrivate() and (cmd.isReceiver() or cmd.isSender()):
            vMarker = cmd.getVehMarker()
            if vMarker and senderID:
                feedbackCtrl.showActionMarker(senderID, vMarker, cmd.getVehMarker(), numberOfReplies, isTargetForPlayer, isPermanent=isPermanent)
                if cmd.isMsgOnMarker() and senderID:
                    message = cmd.messageOnMarker()
                    feedbackCtrl.showActionMessage(senderID, message, True)
        else:
            showReceiver = cmd.showMarkerForReceiver()
            recvMarker, senderMarker = cmd.getVehMarkers()
            if showReceiver:
                if commandName == BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY:
                    senderMarker = MARKER_ACTION_SUPPORTING_YOU if cmd.isReceiver() else MARKER_ACTION_POSITIVE
                    isPermanent = not cmd.isReceiver()
                if targetID:
                    feedbackCtrl.showActionMarker(targetID, recvMarker, recvMarker, numberOfReplies, isTargetForPlayer, isPermanent=isPermanent)
                if senderID:
                    feedbackCtrl.showActionMarker(senderID, senderMarker, senderMarker, 0, False, False)
            elif senderID:
                feedbackCtrl.showActionMarker(senderID, recvMarker, recvMarker, numberOfReplies, isTargetForPlayer, isPermanent=isPermanent)
            if cmd.isMsgOnMarker() and senderID:
                message = cmd.messageOnMarker()
                feedbackCtrl.showActionMessage(senderID, message, False)

    def _handleTargetPointCommand(self, targetID, senderID, commandID, cmdName, cmd):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl:
            return
        if targetID in self._chatCommands[MarkerType.TARGET_POINT_MARKER_TYPE] and commandID in self._chatCommands[MarkerType.TARGET_POINT_MARKER_TYPE][targetID]:
            commandData = self._chatCommands[MarkerType.TARGET_POINT_MARKER_TYPE][targetID][commandID]
            numberOfReplies = len(commandData.owners)
        else:
            numberOfReplies = 0
        if cmdName in (BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT,):
            self._addPositiveMarkerAboveCreator(senderID)
        self._notifyReplyCommandUpdate(targetID, senderID, commandID, 0, numberOfReplies)

    def _handleBaseCommand(self, commandName, cmdCreatorID, cmdID, cmdTargetID):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl or feedbackCtrl is None:
            return
        else:
            if commandName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE):
                self._addPositiveMarkerAboveCreator(cmdCreatorID)
            feedbackCtrl.onActionAddedToMarker(cmdCreatorID, cmdID, MarkerType.BASE_MARKER_TYPE, cmdTargetID)
            return

    def _handleObjectiveCommand(self, commandName, cmdCreatorID, cmd):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl or feedbackCtrl is None:
            return
        else:
            if commandName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE):
                self._addPositiveMarkerAboveCreator(cmdCreatorID)
            feedbackCtrl.markObjectiveOnMinimap(cmdCreatorID, cmd.getMarkedObjective(), commandName)
            return

    def _handleRegularCommand(self, cmd):
        cmdID = cmd.getID()
        cmdName = _ACTIONS.battleChatCommandFromActionID(cmdID).name
        cmdCreatorID = self._getCommandCreatorVehID(cmd)
        cmdTargetID = self._getTargetIDForCommandName(cmdName, cmd)
        cmdDuration = _DEFAULT_ACTIVE_COMMAND_TIME if cmdName != BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA else _DEFAULT_SPG_AREA_COMMAND_TIME
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[cmdName]
        if cmdName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY, BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, BATTLE_CHAT_COMMAND_NAMES.SOS):
            arenaDP = self.sessionProvider.getArenaDP()
            if arenaDP is None:
                return
            if cmdTargetID:
                vehicleInfo = arenaDP.getVehicleInfo(cmdTargetID)
                if vehicleInfo and not vehicleInfo.isAlive():
                    return
        if markerType in self._chatCommands and cmdTargetID in self._chatCommands[markerType] and cmdID in self._chatCommands[markerType][cmdTargetID]:
            if cmdName in AUTOCOMMIT_COMMAND_NAMES:
                self._addReplyToCommandList(cmdCreatorID, cmdTargetID, cmdID)
            return
        else:
            if cmdName == BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY and MarkerType.VEHICLE_MARKER_TYPE in self._chatCommands and cmdTargetID in self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE]:
                activeCommandIDOnTarget = self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE][cmdTargetID].keys()
                helpCommandID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.HELPME].id
                sosCommandID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.SOS].id
                if helpCommandID in activeCommandIDOnTarget or sosCommandID in activeCommandIDOnTarget:
                    activeHelpID = helpCommandID if helpCommandID in activeCommandIDOnTarget else sosCommandID
                    self._tryRemovingCommandFromMarker(activeHelpID, cmdTargetID)
                    self._addCommandToList(cmdID, cmdName, cmdCreatorID, cmdTargetID, cmd, cmdDuration)
                elif cmdID in activeCommandIDOnTarget:
                    self._addReplyToCommandList(cmdCreatorID, cmdTargetID, cmdID)
            elif cmdName not in (BATTLE_CHAT_COMMAND_NAMES.CONFIRM, BATTLE_CHAT_COMMAND_NAMES.POSITIVE):
                self._addCommandToList(cmdID, cmdName, cmdCreatorID, cmdTargetID, cmd, cmdDuration)
            if cmd.isLocationRelatedCommand():
                self._handleMark3DPosition(cmdTargetID, cmdCreatorID, cmdID, cmdName, cmdDuration, cmd)
            elif cmd.isBaseRelatedCommand():
                self._handleBaseCommand(cmdName, cmdCreatorID, cmdID, cmdTargetID)
            elif cmd.isVehicleRelatedCommand():
                self._handleVehicleCommand(cmdTargetID, cmdCreatorID, cmdID, cmd)
            elif cmd.isMarkedObjective():
                self._handleObjectiveCommand(cmdName, cmdCreatorID, cmd)
            elif cmd.isTargetPointCommand():
                self._handleTargetPointCommand(cmdTargetID, cmdCreatorID, cmdID, cmdName, cmd)
            return

    def _addReplyToCommandList(self, replierVehicleID, targetID, repliedToCommandID):
        repliedToActionName = _ACTIONS.battleChatCommandFromActionID(repliedToCommandID).name
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[repliedToActionName]
        if markerType not in self._chatCommands or targetID not in self._chatCommands[markerType] or repliedToCommandID not in self._chatCommands[markerType][targetID]:
            _logger.error('Trying to add reply to non-existing element of markerType(%s), targetID(%d) and repliedToCommandID(%d)', markerType.name, targetID, repliedToCommandID)
            return
        self._removeReplyContributionFromPlayer(replierVehicleID, markerType, targetID)
        commandData = self._chatCommands[markerType][targetID][repliedToCommandID]
        oldOwnerCount = len(commandData.owners)
        if replierVehicleID not in commandData.owners:
            commandData.owners.append(replierVehicleID)
        self._notifyReplyCommandUpdate(targetID, replierVehicleID, repliedToCommandID, oldOwnerCount, len(commandData.owners))
        self._chatCommandsUpdated(markerType, targetID, repliedToCommandID, replierVehicleID, ChatCommandChange.CHAT_CMD_WAS_REPLIED)
        if replierVehicleID == avatar_getter.getPlayerVehicleID():
            self._setFocusedOnMarker(targetID, markerType, repliedToCommandID)

    def _setFocusedOnMarker(self, targetID, markerType, repliedToCommandID):
        self._checkTemporarySticky(repliedToCommandID, targetID)
        oldID = 0
        oldMarkerType = MarkerType.INVALID_MARKER_TYPE
        if self._markerInFocus is not None:
            oldID = self._markerInFocus.targetID
            oldMarkerType = self._markerInFocus.markerType
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.setInFocusForPlayer(oldID, oldMarkerType, targetID, markerType, False)
        if targetID == 0 and markerType == MarkerType.INVALID_MARKER_TYPE:
            self._markerInFocus = None
        else:
            self._markerInFocus = MarkerInFocus(commandID=repliedToCommandID, targetID=targetID, markerType=markerType)
        return

    def _getCorrectReplyCommandName(self, targetID, replyActionName):
        targetMarkerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[replyActionName]
        if targetMarkerType not in self._chatCommands or targetID not in self._chatCommands[targetMarkerType]:
            return replyActionName
        commands = self._chatCommands[targetMarkerType][targetID]
        activeActionWithReplies = replyActionName
        for commandID, commandData in ((k, commands[k]) for k in reversed(commands)):
            commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
            if commandData.owners:
                activeActionWithReplies = commandName

        return activeActionWithReplies

    def _handleReply(self, cmd):
        replierVehicleID = self._getCommandCreatorVehID(cmd)
        targetID = cmd.getFirstTargetID()
        replyToActionName = cmd.getCommandData()['strArg1']
        if replierVehicleID:
            self._addPositiveMarkerAboveCreator(replierVehicleID)
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[replyToActionName]
        replyToActionName = self._getCorrectReplyCommandName(targetID, replyToActionName)
        repliedToActionID = BATTLE_CHAT_COMMANDS_BY_NAMES[replyToActionName].id
        isAlreadyAdded = markerType in self._chatCommands and targetID in self._chatCommands[markerType] and repliedToActionID in self._chatCommands[markerType][targetID]
        avatar_getter.getPlayerVehicleID()
        wasMuted = False
        if not isAlreadyAdded and targetID in g_mutedMessages:
            wasMuted = True
        if not isAlreadyAdded and wasMuted:
            if replyToActionName in _CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_VEHICLES:
                protoData = {'int32Arg1': targetID,
                 'int64Arg1': replierVehicleID,
                 'floatArg1': 0.0,
                 'strArg1': '',
                 'strArg2': ''}
                newAction = _CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_VEHICLES[replyToActionName]
                actionID = BATTLE_CHAT_COMMANDS_BY_NAMES[newAction].id
                command = BattleCommandFactory.createByAction(actionID=actionID, args=protoData)
                self._handleRegularCommand(command)
            elif replyToActionName == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE or replyToActionName in _CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_BASES:
                cmdGoingThere = g_mutedMessages.pop(targetID)
                protoData = cmdGoingThere.getCommandData()
                protoData['int64Arg1'] = replierVehicleID
                if replyToActionName == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE:
                    actionID = BATTLE_CHAT_COMMANDS_BY_NAMES[replyToActionName].id
                else:
                    newAction = _CHAT_CMD_CREATE_IF_NO_ORIGINAL_COMMAND_BASES[replyToActionName]
                    actionID = BATTLE_CHAT_COMMANDS_BY_NAMES[newAction].id
                command = BattleCommandFactory.createByAction(actionID=actionID, args=protoData)
                self._handleRegularCommand(command)
            else:
                _logger.debug('Reply to action name, no action needed (%s)', replyToActionName)
        else:
            self._addReplyToCommandList(replierVehicleID, targetID, repliedToActionID)

    def _handleCancelReply(self, cmd):
        playerVehicleID = self._getCommandCreatorVehID(cmd)
        self._removeReplyContributionFromPlayer(playerVehicleID, MarkerType.INVALID_MARKER_TYPE, -1)

    def _handleClearChatCommands(self, cmd):
        targetID = cmd.getFirstTargetID()
        markerTypeName = cmd.getCommandData()['strArg1']
        markerType = MarkerType.getEnumValueByName(markerTypeName)
        removeList = list()
        if markerType is not None and markerType in self._chatCommands:
            if targetID in self._chatCommands[markerType]:
                for commandID in self._chatCommands[markerType][targetID]:
                    commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
                    currentTargetID = self._getTargetIDForCommandName(commandName, cmd, True)
                    if currentTargetID not in self._chatCommands[markerType]:
                        continue
                    if commandID in self._chatCommands[markerType][currentTargetID]:
                        removeList.append((commandID, currentTargetID))
                        chatCommandData = self._chatCommands[markerType][currentTargetID][commandID]
                        if chatCommandData.owners:
                            for replier in chatCommandData.owners:
                                self._chatCommandsUpdated(markerType, currentTargetID, commandID, replier, ChatCommandChange.CHAT_CMD_WAS_REMOVED)

                        elif commandName == BATTLE_CHAT_COMMAND_NAMES.SOS:
                            self._chatCommandsUpdated(markerType, currentTargetID, commandID, currentTargetID, ChatCommandChange.CHAT_CMD_WAS_REMOVED)

            else:
                self._removeReplyContributionFromPlayer(targetID, MarkerType.INVALID_MARKER_TYPE, -1)
        for commandID, tID in removeList:
            self._tryRemovingCommandFromMarker(commandID, tID, True)

        return

    def _removeReplyContributionFromPlayer(self, replierVehID, newTargetType, newTargetID):
        updatedCommand = None
        checkForRemovalOfCommandFromMarker = False
        for markerType in self._chatCommands:
            for targetID in self._chatCommands[markerType]:
                for commandID, commandData in self._chatCommands[markerType][targetID].iteritems():
                    isSameCommand = targetID == newTargetID and newTargetType == markerType
                    if not isSameCommand and replierVehID in commandData.owners:
                        oldOwnerCount = len(commandData.owners)
                        self._chatCommandsUpdated(markerType, targetID, commandID, replierVehID, ChatCommandChange.CHAT_CMD_WAS_REMOVED)
                        commandData.owners.remove(replierVehID)
                        updatedCommand = (commandID, targetID)
                        self._notifyReplyCommandUpdate(targetID, replierVehID, commandID, oldOwnerCount, len(commandData.owners))
                        if not commandData.owners and not commandData.command.isServerCommand():
                            checkForRemovalOfCommandFromMarker = True
                        break

        if updatedCommand is not None:
            cmdID, cmdTargetID = updatedCommand
            commandName = _ACTIONS.battleChatCommandFromActionID(cmdID).name
            if replierVehID == avatar_getter.getPlayerVehicleID() and self._markerInFocus and self._markerInFocus.isFocused(cmdTargetID, _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]):
                self._setFocusedOnMarker(-1, MarkerType.INVALID_MARKER_TYPE, -1)
            if checkForRemovalOfCommandFromMarker:
                self._tryRemovingCommandFromMarker(cmdID, cmdTargetID, commandName in AUTOCOMMIT_COMMAND_NAMES)
        return

    def _notifyReplyCommandUpdate(self, targetID, replierVehicleID, commandID, oldReplyCount, newReplycount):
        commandDesr = _ACTIONS.battleChatCommandFromActionID(commandID)
        if commandDesr is None or commandDesr.name not in _COMMAND_NAME_TRANSFORM_MARKER_TYPE or not self.sessionProvider.shared.feedback:
            return
        else:
            self.sessionProvider.shared.feedback.onReplyToCommand(targetID, replierVehicleID, _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandDesr.name], oldReplyCount, newReplycount)
            return

    def _me_onBattleUserActionReceived(self, actionID, user):
        if not user.isIgnored():
            return
        else:
            if actionID in (USER_ACTION_ID.IGNORED_ADDED,
             USER_ACTION_ID.IGNORED_REMOVED,
             USER_ACTION_ID.TMP_IGNORED_ADDED,
             USER_ACTION_ID.TMP_IGNORED_REMOVED,
             USER_ACTION_ID.MUTE_SET,
             USER_ACTION_ID.MUTE_UNSET):
                avatarSessionID = user.getID()
                arenaDP = self.sessionProvider.getCtx().getArenaDP()
                if arenaDP is None:
                    return
                vehicleID = arenaDP.getVehIDBySessionID(avatarSessionID)
                self._removeReplyContributionFromPlayer(vehicleID, MarkerType.INVALID_MARKER_TYPE, -1)
            return

    def _onBattleCommunicationsSettingsChanged(self):
        battleCommunicationEnabled = self.battleCommunications.isEnabled
        if battleCommunicationEnabled is None:
            return
        else:
            _logger.debug('IBC settings changed, adding/removing listeners.')
            if battleCommunicationEnabled is True:
                self._addEventListeners()
            else:
                self._removeActiveCommands()
                self._removeEventListenersAndClear()
            self._isEnabled = battleCommunicationEnabled
            return

    def _checkTemporarySticky(self, commandID, targetID):
        if commandID not in self._temporaryStickyCommands or targetID not in self._temporaryStickyCommands[commandID]:
            return
        commandTargetID, markerType = self._temporaryStickyCommands[commandID].pop(targetID)
        isOneShot = _ACTIONS.battleChatCommandFromActionID(commandID).name in ONE_SHOT_COMMANDS_TO_REPLIES.keys()
        focusedTargetID = 0
        focusedMarkerType = ''
        if self._markerInFocus and self._markerInFocus.isFocused(commandTargetID, markerType):
            focusedTargetID = self._markerInFocus.targetID
            focusedMarkerType = self._markerInFocus.markerType
        fbCtrl = self.sessionProvider.shared.feedback
        if fbCtrl and not (focusedMarkerType == markerType and commandTargetID == focusedTargetID):
            fbCtrl.setInFocusForPlayer(commandTargetID, markerType, -1, MarkerType.INVALID_MARKER_TYPE, isOneShot)
        if not self._temporaryStickyCommands[commandID]:
            self._temporaryStickyCommands.pop(commandID)

    def _tryRemovalOfPreviousLocationCommands(self, ucmdCreatorID):
        removeCommandsList = list()
        for markerType in self._chatCommands:
            for targetID in self._chatCommands[markerType]:
                for commandID, commandData in self._chatCommands[markerType][targetID].iteritems():
                    if commandData.command.isLocationRelatedCommand() and ucmdCreatorID == commandData.commandCreatorVehID and not commandData.owners and commandID != BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.GOING_THERE].id:
                        removeCommandsList.append((commandID, targetID))

        if removeCommandsList:
            for removeCommandID, removeTargetID in removeCommandsList:
                self._checkTemporarySticky(removeCommandID, removeTargetID)
                self._tryRemovingCommandFromMarker(removeCommandID, removeTargetID, True)

    def _tryRemovingCommandFromMarker(self, commandID, targetID, forceRemove=False):
        if _ACTIONS.battleChatCommandFromActionID(commandID) is None:
            return
        else:
            commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
            markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
            if commandID in self._chatCommands[markerType][targetID]:
                commandData = self._chatCommands[markerType][targetID][commandID]
                if forceRemove or not self._delayer.hasDelayedCallbackID(commandData.callbackID) and not commandData.owners:
                    self._delayer.stopCallback(commandData.callbackID)
                    self._chatCommands[markerType][targetID].pop(commandID)
                    wasLastCommandForTarget = not self._chatCommands[markerType][targetID]
                    if wasLastCommandForTarget:
                        self._chatCommands[markerType].pop(targetID)
                    if wasLastCommandForTarget:
                        feedbackCtrl = self.sessionProvider.shared.feedback
                        if feedbackCtrl:
                            feedbackCtrl.onCommandRemoved(targetID, markerType)
            return

    def _setInFocusCB(self, commandID, commandTargetID, markerType, isOneShot, isTemporary):
        if isTemporary:
            feedbackCtrl = self.sessionProvider.shared.feedback
            if feedbackCtrl:
                feedbackCtrl.setInFocusForPlayer(-1, MarkerType.INVALID_MARKER_TYPE, commandTargetID, markerType, isOneShot)
        else:
            self._setFocusedOnMarker(commandTargetID, markerType, commandID)

    def _removeCommandMarkerCB(self, removeCommandID, removeCommandTargetID):
        if _ACTIONS.battleChatCommandFromActionID(removeCommandID) is None:
            _logger.warning('Command with ID %s was not found.', removeCommandID)
            return
        else:
            commandName = _ACTIONS.battleChatCommandFromActionID(removeCommandID).name
            markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
            commandData = self._chatCommands.get(markerType, {}).get(removeCommandTargetID, {}).get(removeCommandID, None)
            if not commandData:
                return
            self._delayer.stopCallback(commandData.callbackID)
            self._checkTemporarySticky(removeCommandID, removeCommandTargetID)
            self._tryRemovingCommandFromMarker(removeCommandID, removeCommandTargetID)
            return

    @classmethod
    def _isLastPrebattleMarkerOwner(cls, cmdMarkerType, cmdID, commandData):
        return cls._isPrebattleWaypoint(cmdMarkerType, cmdID) and len(commandData.owners) == 1

    @staticmethod
    def _isPrebattleWaypoint(cmdMarkerType, cmdID):
        return cmdMarkerType == MarkerType.LOCATION_MARKER_TYPE and cmdID == BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT].id
