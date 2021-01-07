# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/advanced_chat_component.py
import logging
from collections import OrderedDict, defaultdict, namedtuple
from functools import partial
from enum import Enum
import BigWorld
import Math
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_component_system.client_arena_component_system import ClientArenaComponent
from battleground.location_point_manager import g_locationPointManager
from chat_commands_consts import ReplyState, _COMMAND_NAME_TRANSFORM_MARKER_TYPE, BATTLE_CHAT_COMMAND_NAMES, _DEFAULT_ACTIVE_COMMAND_TIME, _DEFAULT_SPG_AREA_COMMAND_TIME, MarkerType, ONE_SHOT_COMMANDS_TO_REPLIES, COMMAND_RESPONDING_MAPPING
from constants import ARENA_PERIOD, ARENA_BONUS_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency, i18n, CallbackDelayer
from messenger import MessengerEntry
from messenger.m_constants import MESSENGER_COMMAND_TYPE, USER_ACTION_ID
from messenger.proto.bw_chat2.battle_chat_cmd import BattleCommandFactory, AUTOCOMMIT_COMMAND_NAMES
from messenger.proto.bw_chat2.chat_handlers import g_mutedMessages
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS_BY_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.battle_session import IBattleSessionProvider
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
    settingsCore = dependency.descriptor(ISettingsCore)
    settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self, componentSystem):
        super(AdvancedChatComponent, self).__init__(componentSystem)
        self._chatCommands = defaultdict(dict)
        self.__delayer = CallbackDelayer.CallbacksSetByID()
        self.__callbackIDCounter = 0
        self.__markerInFocus = None
        self.__temporaryStickyCommands = defaultdict(dict)
        self.__isEnabled = None
        return

    def activate(self):
        super(AdvancedChatComponent, self).activate()
        if self.settingsCore:
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        if self.settingsCache:
            if not self.settingsCache.settings.isSynced():
                self.settingsCache.onSyncCompleted += self.__onSettingsReady
            else:
                self.__isEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
        if not self.__isEnabled:
            return
        self.__addEventListeners()

    def deactivate(self):
        super(AdvancedChatComponent, self).deactivate()
        if self.settingsCore:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        if self.__isEnabled:
            self.__removeEventListenersAndClear()
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved

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
                if targetID in commandData.owners and self.__delayer.hasDelayedCallbackID(commandData.callbackID):
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

    def __addEventListeners(self):
        g_messengerEvents.channels.onCommandReceived += self.__onCommandReceived
        g_messengerEvents.users.onBattleUserActionReceived += self.__me_onBattleUserActionReceived
        componentSystem = self._componentSystem()
        if componentSystem is not None:
            arena = componentSystem.arena()
            if arena is not None:
                arena.onVehicleKilled += self.__onArenaVehicleKilled
                if arena.bonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
                    self.__addEpicBattleEventListeners()
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived += self.__onCommandReceived
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def __addEpicBattleEventListeners(self):
        if self._componentSystem() is None:
            return
        else:
            sectorBaseComponent = self._componentSystem().sectorBaseComponent
            if sectorBaseComponent is not None:
                sectorBaseComponent.onSectorBaseCaptured += self.__onSectorBaseCaptured
            destructibleComponent = self._componentSystem().destructibleEntityComponent
            if destructibleComponent is not None:
                destructibleComponent.onDestructibleEntityStateChanged += self.__onDestructibleEntityStateChanged
            return

    def __removeEventListenersAndClear(self):
        g_messengerEvents.channels.onCommandReceived -= self.__onCommandReceived
        g_messengerEvents.users.onBattleUserActionReceived -= self.__me_onBattleUserActionReceived
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        componentSystem = self._componentSystem()
        if componentSystem is not None:
            arena = componentSystem.arena()
            if arena is not None:
                arena.onVehicleKilled -= self.__onArenaVehicleKilled
                if arena.bonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
                    self.__removeEpicBattleEventsListeners()
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__onCommandReceived
        self._chatCommands.clear()
        self.__delayer.clear()
        self.__temporaryStickyCommands.clear()
        self.__markerInFocus = None
        return

    def __removeEpicBattleEventsListeners(self):
        if self._componentSystem() is None:
            return
        else:
            sectorBaseComponent = self._componentSystem().sectorBaseComponent
            if sectorBaseComponent is not None:
                sectorBaseComponent.onSectorBaseCaptured -= self.__onSectorBaseCaptured
            destructibleComponent = self._componentSystem().destructibleEntityComponent
            if destructibleComponent is not None:
                destructibleComponent.onDestructibleEntityStateChanged -= self.__onDestructibleEntityStateChanged
            return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING and avatar_getter.isObserver():
            self.__removeActiveCommands()

    def __onArenaPeriodChange(self, period, endTime, *_):
        if period == ARENA_PERIOD.PREBATTLE:
            self.__addPrebattleWaypoints(endTime - BigWorld.serverTime())
        elif period == ARENA_PERIOD.BATTLE:
            self.__removePrebattleWaypoints()

    def __addPrebattleWaypoints(self, remainingPrebattleTime):
        if not hasattr(BigWorld.player(), 'arenaExtraData'):
            _logger.info('PrebattleMarkers: no arenaExtraData found for Avatar')
            return
        if self.__isEnabled is False:
            _logger.info('PrebattleMarkers: no IBC enabled.')
            return
        PREBATTLEMARKER_EXTRA_DATA = 'prebattleMarkers'
        if PREBATTLEMARKER_EXTRA_DATA not in BigWorld.player().arenaExtraData:
            _logger.info('PrebattleMarkers:  PrebattleMarker extra data not found (no markers set for this map?)')
            return
        generatedUniqueID = 0
        commandName = BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT
        commandID = BATTLE_CHAT_COMMANDS_BY_NAMES[commandName].id
        commandCreatorID = -10
        if not BigWorld.player().userSeesWorld():
            g_playerEvents.onAvatarReady += self.__onAvatarReady
            return
        for item in BigWorld.player().arenaExtraData[PREBATTLEMARKER_EXTRA_DATA]:
            name = item['locationName']
            team = item['teams']
            position = item['position']
            playerTeam = BigWorld.player().team
            if team != 'both' and team != 'team%s' % playerTeam:
                continue
            protoData = {'int32Arg1': generatedUniqueID,
             'int64Arg1': commandCreatorID,
             'floatArg1': 0.0,
             'strArg1': '',
             'strArg2': ''}
            actionID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT].id
            command = BattleCommandFactory.createByAction(actionID=actionID, args=protoData)
            localizedName = i18n.makeString(name)
            position = Math.Vector3(position)
            pos = Math.Vector3(position.x, position.y, position.z)
            self.__addCommandToList(commandID, commandName, commandCreatorID, generatedUniqueID, command, remainingPrebattleTime)
            g_locationPointManager.addLocationPoint(pos, generatedUniqueID, commandCreatorID, commandID, remainingPrebattleTime, localizedName, 0, False)
            generatedUniqueID += 1
            commandCreatorID -= 1

    def __removePrebattleWaypoints(self):
        if MarkerType.LOCATION_MARKER_TYPE not in self._chatCommands:
            return
        removeList = list()
        prebattleCmdID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT].id
        for locMarkerID in self._chatCommands[MarkerType.LOCATION_MARKER_TYPE].keys():
            if prebattleCmdID in self._chatCommands[MarkerType.LOCATION_MARKER_TYPE][locMarkerID] and not self._chatCommands[MarkerType.LOCATION_MARKER_TYPE][locMarkerID][prebattleCmdID].owners:
                removeList.append((prebattleCmdID, locMarkerID))

        for removeElement in removeList:
            cmdID, targetID = removeElement
            self.__tryRemovingCommandFromMarker(cmdID, targetID, True)

    def __chatCommandsUpdated(self, cmdMarkerType, cmdTargetID, cmdID, senderVehID, typeOfUpdate):
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
                if playerVehID in commandData.owners or playerVehID == cmdTargetID:
                    chatStats = {senderVehID: (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)}
                    if isPlayerSender:
                        chatStats = dict(((vehID, (EMPTY_STATE, EMPTY_CHAT_CMD_FLAG)) for vehID in commandData.owners))
                        if cmdMarkerType == MarkerType.VEHICLE_MARKER_TYPE:
                            chatStats[cmdTargetID] = (EMPTY_STATE, TARGET_CHAT_CMD_FLAG)
                    elif cmdMarkerType == MarkerType.VEHICLE_MARKER_TYPE and self.__markerInFocus is not None and senderVehID == self.__markerInFocus.targetID:
                        actionMarker = _ACTIONS.battleChatCommandFromActionID(self.__markerInFocus.commandID).vehMarker
                        chatStats[senderVehID] = (actionMarker, TARGET_CHAT_CMD_FLAG)
            elif typeOfUpdate in (ChatCommandChange.CHAT_CMD_WAS_REPLIED, ChatCommandChange.CHAT_CMD_TRIGGERED):
                actionMarker = _ACTIONS.battleChatCommandFromActionID(cmdID).vehMarker
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

    def __onDestructibleEntityStateChanged(self, entityID):
        if self.__markerInFocus is None:
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
                self.__removeActualTargetIfDestroyed(commands, playerVehID, entityID, MarkerType.HEADQUARTER_MARKER_TYPE)
            return

    def __onSectorBaseCaptured(self, baseId, _):
        sectorBaseComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            playerVehID = avatar_getter.getPlayerVehicleID()
            commands = self.sessionProvider.shared.chatCommands
            self.__removeActualTargetIfDestroyed(commands, playerVehID, baseId, MarkerType.BASE_MARKER_TYPE)
        return

    def __onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason):
        if self.__markerInFocus is None or not self.sessionProvider.shared.chatCommands:
            return
        else:
            playerVehID = avatar_getter.getPlayerVehicleID()
            commands = self.sessionProvider.shared.chatCommands
            self.__removeActualTargetIfDestroyed(commands, playerVehID, targetID, MarkerType.VEHICLE_MARKER_TYPE)
            if playerVehID == targetID:
                commands.sendClearChatCommandsFromTarget(targetID, self.__markerInFocus.markerType.name)
            return

    def __removeActualTargetIfDestroyed(self, commands, playerVehID, targetID, markerType):
        if self.__markerInFocus is None:
            return
        else:
            if self.__markerInFocus.isFocused(targetID, markerType):
                listOfCommands = self._chatCommands[markerType][self.__markerInFocus.targetID]
                for _, commandData in listOfCommands.iteritems():
                    if playerVehID == commandData.commandCreatorVehID or playerVehID in commandData.owners:
                        commands.sendClearChatCommandsFromTarget(targetID, markerType.name)

            return

    def __onAvatarBecomePlayer(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved += self.__onVehicleMarkerRemoved
        if self.settingsCore:
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def __onAvatarBecomeNonPlayer(self):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.onVehicleMarkerRemoved -= self.__onVehicleMarkerRemoved
        if self.settingsCore:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    def __onAvatarReady(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena.period == ARENA_PERIOD.PREBATTLE:
            self.__addPrebattleWaypoints(arena.periodEndTime - BigWorld.serverTime())
        g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def __onVehicleMarkerRemoved(self, vehicleID):
        if self.__markerInFocus is None or not self.sessionProvider.shared.chatCommands:
            return
        else:
            commands = self.sessionProvider.shared.chatCommands
            if self.__markerInFocus.isFocused(vehicleID, MarkerType.VEHICLE_MARKER_TYPE):
                commands.sendCancelReplyChatCommand(self.__markerInFocus.targetID, _ACTIONS.battleChatCommandFromActionID(self.__markerInFocus.commandID).name)
            return

    def __getTargetIDForCommandName(self, commandName, cmd, allowDeadVehInfo=False):
        return self.__getCommandCreatorVehID(cmd, allowDeadVehInfo) if commandName in (BATTLE_CHAT_COMMAND_NAMES.SOS,
         BATTLE_CHAT_COMMAND_NAMES.HELPME,
         BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
         BATTLE_CHAT_COMMAND_NAMES.TURNBACK,
         BATTLE_CHAT_COMMAND_NAMES.THANKS) else cmd.getFirstTargetID()

    def __getUniqueCallbackID(self):
        self.__callbackIDCounter += 1
        return self.__callbackIDCounter

    def __removeActiveCommands(self):
        commands = self.sessionProvider.shared.chatCommands
        fbCtrl = self.sessionProvider.shared.feedback
        if self.__markerInFocus:
            action = _ACTIONS.battleChatCommandFromActionID(self.__markerInFocus.commandID)
            if action is None:
                _logger.debug('Action in removeActiveCommands was None, %s', self.__markerInFocus.commandID)
            else:
                commands.sendCancelReplyChatCommand(self.__markerInFocus.targetID, action.name)
                self.__removeReplyContributionFromPlayer(avatar_getter.getPlayerVehicleID(), MarkerType.INVALID_MARKER_TYPE, -1)
            fbCtrl.setInFocusForPlayer(self.__markerInFocus.targetID, self.__markerInFocus.markerType, -1, MarkerType.INVALID_MARKER_TYPE, False)
            self.__markerInFocus = None
        for markerType in self._chatCommands.keys():
            for targetIC in self._chatCommands[markerType].keys():
                for commandID in self._chatCommands[markerType][targetIC]:
                    self.__tryRemovingCommandFromMarker(commandID, targetIC, forceRemove=True)

        return

    def __onCommandReceived(self, cmd):
        if cmd.getCommandType() != MESSENGER_COMMAND_TYPE.BATTLE:
            return
        else:
            controller = MessengerEntry.g_instance.gui.channelsCtrl.getController(cmd.getClientID())
            if controller is None:
                _logger.error('Controller not found %s', cmd)
                return
            if not controller.filterMessage(cmd):
                return
            commandName = _ACTIONS.battleChatCommandFromActionID(cmd.getID()).name
            if commandName in _COMMAND_NAME_TRANSFORM_MARKER_TYPE or commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                self.__handleRegularCommand(cmd)
            elif cmd.isReply():
                self.__handleReply(cmd)
            elif cmd.isCancelReply():
                self.__handleCancelReply(cmd)
            elif cmd.isClearChatCommand():
                self.__handleClearChatCommands(cmd)
            return

    def __getCommandCreatorVehID(self, cmd, allowDeadVehInfo=False):
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
            if not isValidVehicle:
                _logger.warning('__getCommandCreatorVehID: Vehicle state is invalid - using senderID')
            return vehicleID if isValidVehicle else 0

    def __addCommandToList(self, commandID, commandName, commandCreatorID, commandTargetID, command, activeTime=_DEFAULT_ACTIVE_COMMAND_TIME):
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
        if markerType not in self._chatCommands:
            self._chatCommands[markerType] = dict()
        self.__tryRemovalOfPreviousLocationCommands(commandCreatorID)
        if commandName in AUTOCOMMIT_COMMAND_NAMES:
            self.__removeReplyContributionFromPlayer(commandCreatorID, markerType, commandTargetID)
        uniqueCBID = self.__getUniqueCallbackID()
        self.__delayer.delayCallback(uniqueCBID, activeTime, self.__removeCommandMarkerCB, commandID, commandTargetID)
        if commandTargetID not in self._chatCommands[markerType]:
            self._chatCommands[markerType][commandTargetID] = OrderedDict()
        owners = []
        if commandName in AUTOCOMMIT_COMMAND_NAMES:
            owners.append(commandCreatorID)
        self._chatCommands[markerType][commandTargetID].update({commandID: AdvancedChatCommandData(command=command, commandCreatorVehID=commandCreatorID, callbackID=uniqueCBID, owners=owners)})
        if self.sessionProvider.shared.feedback:
            self.sessionProvider.shared.feedback.onCommandAdded(commandTargetID, markerType)
        updateCmdType = ChatCommandChange.CHAT_CMD_WAS_REPLIED if commandName in AUTOCOMMIT_COMMAND_NAMES else ChatCommandChange.CHAT_CMD_TRIGGERED
        self.__chatCommandsUpdated(markerType, commandTargetID, commandID, commandCreatorID, updateCmdType)
        isTemporarySticky = command and not command.isInSilentMode() and command.isTemporarySticky() and not commandCreatorID == avatar_getter.getPlayerVehicleID()
        if isTemporarySticky:
            self.__temporaryStickyCommands[commandID][commandTargetID] = (commandTargetID, markerType)
        if commandCreatorID == avatar_getter.getPlayerVehicleID() and commandName in AUTOCOMMIT_COMMAND_NAMES or isTemporarySticky:
            BigWorld.callback(0.1, partial(self.__setInFocusCB, commandID, commandTargetID, markerType, commandName in ONE_SHOT_COMMANDS_TO_REPLIES.keys(), isTemporarySticky))

    def __addPositiveMarkerAboveCreator(self, vehicleMarkerID):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.showActionMarker(vehicleMarkerID, vMarker=MARKER_ACTION_POSITIVE, mMarker=MARKER_ACTION_POSITIVE, isPermanent=False)

    def __handleMark3DPosition(self, commandTargetID, creatorVehicleID, commandID, commandName, commandDuration, cmd):
        if commandName == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE:
            self.__addPositiveMarkerAboveCreator(creatorVehicleID)
        position = cmd.getMarkedPosition()
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
        commandData = self._chatCommands[markerType][commandTargetID][commandID]
        numberOfReplies = len(commandData.owners)
        isTargetForPlayer = avatar_getter.getPlayerVehicleID() in commandData.owners
        g_locationPointManager.addLocationPoint(position, commandTargetID, creatorVehicleID, commandID, commandDuration, None, numberOfReplies, isTargetForPlayer)
        return

    def __handleVehicleCommand(self, targetID, senderID, commandID, cmd):
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

    def __handleBaseCommand(self, commandName, cmdCreatorID, cmdID, cmdTargetID):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl or feedbackCtrl is None:
            return
        else:
            if commandName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE):
                self.__addPositiveMarkerAboveCreator(cmdCreatorID)
            feedbackCtrl.onActionAddedToMarker(cmdCreatorID, cmdID, MarkerType.BASE_MARKER_TYPE, cmdTargetID)
            return

    def __handleObjectiveCommand(self, commandName, cmdCreatorID, cmd):
        feedbackCtrl = self.sessionProvider.shared.feedback
        if not feedbackCtrl or feedbackCtrl is None:
            return
        else:
            if commandName in (BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE):
                self.__addPositiveMarkerAboveCreator(cmdCreatorID)
            feedbackCtrl.markObjectiveOnMinimap(cmdCreatorID, cmd.getMarkedObjective(), commandName)
            return

    def __handleRegularCommand(self, cmd):
        cmdID = cmd.getID()
        cmdName = _ACTIONS.battleChatCommandFromActionID(cmdID).name
        cmdCreatorID = self.__getCommandCreatorVehID(cmd)
        cmdTargetID = self.__getTargetIDForCommandName(cmdName, cmd)
        cmdDuration = _DEFAULT_ACTIVE_COMMAND_TIME if cmdName != BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA else _DEFAULT_SPG_AREA_COMMAND_TIME
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[cmdName]
        if markerType in self._chatCommands and cmdTargetID in self._chatCommands[markerType] and cmdID in self._chatCommands[markerType][cmdTargetID]:
            if cmdName in AUTOCOMMIT_COMMAND_NAMES:
                self.__addReplyToCommandList(cmdCreatorID, cmdTargetID, cmdID)
            return
        if cmdName == BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY and MarkerType.VEHICLE_MARKER_TYPE in self._chatCommands and cmdTargetID in self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE]:
            activeCommandIDOnTarget = self._chatCommands[MarkerType.VEHICLE_MARKER_TYPE][cmdTargetID].keys()
            helpCommandID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.HELPME].id
            sosCommandID = BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.SOS].id
            if helpCommandID in activeCommandIDOnTarget or sosCommandID in activeCommandIDOnTarget:
                activeHelpID = helpCommandID if helpCommandID in activeCommandIDOnTarget else sosCommandID
                self.__tryRemovingCommandFromMarker(activeHelpID, cmdTargetID)
                self.__addCommandToList(cmdID, cmdName, cmdCreatorID, cmdTargetID, cmd, cmdDuration)
            elif cmdID in activeCommandIDOnTarget:
                self.__addReplyToCommandList(cmdCreatorID, cmdTargetID, cmdID)
        elif cmdName not in (BATTLE_CHAT_COMMAND_NAMES.CONFIRM, BATTLE_CHAT_COMMAND_NAMES.POSITIVE):
            self.__addCommandToList(cmdID, cmdName, cmdCreatorID, cmdTargetID, cmd, cmdDuration)
        if cmd.isLocationRelatedCommand():
            self.__handleMark3DPosition(cmdTargetID, cmdCreatorID, cmdID, cmdName, cmdDuration, cmd)
        elif cmd.isBaseRelatedCommand():
            self.__handleBaseCommand(cmdName, cmdCreatorID, cmdID, cmdTargetID)
        elif cmd.isVehicleRelatedCommand():
            self.__handleVehicleCommand(cmdTargetID, cmdCreatorID, cmdID, cmd)
        elif cmd.isMarkedObjective():
            self.__handleObjectiveCommand(cmdName, cmdCreatorID, cmd)

    def __addReplyToCommandList(self, replierVehicleID, targetID, repliedToCommandID):
        repliedToActionName = _ACTIONS.battleChatCommandFromActionID(repliedToCommandID).name
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[repliedToActionName]
        if markerType not in self._chatCommands or targetID not in self._chatCommands[markerType] or repliedToCommandID not in self._chatCommands[markerType][targetID]:
            _logger.error('Trying to add reply to non-existing element of markerType(%s), targetID(%d) and repliedToCommandID(%d)', markerType.name, targetID, repliedToCommandID)
            return
        self.__removeReplyContributionFromPlayer(replierVehicleID, markerType, targetID)
        commandData = self._chatCommands[markerType][targetID][repliedToCommandID]
        oldOwnerCount = len(commandData.owners)
        if replierVehicleID not in commandData.owners:
            commandData.owners.append(replierVehicleID)
        self.__notifyReplyCommandUpdate(targetID, replierVehicleID, repliedToCommandID, oldOwnerCount, len(commandData.owners))
        self.__chatCommandsUpdated(markerType, targetID, repliedToCommandID, replierVehicleID, ChatCommandChange.CHAT_CMD_WAS_REPLIED)
        if replierVehicleID == avatar_getter.getPlayerVehicleID():
            self.__setFocusedOnMarker(targetID, markerType, repliedToCommandID)

    def __setFocusedOnMarker(self, targetID, markerType, repliedToCommandID):
        self.__checkTemporarySticky(repliedToCommandID, targetID)
        oldID = 0
        oldMarkerType = MarkerType.INVALID_MARKER_TYPE
        if self.__markerInFocus is not None:
            oldID = self.__markerInFocus.targetID
            oldMarkerType = self.__markerInFocus.markerType
        feedbackCtrl = self.sessionProvider.shared.feedback
        if feedbackCtrl:
            feedbackCtrl.setInFocusForPlayer(oldID, oldMarkerType, targetID, markerType, False)
        if targetID == 0 and markerType == MarkerType.INVALID_MARKER_TYPE:
            self.__markerInFocus = None
        else:
            self.__markerInFocus = MarkerInFocus(commandID=repliedToCommandID, targetID=targetID, markerType=markerType)
        return

    def __getCorrectReplyCommandName(self, targetID, replyActionName):
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

    def __handleReply(self, cmd):
        replierVehicleID = self.__getCommandCreatorVehID(cmd)
        targetID = cmd.getFirstTargetID()
        replyToActionName = cmd.getCommandData()['strArg1']
        if replierVehicleID:
            self.__addPositiveMarkerAboveCreator(replierVehicleID)
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[replyToActionName]
        replyToActionName = self.__getCorrectReplyCommandName(targetID, replyToActionName)
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
                self.__handleRegularCommand(command)
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
                self.__handleRegularCommand(command)
            else:
                _logger.debug('Reply to action name, no action needed (%s)', replyToActionName)
        else:
            self.__addReplyToCommandList(replierVehicleID, targetID, repliedToActionID)

    def __handleCancelReply(self, cmd):
        playerVehicleID = self.__getCommandCreatorVehID(cmd)
        self.__removeReplyContributionFromPlayer(playerVehicleID, MarkerType.INVALID_MARKER_TYPE, -1)

    def __handleClearChatCommands(self, cmd):
        targetID = cmd.getFirstTargetID()
        markerTypeName = cmd.getCommandData()['strArg1']
        markerType = MarkerType.getEnumValueByName(markerTypeName)
        removeList = list()
        if markerType is not None and markerType in self._chatCommands:
            if targetID in self._chatCommands[markerType]:
                for commandID in self._chatCommands[markerType][targetID]:
                    commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
                    currentTargetID = self.__getTargetIDForCommandName(commandName, cmd, True)
                    if currentTargetID not in self._chatCommands[markerType]:
                        continue
                    removeList.append((commandID, currentTargetID))
                    chatCommandData = self._chatCommands[markerType][currentTargetID][commandID]
                    for replier in chatCommandData.owners:
                        self.__chatCommandsUpdated(markerType, currentTargetID, commandID, replier, ChatCommandChange.CHAT_CMD_WAS_REMOVED)

            else:
                self.__removeReplyContributionFromPlayer(targetID, MarkerType.INVALID_MARKER_TYPE, -1)
        for commandID, tID in removeList:
            self.__tryRemovingCommandFromMarker(commandID, tID, True)

        return

    def __removeReplyContributionFromPlayer(self, replierVehID, newTargetType, newTargetID):
        updatedCommand = None
        checkForRemovalOfCommandFromMarker = False
        for markerType in self._chatCommands:
            for targetID in self._chatCommands[markerType]:
                for commandID, commandData in self._chatCommands[markerType][targetID].iteritems():
                    isSameCommand = targetID == newTargetID and newTargetType == markerType
                    if not isSameCommand and replierVehID in commandData.owners:
                        oldOwnerCount = len(commandData.owners)
                        self.__chatCommandsUpdated(markerType, targetID, commandID, replierVehID, ChatCommandChange.CHAT_CMD_WAS_REMOVED)
                        commandData.owners.remove(replierVehID)
                        updatedCommand = (commandID, targetID)
                        self.__notifyReplyCommandUpdate(targetID, replierVehID, commandID, oldOwnerCount, len(commandData.owners))
                        if not commandData.owners:
                            checkForRemovalOfCommandFromMarker = True
                        break

        if updatedCommand is not None:
            cmdID, cmdTargetID = updatedCommand
            commandName = _ACTIONS.battleChatCommandFromActionID(cmdID).name
            if replierVehID == avatar_getter.getPlayerVehicleID() and self.__markerInFocus and self.__markerInFocus.isFocused(cmdTargetID, _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]):
                self.__setFocusedOnMarker(-1, MarkerType.INVALID_MARKER_TYPE, -1)
            if checkForRemovalOfCommandFromMarker:
                self.__tryRemovingCommandFromMarker(cmdID, cmdTargetID, commandName in AUTOCOMMIT_COMMAND_NAMES)
        return

    def __notifyReplyCommandUpdate(self, targetID, replierVehicleID, commandID, oldReplyCount, newReplycount):
        commandDesr = _ACTIONS.battleChatCommandFromActionID(commandID)
        if commandDesr is None or commandDesr.name not in _COMMAND_NAME_TRANSFORM_MARKER_TYPE or not self.sessionProvider.shared.feedback:
            return
        else:
            self.sessionProvider.shared.feedback.onReplyToCommand(targetID, replierVehicleID, _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandDesr.name], oldReplyCount, newReplycount)
            return

    def __me_onBattleUserActionReceived(self, actionID, user):
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
                self.__removeReplyContributionFromPlayer(vehicleID, MarkerType.INVALID_MARKER_TYPE, -1)
            return

    def __onSettingsChanged(self, diff):
        battleCommunicationEnabled = diff.get(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION)
        if battleCommunicationEnabled is None:
            return
        else:
            _logger.debug('IBC settings changed, adding/removing listeners.')
            if battleCommunicationEnabled is True:
                self.__addEventListeners()
            else:
                self.__removeActiveCommands()
                self.__removeEventListenersAndClear()
            self.__isEnabled = battleCommunicationEnabled
            return

    def __checkTemporarySticky(self, commandID, targetID):
        if commandID not in self.__temporaryStickyCommands or targetID not in self.__temporaryStickyCommands[commandID]:
            return
        commandTargetID, markerType = self.__temporaryStickyCommands[commandID].pop(targetID)
        isOneShot = _ACTIONS.battleChatCommandFromActionID(commandID).name in ONE_SHOT_COMMANDS_TO_REPLIES.keys()
        focusedTargetID = 0
        focusedMarkerType = ''
        if self.__markerInFocus and self.__markerInFocus.isFocused(commandTargetID, markerType):
            focusedTargetID = self.__markerInFocus.targetID
            focusedMarkerType = self.__markerInFocus.markerType
        fbCtrl = self.sessionProvider.shared.feedback
        if fbCtrl and not (focusedMarkerType == markerType and commandTargetID == focusedTargetID):
            fbCtrl.setInFocusForPlayer(commandTargetID, markerType, -1, MarkerType.INVALID_MARKER_TYPE, isOneShot)
        if not self.__temporaryStickyCommands[commandID]:
            self.__temporaryStickyCommands.pop(commandID)

    def __tryRemovalOfPreviousLocationCommands(self, ucmdCreatorID):
        removeCommandsList = list()
        for markerType in self._chatCommands:
            for targetID in self._chatCommands[markerType]:
                for commandID, commandData in self._chatCommands[markerType][targetID].iteritems():
                    if commandData.command.isLocationRelatedCommand() and ucmdCreatorID == commandData.commandCreatorVehID and not commandData.owners and commandID != BATTLE_CHAT_COMMANDS_BY_NAMES[BATTLE_CHAT_COMMAND_NAMES.GOING_THERE].id:
                        removeCommandsList.append((commandID, targetID))

        if removeCommandsList:
            for removeCommandID, removeTargetID in removeCommandsList:
                self.__checkTemporarySticky(removeCommandID, removeTargetID)
                self.__tryRemovingCommandFromMarker(removeCommandID, removeTargetID, True)

    def __tryRemovingCommandFromMarker(self, commandID, targetID, forceRemove=False):
        if _ACTIONS.battleChatCommandFromActionID(commandID) is None:
            return
        else:
            commandName = _ACTIONS.battleChatCommandFromActionID(commandID).name
            markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
            commandData = self._chatCommands[markerType][targetID][commandID]
            if forceRemove or not self.__delayer.hasDelayedCallbackID(commandData.callbackID) and not commandData.owners:
                self.__delayer.stopCallback(commandData.callbackID)
                self._chatCommands[markerType][targetID].pop(commandID)
                wasLastCommandForTarget = not self._chatCommands[markerType][targetID]
                if wasLastCommandForTarget:
                    self._chatCommands[markerType].pop(targetID)
                if wasLastCommandForTarget:
                    feedbackCtrl = self.sessionProvider.shared.feedback
                    if feedbackCtrl:
                        feedbackCtrl.onCommandRemoved(targetID, markerType)
            return

    def __setInFocusCB(self, commandID, commandTargetID, markerType, isOneShot, isTemporary):
        if isTemporary:
            feedbackCtrl = self.sessionProvider.shared.feedback
            if feedbackCtrl:
                feedbackCtrl.setInFocusForPlayer(-1, MarkerType.INVALID_MARKER_TYPE, commandTargetID, markerType, isOneShot)
        else:
            self.__setFocusedOnMarker(commandTargetID, markerType, commandID)

    def __removeCommandMarkerCB(self, removeCommandID, removeCommandTargetID):
        if _ACTIONS.battleChatCommandFromActionID(removeCommandID) is None:
            _logger.warning('Command with ID %s was not found.', removeCommandID)
            return
        else:
            commandName = _ACTIONS.battleChatCommandFromActionID(removeCommandID).name
            markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[commandName]
            commandData = self._chatCommands.get(markerType, {}).get(removeCommandTargetID, {}).get(removeCommandID, None)
            if not commandData:
                return
            self.__delayer.stopCallback(commandData.callbackID)
            self.__checkTemporarySticky(removeCommandID, removeCommandTargetID)
            self.__tryRemovingCommandFromMarker(removeCommandID, removeCommandTargetID)
            return

    def __onSettingsReady(self):
        _logger.debug('Settings are synced, checking the IBC.')
        if self.__isEnabled is None:
            self.__isEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
            if not self.__isEnabled:
                return
            self.__addEventListeners()
        self.settingsCache.onSyncCompleted -= self.__onSettingsReady
        return
