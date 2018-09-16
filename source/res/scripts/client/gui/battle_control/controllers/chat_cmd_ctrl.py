# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/chat_cmd_ctrl.py
import math
import struct
import weakref
import BigWorld
import CommandMapping
import Math
from battleground.StunAreaManager import g_stunAreaManager
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter, minimap_utils
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from messenger import MessengerEntry
from messenger.m_constants import MESSENGER_COMMAND_TYPE, PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from gui.sounds.epic_sound_constants import EPIC_SOUND
import Vehicle
import DestructibleEntity
from helpers import isPlayerAvatar
from epic_constants import EPIC_BATTLE_TEAM_ID

class CHAT_COMMANDS(object):
    ATTACK = 'ATTACK'
    BACKTOBASE = 'BACKTOBASE'
    POSITIVE = 'POSITIVE'
    NEGATIVE = 'NEGATIVE'
    SOS = 'HELPME'
    RELOADINGGUN = 'RELOADINGGUN'
    FOLLOWME = 'FOLLOWME'
    TURNBACK = 'TURNBACK'
    HELPME = 'HELPMEEX'
    SUPPORTMEWITHFIRE = 'SUPPORTMEWITHFIRE'
    ATTACKENEMY = 'ATTACKENEMY'
    STOP = 'STOP'
    SPG_AIM_AREA = 'SPG_AIM_AREA'
    GLOBAL_SAVE_TANKS_ATK = 'EPIC_GLOBAL_SAVETANKS_ATK'
    GLOBAL_TIME_ATK = 'EPIC_GLOBAL_TIME_ATK'
    GLOBAL_FOCUSHQ_ATK = 'EPIC_GLOBAL_HQ_ATK'
    GLOBAL_SAVE_TANKS_DEF = 'EPIC_GLOBAL_SAVETANKS_DEF'
    GLOBAL_TIME_DEF = 'EPIC_GLOBAL_TIME_DEF'
    GLOBAL_FOCUSHQ_DEF = 'EPIC_GLOBAL_HQ_DEF'
    GLOBAL_LANE_WEST = 'EPIC_GLOBAL_WEST'
    GLOBAL_LANE_CENTER = 'EPIC_GLOBAL_CENTER'
    GLOBAL_LANE_EAST = 'EPIC_GLOBAL_EAST'


KB_MAPPING = {CHAT_COMMANDS.ATTACKENEMY: CommandMapping.CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET,
 CHAT_COMMANDS.ATTACK: CommandMapping.CMD_CHAT_SHORTCUT_ATTACK,
 CHAT_COMMANDS.BACKTOBASE: CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
 CHAT_COMMANDS.POSITIVE: CommandMapping.CMD_CHAT_SHORTCUT_POSITIVE,
 CHAT_COMMANDS.NEGATIVE: CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE,
 CHAT_COMMANDS.SOS: CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
 CHAT_COMMANDS.RELOADINGGUN: CommandMapping.CMD_CHAT_SHORTCUT_RELOAD}
TARGET_ACTIONS = [CHAT_COMMANDS.FOLLOWME,
 CHAT_COMMANDS.TURNBACK,
 CHAT_COMMANDS.HELPME,
 CHAT_COMMANDS.SUPPORTMEWITHFIRE,
 CHAT_COMMANDS.ATTACKENEMY,
 CHAT_COMMANDS.STOP]
EPIC_GLOBAL_ACTIONS = [CHAT_COMMANDS.GLOBAL_SAVE_TANKS_ATK,
 CHAT_COMMANDS.GLOBAL_TIME_ATK,
 CHAT_COMMANDS.GLOBAL_FOCUSHQ_ATK,
 CHAT_COMMANDS.GLOBAL_SAVE_TANKS_DEF,
 CHAT_COMMANDS.GLOBAL_TIME_DEF,
 CHAT_COMMANDS.GLOBAL_FOCUSHQ_DEF,
 CHAT_COMMANDS.GLOBAL_LANE_WEST,
 CHAT_COMMANDS.GLOBAL_LANE_CENTER,
 CHAT_COMMANDS.GLOBAL_LANE_EAST]
