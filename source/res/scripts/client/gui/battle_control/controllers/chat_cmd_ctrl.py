# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/chat_cmd_ctrl.py
import logging
import math
import weakref
import BigWorld
import CommandMapping
import DestructibleEntity
import Math
import Vehicle
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.cameras import getWorldRayAndPoint
from aih_constants import CTRL_MODE_NAME
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME
from chat_commands_consts import MarkerType, DefaultMarkerSubType, ReplyState, BATTLE_CHAT_COMMAND_NAMES, INVALID_MARKER_SUBTYPE, _COMMAND_NAME_TRANSFORM_MARKER_TYPE, ONE_SHOT_COMMANDS_TO_REPLIES, COMMAND_RESPONDING_MAPPING
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import dependency
from helpers import isPlayerAvatar
from messenger import MessengerEntry
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw_chat2.battle_chat_cmd import EPIC_GLOBAL_CMD_NAMES, LOCATION_CMD_NAMES, TARGET_CMD_NAMES
from skeletons.account_helpers.settings_core import IBattleCommunicationsSettings
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.player_satisfaction_rating.loggers import KeyboardShortcutLogger
_logger = logging.getLogger(__name__)
CONTEXTCOMMAND = 'CONTEXTCOMMAND'
CONTEXTCOMMAND2 = 'CONTEXTCOMMAND2'
KB_MAPPING = {BATTLE_CHAT_COMMAND_NAMES.TURNBACK: CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
 BATTLE_CHAT_COMMAND_NAMES.SOS: CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN: CommandMapping.CMD_CHAT_SHORTCUT_RELOAD,
 BATTLE_CHAT_COMMAND_NAMES.AFFIRMATIVE: CommandMapping.CMD_CHAT_SHORTCUT_AFFIRMATIVE,
 BATTLE_CHAT_COMMAND_NAMES.NEGATIVE: CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE,
 BATTLE_CHAT_COMMAND_NAMES.THANKS: CommandMapping.CMD_CHAT_SHORTCUT_THANKYOU,
 BATTLE_CHAT_COMMAND_NAMES.REPLY: CommandMapping.CMD_RADIAL_MENU_SHOW,
 CONTEXTCOMMAND: CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND,
 CONTEXTCOMMAND2: CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMIT}
TARGET_TYPE_TRANSLATION_MAPPING = {CONTEXTCOMMAND: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.HELPME,
                                                   DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY},
                  MarkerType.BASE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
                                                DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE},
                  MarkerType.TARGET_POINT_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT,
                                                        DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.MOVE_TO_TARGET_POINT},
                  MarkerType.HEADQUARTER_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE,
                                                       DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE},
                  MarkerType.LOCATION_MARKER_TYPE: {INVALID_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION}},
 CONTEXTCOMMAND2: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
                                                    DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY},
                   MarkerType.BASE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
                                                 DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE},
                   MarkerType.TARGET_POINT_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT,
                                                         DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.MOVING_TO_TARGET_POINT},
                   MarkerType.HEADQUARTER_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.DEFENDING_OBJECTIVE,
                                                        DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.ATTACKING_OBJECTIVE},
                   MarkerType.LOCATION_MARKER_TYPE: {INVALID_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.GOING_THERE}},
 BATTLE_CHAT_COMMAND_NAMES.TURNBACK: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.TURNBACK}},
 BATTLE_CHAT_COMMAND_NAMES.THANKS: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.THANKS}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_1}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_2}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_3}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_4}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_5}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_6}},
 BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7_EX: {MarkerType.VEHICLE_MARKER_TYPE: {DefaultMarkerSubType.ALLY_MARKER_SUBTYPE: BATTLE_CHAT_COMMAND_NAMES.EVENT_CHAT_7}}}
DIRECT_ACTION_BATTLE_CHAT_COMMANDS = [BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN,
 BATTLE_CHAT_COMMAND_NAMES.AFFIRMATIVE,
 BATTLE_CHAT_COMMAND_NAMES.NEGATIVE]
