# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/chat_cmd_ctrl.py
import math
import weakref
import CommandMapping
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, GUN_RELOADING_VALUE_TYPE
from gui.battle_control.controllers.interfaces import IBattleController
from messenger import MessengerEntry
from messenger.m_constants import MESSENGER_COMMAND_TYPE, PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents

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
DEFAULT_CUT = 'default'
ALLY_CUT = 'ally'
ENEMY_CUT = 'enemy'
ENEMY_SPG_CUT = 'enemy_spg'
TARGET_TRANSLATION_MAPPING = {CHAT_COMMANDS.ATTACKENEMY: {ALLY_CUT: CHAT_COMMANDS.FOLLOWME,
                             ENEMY_CUT: CHAT_COMMANDS.SUPPORTMEWITHFIRE,
                             ENEMY_SPG_CUT: CHAT_COMMANDS.ATTACKENEMY},
 CHAT_COMMANDS.BACKTOBASE: {ALLY_CUT: CHAT_COMMANDS.TURNBACK},
 CHAT_COMMANDS.SOS: {ALLY_CUT: CHAT_COMMANDS.HELPME},
 CHAT_COMMANDS.RELOADINGGUN: {ALLY_CUT: CHAT_COMMANDS.STOP}}

class ChatCommandsController(IBattleController):
    """Controller of chat commands in battle. It shows markers in minimap,
    on vehicles. Also it sends chat commands to battle team channel.
    """
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
        """Starts to controlling."""
        g_messengerEvents.channels.onCommandReceived += self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived += self.__me_onCommandReceived

    def stopControl(self):
        """Stops to controlling."""
        self.__arenaDP = None
        self.__feedback = None
        self.__ammo = None
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__me_onCommandReceived
        return

    def handleShortcutChatCommand(self, key):
        cmdMap = CommandMapping.g_instance
        import BigWorld
        player = BigWorld.player()
        target = BigWorld.target()
        for chatCmd, keyboardCmd in KB_MAPPING.iteritems():
            if cmdMap.isFired(keyboardCmd, key):
                action = chatCmd
                crosshairType = self.__getCrosshairType(player, target)
                if crosshairType != DEFAULT_CUT and chatCmd in TARGET_TRANSLATION_MAPPING and crosshairType in TARGET_TRANSLATION_MAPPING[chatCmd]:
                    action = TARGET_TRANSLATION_MAPPING[chatCmd][crosshairType]
                if action in TARGET_ACTIONS:
                    if crosshairType != DEFAULT_CUT:
                        self.handleChatCommand(action, targetID=target.id)
                else:
                    self.handleChatCommand(action)

    def handleChatCommand(self, action, targetID=None):
        if action in TARGET_ACTIONS:
            self.sendTargetedCommand(action, targetID)
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

    def sendCommand(self, cmdName):
        if not avatar_getter.isVehicleAlive():
            return
        command = self.proto.battleCmd.createByName(cmdName)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Command is not found', cmdName)

    def sendTargetedCommand(self, cmdName, targetID):
        if not avatar_getter.isVehicleAlive():
            return
        command = self.proto.battleCmd.createByNameTarget(cmdName, targetID)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Targeted command is not found or targetID is not defined', cmdName)

    def sendReloadingCommand(self):
        if not avatar_getter.isPlayerOnArena():
            return
        state = self.__ammo.getGunReloadingState()
        if state.getValueType() != GUN_RELOADING_VALUE_TYPE.TIME:
            LOG_ERROR('Chat reloading command is not allowed')
            return
        command = self.proto.battleCmd.create4Reload(self.__ammo.getGunSettings().isCassetteClip(), math.ceil(state.getTimeLeft()), self.__ammo.getShellsQuantityLeft())
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Can not create reloading command')

    def __playSound(self, cmd):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(cmd.getSoundEventName())

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
        if cmd.isOnMinimap():
            self.__feedback.markCellOnMinimap(cmd.getCellIndex())
        elif cmd.isPrivate():
            self.__handlePrivateCommand(cmd)
        else:
            self.__playSound(cmd)
            if cmd.isPublic():
                self.__handlePublicCommand(cmd)
            else:
                self.__handleSimpleCommand(cmd)

    def __getCrosshairType(self, player, target):
        outcome = DEFAULT_CUT
        if self.__isTargetCorrect(player, target):
            if target.publicInfo.team == player.team:
                outcome = ALLY_CUT
            elif 'SPG' in self.__getCurrentVehicleDesc(player)['vehicleType'].type.tags:
                outcome = ENEMY_SPG_CUT
            else:
                outcome = ENEMY_CUT
        return outcome

    def __isTargetCorrect(self, player, target):
        import Vehicle
        from helpers import isPlayerAvatar
        if target is not None and isinstance(target, Vehicle.Vehicle):
            if target.isAlive():
                if player is not None and isPlayerAvatar():
                    vInfo = self.__arenaDP.getVehicleInfo(target.id)
                    return not vInfo.isActionsDisabled()
        return False

    def __getCurrentVehicleDesc(self, player):
        vehicles = player.arena.vehicles
        for vID, desc in vehicles.items():
            if vID == player.playerVehicleID:
                return desc