DEFAULT_CUT = 'default'
ALLY_CUT = 'ally'
ENEMY_CUT = 'enemy'
ENEMY_SPG_CUT = 'enemy_spg'
OBJECTIVE_CUT = 'objective'
TARGET_TRANSLATION_MAPPING = {CHAT_COMMANDS.ATTACKENEMY: {ALLY_CUT: CHAT_COMMANDS.FOLLOWME,
                             ENEMY_CUT: CHAT_COMMANDS.SUPPORTMEWITHFIRE,
                             ENEMY_SPG_CUT: CHAT_COMMANDS.ATTACKENEMY},
 CHAT_COMMANDS.BACKTOBASE: {ALLY_CUT: CHAT_COMMANDS.TURNBACK},
 CHAT_COMMANDS.SOS: {ALLY_CUT: CHAT_COMMANDS.HELPME},
 CHAT_COMMANDS.RELOADINGGUN: {ALLY_CUT: CHAT_COMMANDS.STOP}}

class ChatCommandsController(IBattleController):
    __slots__ = ('__arenaDP', '__feedback', '__ammo')

    def __init__(self, setup, feedback, ammo):
        super(ChatCommandsController, self).__init__()
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__feedback = weakref.proxy(feedback)
        self.__ammo = weakref.proxy(ammo)

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def getControllerID(self):
        return BATTLE_CTRL_ID.CHAT_COMMANDS

    def startControl(self):
        g_messengerEvents.channels.onCommandReceived += self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived += self.__me_onCommandReceived

    def stopControl(self):
        self.__arenaDP = None
        self.__feedback = None
        self.__ammo = None
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__me_onCommandReceived
        return

    def handleShortcutChatCommand(self, key):
        cmdMap = CommandMapping.g_instance
        player = BigWorld.player()
        target = BigWorld.target()
        for chatCmd, keyboardCmd in KB_MAPPING.iteritems():
            if cmdMap.isFired(keyboardCmd, key):
                action = chatCmd
                crosshairType = self.__getCrosshairType(player, target)
                if crosshairType != DEFAULT_CUT and chatCmd in TARGET_TRANSLATION_MAPPING and crosshairType in TARGET_TRANSLATION_MAPPING[chatCmd]:
                    action = TARGET_TRANSLATION_MAPPING[chatCmd][crosshairType]
                if action in TARGET_ACTIONS:
                    if crosshairType == OBJECTIVE_CUT:
                        self.sendAttentionToObjective(target.destructibleEntityID, player.team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER)
                    elif crosshairType != DEFAULT_CUT:
                        self.handleChatCommand(action, targetID=target.id)
                else:
                    self.handleChatCommand(action)

    def handleSPGAimAreaCommand(self, player):
        boundingBox = player.arena.arenaType.boundingBox
        desiredShotPoint = player.inputHandler.getMarkerPoint()
        if not boundingBox[0][0] <= desiredShotPoint.x <= boundingBox[1][0] or not boundingBox[0][1] <= desiredShotPoint.z <= boundingBox[1][1]:
            desiredShotPoint = None
        if desiredShotPoint is not None:
            reloadTime = self.__getReloadTime()
            cellIdx = minimap_utils.getCellIdxFromPosition(desiredShotPoint, boundingBox)
            command = self.proto.battleCmd.createSPGAimAreaCommand(desiredShotPoint, cellIdx, reloadTime)
            if command:
                self.__sendChatCommand(command)
            else:
                LOG_ERROR('Failed to create {} command: {}'.format(CHAT_COMMANDS.SPG_AIM_AREA, (desiredShotPoint, boundingBox, reloadTime)))
        return

    def handleChatCommand(self, action, targetID=None):
        if action in TARGET_ACTIONS:
            self.sendTargetedCommand(action, targetID)
        elif action in EPIC_GLOBAL_ACTIONS:
            self.sendEpicGlobalCommand(action)
        elif action == CHAT_COMMANDS.RELOADINGGUN:
            self.sendReloadingCommand()
        else:
            self.sendCommand(action)

    def sendAttentionToCell(self, cellIdx):
        if avatar_getter.isForcedGuiControlMode():
            command = self.proto.battleCmd.createByCellIdx(cellIdx)
            if command:
                self.__sendChatCommand(command)
            else:
                LOG_ERROR('Minimap command not found', cellIdx)

    def sendAttentionToPosition(self, position):
        if avatar_getter.isForcedGuiControlMode():
            command = self.proto.battleCmd.createByPosition(position)
            if command:
                self.__sendChatCommand(command)
            else:
                LOG_ERROR('Minimap command not found', position)

    def sendAttentionToObjective(self, hqIdx, isAtk):
        command = self.proto.battleCmd.createByObjectiveIndex(hqIdx, isAtk)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Minimap command not found', hqIdx)

    def sendAttentionToBase(self, baseIdx, baseName, isAtk):
        if avatar_getter.isForcedGuiControlMode():
            command = self.proto.battleCmd.createByBaseIndex(baseIdx, baseName, isAtk)
            if command:
                self.__sendChatCommand(command)
            else:
                LOG_ERROR('Minimap command not found', baseIdx)

    def sendCommand(self, cmdName):
        if not avatar_getter.isVehicleAlive():
            return
        command = self.proto.battleCmd.createByName(cmdName)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Command is not found', cmdName)

    def sendEpicGlobalCommand(self, cmdName, baseName=''):
        command = self.proto.battleCmd.createByGlobalMsgName(cmdName, baseName)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Global Command is not found', cmdName)

    def sendTargetedCommand(self, cmdName, targetID):
        if not avatar_getter.isVehicleAlive():
            return
        if cmdName == CHAT_COMMANDS.ATTACKENEMY:
            command = self.proto.battleCmd.createSPGAimTargetCommand(targetID, self.__getReloadTime())
        else:
            command = self.proto.battleCmd.createByNameTarget(cmdName, targetID)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Targeted command is not found or targetID is not defined', cmdName)

    def sendReloadingCommand(self):
        if not avatar_getter.isPlayerOnArena():
            return
        state = self.__ammo.getGunReloadingState()
        command = self.proto.battleCmd.create4Reload(self.__ammo.getGunSettings().isCassetteClip(), math.ceil(state.getTimeLeft()), self.__ammo.getShellsQuantityLeft())
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Can not create reloading command')

    def __getReloadTime(self):
        reloadState = self.__ammo.getGunReloadingState()
        reloadTime = reloadState.getTimeLeft()
        return reloadTime

    def __playSound(self, cmd):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(cmd.getSoundEventName())
        if cmd is None:
            return
        else:
            if cmd.isEpicGlobalMessage():
                if soundNotifications and hasattr(soundNotifications, 'play'):
                    soundNotifications.play(EPIC_SOUND.BF_EB_GLOBAL_MESSAGE)
            elif soundNotifications and hasattr(soundNotifications, 'play'):
                soundNotifications.play(cmd.getSoundEventName())
            return

    def __findVehicleInfoByDatabaseID(self, dbID):
        result = None
        if self.__arenaDP is None:
            return result
        else:
            vehicleID = self.__arenaDP.getVehIDByAccDBID(dbID)
            if vehicleID:
                result = self.__findVehicleInfoByVehicleID(vehicleID)
            return result

    def __findVehicleInfoByVehicleID(self, vehicleID):
        result = None
        if self.__arenaDP is None:
            return result
        else:
            vehicleInfo = self.__arenaDP.getVehicleInfo(vehicleID)
            if vehicleInfo.isAlive() and not vehicleInfo.isObserver():
                result = vehicleInfo
            return result

    def __sendChatCommand(self, command):
        controller = MessengerEntry.g_instance.gui.channelsCtrl.getController(command.getClientID())
        if controller:
            controller.sendCommand(command)

    def __handleSimpleCommand(self, cmd):
        vMarker = cmd.getVehMarker()
        if vMarker:
            vehicleInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
            vehicleID = vehicleInfo.vehicleID if vehicleInfo else 0
            if vehicleID:
                self.__feedback.showActionMarker(vehicleID, vMarker, vMarker)

    def __handlePrivateCommand(self, cmd):
        vehicleInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if cmd.isReceiver() or cmd.isSender():
            self.__playSound(cmd)
            if vehicleInfo is None:
                vehicleInfo = self.__findVehicleInfoByVehicleID(avatar_getter.getPlayerVehicleID())
            vehicleID = vehicleInfo.vehicleID if vehicleInfo else 0
            vMarker = cmd.getVehMarker(vehicle=vehicleInfo)
            if vMarker and vehicleID:
                self.__feedback.showActionMarker(vehicleID, vMarker, cmd.getVehMarker())
        return

    def __handlePublicCommand(self, cmd):
        senderInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if senderInfo is None:
            senderInfo = self.__findVehicleInfoByVehicleID(avatar_getter.getPlayerVehicleID())
        showReceiver = cmd.showMarkerForReceiver()
        recvMarker, senderMarker = cmd.getVehMarkers(vehicle=senderInfo)
        receiverID = cmd.getFirstTargetID()
        senderID = senderInfo.vehicleID if senderInfo else 0
        if showReceiver:
            if receiverID:
                self.__feedback.showActionMarker(receiverID, recvMarker, recvMarker)
            if senderID:
                self.__feedback.showActionMarker(senderID, senderMarker, senderMarker)
        elif senderID:
            self.__feedback.showActionMarker(senderID, recvMarker, recvMarker)
        return

    def __me_onCommandReceived(self, cmd):
        if cmd.getCommandType() != MESSENGER_COMMAND_TYPE.BATTLE:
            return
        else:
            controller = MessengerEntry.g_instance.gui.channelsCtrl.getController(cmd.getClientID())
            if controller is None:
                LOG_ERROR('Controller not found', cmd)
                return
            if not controller.filterMessage(cmd):
                return
            if cmd.isOnMinimap():
                if cmd.isSPGAimCommand():
                    try:
                        coordX, coordY, coordZ = struct.unpack('<fffif', cmd.getCommandData()['strArg1'])[:3]
                    except struct.error as e:
                        LOG_ERROR('The following command can not be unpacked: ', e)
                        return

                    senderID = cmd.getSenderID()
                    g_stunAreaManager.manageStunArea(Math.Vector3(coordX, coordY, coordZ), senderID)
                else:
                    self.__feedback.markCellOnMinimap(cmd.getCellIndex())
            elif cmd.isOnEpicBattleMinimap():
                if cmd.isMarkedPosition():
                    self.__feedback.markPositionOnMinimap(cmd.getSenderID(), cmd.getMarkedPosition())
                elif cmd.isMarkedObjective():
                    self.__feedback.markObjectiveOnMinimap(cmd.getSenderID(), cmd.getMarkedObjective())
                elif cmd.isMarkedBase():
                    self.__feedback.markBaseOnMinimap(cmd.getSenderID(), cmd.getMarkedBase(), cmd.getMarkedBaseName())
            elif cmd.isEpicGlobalMessage():
                self.__playSound(cmd)
            elif cmd.isPrivate():
                self.__handlePrivateCommand(cmd)
            else:
                self.__playSound(cmd)
                if cmd.isPublic():
                    self.__handlePublicCommand(cmd)
                else:
                    self.__handleSimpleCommand(cmd)
            return

    def __getCrosshairType(self, player, target):
        outcome = DEFAULT_CUT
        if self.__isTargetCorrect(player, target):
            if isinstance(target, DestructibleEntity.DestructibleEntity):
                outcome = OBJECTIVE_CUT
            elif target.publicInfo['team'] == player.team:
                outcome = ALLY_CUT
            else:
                vehicleDesc = self.__getVehicleDesc(player.playerVehicleID)['vehicleType']
                if vehicleDesc is not None and 'SPG' in vehicleDesc.type.tags:
                    outcome = ENEMY_SPG_CUT
                else:
                    outcome = ENEMY_CUT
        return outcome

    def __isTargetCorrect(self, player, target):
        if target is not None and isinstance(target, DestructibleEntity.DestructibleEntity):
            if target.isAlive():
                if player is not None and isPlayerAvatar():
                    return True
        if target is not None and isinstance(target, Vehicle.Vehicle):
            if target.isAlive():
                if player is not None and isPlayerAvatar():
                    vInfo = self.__arenaDP.getVehicleInfo(target.id)
                    return not vInfo.isActionsDisabled()
        return False

    def __getVehicleDesc(self, vehicleID):
        vehicles = BigWorld.player().arena.vehicles
        for vID, desc in vehicles.items():
            if vID == vehicleID:
                return desc

        return None