PROHIBITED_IF_DEAD = [BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT,
 BATTLE_CHAT_COMMAND_NAMES.FLAG_POINT]
PROHIBITED_IF_SPECTATOR = [BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.SOS,
 BATTLE_CHAT_COMMAND_NAMES.HELPME,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY,
 BATTLE_CHAT_COMMAND_NAMES.ATTACK_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFEND_BASE,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT,
 BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE,
 BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
 BATTLE_CHAT_COMMAND_NAMES.FLAG_POINT]

def getAimedAtPositionWithinBorders(aimOffsetX, aimOffsetY):
    ray, _ = getWorldRayAndPoint(aimOffsetX, aimOffsetY)
    player = BigWorld.player()
    staticHitPoint = BigWorld.wg_collideSegment(player.spaceID, BigWorld.camera().position, BigWorld.camera().position + ray * 100000, 128)
    if staticHitPoint is not None:
        staticHitPoint = staticHitPoint.closestPoint
        boundingBox = player.arena.arenaType.boundingBox
        if not boundingBox[0][0] <= staticHitPoint.x <= boundingBox[1][0] or not boundingBox[0][1] <= staticHitPoint.z <= boundingBox[1][1]:
            return
        return staticHitPoint
    else:
        return
        return


class ChatCommandsController(IBattleController):
    __slots__ = ('__isEnabled', '__arenaDP', '__feedback', '__ammo', '__markersManager', '_uiPlayerSatisfactionRatingLogger')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    battleCommunications = dependency.descriptor(IBattleCommunicationsSettings)
    _aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self, setup, feedback, ammo):
        super(ChatCommandsController, self).__init__()
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__feedback = weakref.proxy(feedback)
        self.__ammo = weakref.proxy(ammo)
        self.__markersManager = None
        self.__isEnabled = False
        self._uiPlayerSatisfactionRatingLogger = KeyboardShortcutLogger()
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def getControllerID(self):
        return BATTLE_CTRL_ID.CHAT_COMMANDS

    def startControl(self):
        self.battleCommunications.onChanged += self.__onBattleCommunicationChanged
        g_eventBus.addListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        self.__arenaDP = None
        self.__feedback = None
        self.__ammo = None
        self.__markersManager = None
        self.battleCommunications.onChanged -= self.__onBattleCommunicationChanged
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        return

    def getAimedAtTargetData(self):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            targetID, targetMarkerType, markerSubType = self.__getAimedAtVehicleOrObject()
            if targetMarkerType == MarkerType.INVALID_MARKER_TYPE and self.__markersManager:
                tID, tMarkerType, tMarkerSubType = self.__markersManager.getCurrentlyAimedAtMarkerIDAndType()
                needCorrectCheck = tMarkerType == MarkerType.VEHICLE_MARKER_TYPE
                if not needCorrectCheck or self.__isTargetCorrect(BigWorld.player(), BigWorld.entities.get(tID)):
                    targetID, targetMarkerType, markerSubType = tID, tMarkerType, tMarkerSubType
            if targetMarkerType == MarkerType.INVALID_MARKER_TYPE and getAimedAtPositionWithinBorders(self._aimOffset[0], self._aimOffset[1]) is not None:
                targetMarkerType = MarkerType.LOCATION_MARKER_TYPE
                markerSubType = INVALID_MARKER_SUBTYPE
            replyState, replyToAction = self.getReplyStateForTargetIDAndMarkerType(targetID, targetMarkerType)
            return (targetID,
             targetMarkerType,
             markerSubType,
             replyState,
             replyToAction)

    def getReplyStateForTargetIDAndMarkerType(self, targetID, targetMarkerType):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        return None if advChatCmp is None else advChatCmp.getReplyStateForTargetIDAndMarkerType(targetID, targetMarkerType)

    def isTargetAllyCommittedToMe(self, targetID):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        return False if advChatCmp is None else advChatCmp.isTargetAllyCommittedToMe(targetID)

    def handleContexChatCommand(self, key):
        cmdMap = CommandMapping.g_instance
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            for chatCmd, keyboardCmd in KB_MAPPING.iteritems():
                if cmdMap.isFired(keyboardCmd, key):
                    if chatCmd in DIRECT_ACTION_BATTLE_CHAT_COMMANDS:
                        self.handleChatCommand(chatCmd)
                        return
                    targetID, targetMarkerType, markerSubType, replyState, replyToAction = self.getAimedAtTargetData()
                    if chatCmd in (BATTLE_CHAT_COMMAND_NAMES.THANKS, BATTLE_CHAT_COMMAND_NAMES.TURNBACK):
                        replyState = ReplyState.NO_REPLY
                    if replyState == ReplyState.NO_REPLY:
                        if chatCmd in TARGET_TYPE_TRANSLATION_MAPPING and targetMarkerType in TARGET_TYPE_TRANSLATION_MAPPING[chatCmd] and markerSubType in TARGET_TYPE_TRANSLATION_MAPPING[chatCmd][targetMarkerType]:
                            action = TARGET_TYPE_TRANSLATION_MAPPING[chatCmd][targetMarkerType][markerSubType]
                        else:
                            _logger.debug('Action %s (at key %s) is not supported for target type %s (cut type: %s)', chatCmd, key, targetMarkerType, markerSubType)
                            return
                        if action == BATTLE_CHAT_COMMAND_NAMES.HELPME:
                            if advChatCmp.isTargetAllyCommittedToMe(targetID):
                                action = BATTLE_CHAT_COMMAND_NAMES.THANKS
                        self._uiPlayerSatisfactionRatingLogger.logKeyboardShortcutAction(action)
                        self.handleChatCommand(action, targetID=targetID)
                    else:
                        if chatCmd == CONTEXTCOMMAND2 and replyState != ReplyState.CAN_REPLY:
                            return
                        if replyState == ReplyState.CAN_CANCEL_REPLY:
                            self.sendCancelReplyChatCommand(targetID, replyToAction)
                        elif replyState == ReplyState.CAN_REPLY:
                            if replyToAction in (BATTLE_CHAT_COMMAND_NAMES.HELPME, BATTLE_CHAT_COMMAND_NAMES.SOS):
                                self.handleChatCommand(BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY, targetID=targetID)
                            else:
                                self.sendReplyChatCommand(targetID, replyToAction)
                        elif replyState == ReplyState.CAN_CONFIRM and replyToAction in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
                            self.handleChatCommand(ONE_SHOT_COMMANDS_TO_REPLIES[replyToAction], targetID=targetID)
                        elif replyState == ReplyState.CAN_RESPOND and replyToAction in COMMAND_RESPONDING_MAPPING.keys():
                            self.handleChatCommand(COMMAND_RESPONDING_MAPPING[replyToAction], targetID=targetID)

            return

    def sendAdvancedPositionPing(self, action, isInRadialMenu=False):
        aimedAtPosition = getAimedAtPositionWithinBorders(self._aimOffset[0], self._aimOffset[1])
        if aimedAtPosition is not None:
            if self.__isSPG() and action == BATTLE_CHAT_COMMAND_NAMES.GOING_THERE or self.__isSPGAndInStrategicOrArtyMode() and isInRadialMenu is False and action == BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION:
                action = BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA
            self.sendAttentionToPosition3D(position=aimedAtPosition, name=action)
        return

    def sendReplyChatCommand(self, targetID, action):
        if not avatar_getter.isVehicleAlive() or self.sessionProvider.getCtx().isPlayerObserver() or self.__isEnabled is False:
            return
        player = BigWorld.player()
        command = self.proto.battleCmd.createReplyByName(targetID, action, player.id)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Reply command not valid for command id: %d', targetID)

    def sendCancelReplyChatCommand(self, targetID, action):
        if not avatar_getter.isVehicleAlive():
            return
        player = BigWorld.player()
        command = self.proto.battleCmd.createCancelReplyByName(targetID, action, player.id)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Cancel reply command not valid for command id: %d', targetID)

    def sendClearChatCommandsFromTarget(self, targetID, targetMarkerType):
        command = self.proto.battleCmd.createClearChatCommandsFromTarget(targetID, targetMarkerType)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Clear chat commands not valid for command id: %d and marker type: %s', targetID, targetMarkerType)

    def handleChatCommand(self, action, targetID=None, isInRadialMenu=False):
        player = BigWorld.player()
        targetType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE[action]
        if targetType == MarkerType.HEADQUARTER_MARKER_TYPE:
            self.sendAttentionToObjective(targetID, player.team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER, action)
        elif targetType == MarkerType.BASE_MARKER_TYPE:
            self.sendCommandToBase(targetID, action)
        elif action in LOCATION_CMD_NAMES:
            self.sendAdvancedPositionPing(action, isInRadialMenu)
        elif action in TARGET_CMD_NAMES:
            self.sendTargetedCommand(action, targetID, isInRadialMenu)
        elif action in EPIC_GLOBAL_CMD_NAMES:
            self.sendEpicGlobalCommand(action)
        elif action == BATTLE_CHAT_COMMAND_NAMES.RELOADINGGUN:
            self.sendReloadingCommand()
        else:
            self.sendCommand(action)

    def sendAttentionToPosition3D(self, position, name):
        if self.__isProhibitedToSendIfDeadOrObserver(name) or self.__isEnabled is False:
            return
        positionVec = Math.Vector3(position[0], position[1], position[2])
        if name == BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA and self.__isSPG():
            time = self.__getReloadTime() if self.__ammo.getAllShellsQuantityLeft() > 0 else -1
            command = self.proto.battleCmd.createByPosition(positionVec, name, time)
        else:
            command = self.proto.battleCmd.createByPosition(positionVec, name)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Minimap command for position (%d, %d, %d) not found', positionVec.x, positionVec.y, positionVec.z)

    def sendAttentionToObjective(self, hqIdx, isAtk, action=None):
        if self.__isEnabled is False:
            return
        else:
            if action is None:
                action = BATTLE_CHAT_COMMAND_NAMES.ATTACK_OBJECTIVE
                if not isAtk:
                    action = BATTLE_CHAT_COMMAND_NAMES.DEFEND_OBJECTIVE
            command = self.proto.battleCmd.createByObjectiveIndex(hqIdx, isAtk, action)
            if command:
                self.__sendChatCommand(command)
            else:
                _logger.error('Minimap command for objective with id: %d not found', hqIdx)
            return

    def sendCommandToBase(self, baseIdx, cmdName, baseName=''):
        if self.__isProhibitedToSendIfDeadOrObserver(cmdName) or self.__isEnabled is False:
            return
        if self.sessionProvider.arenaVisitor.gui.isInEpicRange():
            baseName = ID_TO_BASENAME[baseIdx]
        command = self.proto.battleCmd.createByBaseIndexAndName(baseIdx, cmdName, baseName)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Command not found: %s', cmdName)

    def sendCommand(self, cmdName):
        if self.__isProhibitedToSendIfDeadOrObserver(cmdName) or self.__isEnabled is False:
            return
        command = self.proto.battleCmd.createByName(cmdName)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Command not found: %s', cmdName)

    def sendEpicGlobalCommand(self, cmdName, baseName=''):
        if self.__isProhibitedToSendIfDeadOrObserver(cmdName) or self.__isEnabled is False:
            return
        command = self.proto.battleCmd.createByGlobalMsgName(cmdName, baseName)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Command not found: %s', cmdName)

    def sendTargetedCommand(self, cmdName, targetID, isInRadialMenu=False):
        if self.__isProhibitedToSendIfDeadOrObserver(cmdName) or self.__isEnabled is False:
            return
        if self.__arenaDP.isVehiclePresented(targetID):
            if not self.__arenaDP.getVehicleInfo(targetID).isAlive():
                return
            if self.__isSPG() and cmdName == BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY or self.__isSPGAndInStrategicOrArtyMode() and cmdName == BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY and isInRadialMenu is False:
                shellsLeft = self.__ammo.getAllShellsQuantityLeft()
                time = self.__getReloadTime() if shellsLeft > 0 else -1
                command = self.proto.battleCmd.createSPGAimTargetCommand(targetID, time)
            else:
                command = self.proto.battleCmd.createByNameTarget(cmdName, targetID)
        else:
            command = self.proto.battleCmd.createByNameTarget(cmdName, targetID)
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Targeted command(%s) was not found or targetID(%d) is not valid', cmdName, targetID)

    def sendReloadingCommand(self):
        if not avatar_getter.isPlayerOnArena() or self.__isEnabled is False:
            return
        state = self.__ammo.getGunReloadingState()
        command = self.proto.battleCmd.create4Reload(self.__ammo.getGunSettings().isCassetteClip(), math.ceil(state.getTimeLeft()), self.__ammo.getShellsQuantityLeft())
        if command:
            self.__sendChatCommand(command)
        else:
            _logger.error('Can not create reloading command')

    def __isProhibitedToSendIfDeadOrObserver(self, name):
        return not avatar_getter.isVehicleAlive() and name in PROHIBITED_IF_DEAD or self.sessionProvider.getCtx().isPlayerObserver() and name in PROHIBITED_IF_SPECTATOR

    def __isSPG(self):
        return self.sessionProvider.getArenaDP().getVehicleInfo().isSPG()

    def __isSPGAndInStrategicOrArtyMode(self):
        return self.__isSPG() and avatar_getter.getInputHandler().ctrlModeName in (CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY, CTRL_MODE_NAME.MAP_CASE)

    def __getReloadTime(self):
        reloadState = self.__ammo.getGunReloadingState()
        reloadTime = reloadState.getTimeLeft()
        return reloadTime

    def __sendChatCommand(self, command):
        controller = MessengerEntry.g_instance.gui.channelsCtrl.getController(command.getClientID())
        if controller:
            controller.sendCommand(command)

    def __onBattleCommunicationChanged(self):
        enableBattleCommunication = self.battleCommunications.isEnabled
        if enableBattleCommunication is None:
            return
        else:
            self.__isEnabled = enableBattleCommunication
            return

    def __getAimedAtVehicleOrObject(self):
        player = BigWorld.player()
        target = BigWorld.target()
        targetID = -1
        markerSubType = INVALID_MARKER_SUBTYPE
        targetMarkerType = MarkerType.INVALID_MARKER_TYPE
        if self.__isTargetCorrect(player, target):
            if isinstance(target, DestructibleEntity.DestructibleEntity):
                targetID = target.destructibleEntityID
                targetMarkerType = MarkerType.HEADQUARTER_MARKER_TYPE
                markerSubType = DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE if avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER else DefaultMarkerSubType.ALLY_MARKER_SUBTYPE
            elif target.publicInfo['team'] == avatar_getter.getPlayerTeam():
                targetID = target.id
                targetMarkerType = MarkerType.VEHICLE_MARKER_TYPE
                markerSubType = DefaultMarkerSubType.ALLY_MARKER_SUBTYPE
            else:
                targetID = target.id
                targetMarkerType = MarkerType.VEHICLE_MARKER_TYPE
                markerSubType = DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE
        return (targetID, targetMarkerType, markerSubType)

    def __isTargetCorrect(self, player, target):
        if target is not None and isinstance(target, DestructibleEntity.DestructibleEntity):
            if target.isAlive():
                if player is not None and isPlayerAvatar():
                    return True
        if target is not None and isinstance(target, Vehicle.Vehicle):
            if target.isAlive():
                if player is not None and isPlayerAvatar():
                    vInfo = self.__arenaDP.getVehicleInfo(target.id)
                    isAlly = target.publicInfo['team'] == player.team
                    return not vInfo.isChatCommandsDisabled(isAlly)
        return False

    def __onMarkersManagerMarkersCreated(self, event):
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self.__markersManager = event.getMarkersManager()
        self.__isEnabled = bool(self.battleCommunications.isEnabled)
