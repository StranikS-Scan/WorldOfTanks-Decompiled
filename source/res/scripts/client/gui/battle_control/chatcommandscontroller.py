# Embedded file name: scripts/client/gui/battle_control/ChatCommandsController.py
import weakref
import math
import BigWorld
import BattleReplay
from chat_shared import CHAT_COMMANDS
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.BattleContext import g_battleContext
from gui.arena_info import getPlayerVehicleID
from gui.battle_control import avatar_getter
from messenger import MessengerEntry
from messenger.proto.bw.battle_chat_cmd import SendChatCommandDecorator
from messenger.proto.bw.find_criteria import BWBattleTeamChannelFindCriteria
from messenger.proto.events import g_messengerEvents

class ChatCommandsController(object):

    def __init__(self):
        super(ChatCommandsController, self).__init__()
        self.__battleUI = None
        return

    def start(self, battleUI):
        self.__battleUI = weakref.proxy(battleUI)
        g_messengerEvents.channels.onCommandReceived += self.__me_onCommandReceived
        BattleReplay.g_replayCtrl.onCommandReceived += self.__me_onCommandReceived

    def stop(self):
        self.__battleUI = None
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__me_onCommandReceived
        return

    def sendAttentionToCell(self, cellIdx):
        if avatar_getter.isForcedGuiControlMode():
            self.__sendChatCommand(SendChatCommandDecorator(CHAT_COMMANDS.ATTENTIONTOCELL, second=cellIdx))

    def sendCommand(self, cmdName):
        if not avatar_getter.isVehicleAlive():
            return
        else:
            command = CHAT_COMMANDS.lookup(cmdName)
            if command is None:
                LOG_ERROR('Command not found', cmdName)
                return
            if command == CHAT_COMMANDS.RELOADINGGUN:
                decorator = self.__getReloadingCommand()
            else:
                decorator = SendChatCommandDecorator(command)
            if decorator:
                self.__sendChatCommand(decorator)
            return

    def sendTargetedCommand(self, cmdName, targetID):
        if not avatar_getter.isVehicleAlive():
            return
        elif targetID is None:
            return
        else:
            command = CHAT_COMMANDS.lookup(cmdName)
            if command is None:
                LOG_ERROR('Command not found', cmdName)
                return
            self.__sendChatCommand(SendChatCommandDecorator(command, first=targetID))
            return

    def __playSound(self, cmd):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(cmd.getSoundEventName())

    def __findVehicleInfoByDatabaseID(self, dbID):
        result = None
        vehicleID = g_battleContext.getVehIDByAccDBID(dbID)
        if vehicleID:
            result = self.__findVehicleInfoByVehicleID(vehicleID)
        return result

    def __findVehicleInfoByVehicleID(self, vehicleID):
        result = None
        vehicleInfo = g_battleContext.arenaDP.getVehicleInfo(vehicleID)
        if vehicleInfo.isAlive() and not vehicleInfo.isObserver():
            result = vehicleInfo
        return result

    def __showVehicleMarker(self, vehicleID, markerName):
        if vehicleID == getPlayerVehicleID():
            return
        else:
            entity = BigWorld.entity(vehicleID)
            if entity is not None and entity.isStarted:
                self.__battleUI.vMarkersManager.showActionMarker(entity.marker, markerName)
            return

    def __getReloadingCommand(self):
        if not avatar_getter.isPlayerOnArena():
            return None
        else:
            inputHandler = avatar_getter.getInputHandler()
            if not inputHandler:
                return None
            aim = inputHandler.aim
            if not aim:
                return None
            reloadingTimeLeft = math.ceil(aim.getReloadingTimeLeft())
            ammoQuantityLeft = aim.getAmmoQuantityLeft()
            command = CHAT_COMMANDS.RELOADINGGUN
            first, second = (0, 0)
            if reloadingTimeLeft > 0:
                first = reloadingTimeLeft
                if aim.isCasseteClip():
                    if ammoQuantityLeft > 0:
                        command = CHAT_COMMANDS.RELOADING_CASSETE
                        second = ammoQuantityLeft
            elif ammoQuantityLeft == 0:
                command = CHAT_COMMANDS.RELOADING_UNAVAILABLE
            elif aim.isCasseteClip():
                command = CHAT_COMMANDS.RELOADING_READY_CASSETE
                first = ammoQuantityLeft
            else:
                command = CHAT_COMMANDS.RELOADING_READY
            return SendChatCommandDecorator(command, first, second)

    def __sendChatCommand(self, command):
        controls = MessengerEntry.g_instance.gui.channelsCtrl
        controller = controls.getControllerByCriteria(BWBattleTeamChannelFindCriteria())
        if controller:
            controller.sendCommand(command)

    def __handleSimpleCommand(self, cmd):
        vMarker = cmd.getVehMarker()
        if vMarker:
            vehicleInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
            vehicleID = vehicleInfo.vehicleID if vehicleInfo else 0
            if vehicleID:
                self.__showVehicleMarker(vehicleID, vMarker)
                self.__battleUI.minimap.showActionMarker(vehicleID, vMarker)

    def __handlePrivateCommand(self, cmd):
        vehicleInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if cmd.isReceiver() or cmd.isSender():
            self.__playSound(cmd)
            if vehicleInfo is None:
                vehicleInfo = self.__findVehicleInfoByVehicleID(getPlayerVehicleID())
            vehicleID = vehicleInfo.vehicleID if vehicleInfo else 0
            vehMarker = cmd.getVehMarker(vehicle=vehicleInfo)
            if vehMarker and vehicleID:
                self.__showVehicleMarker(vehicleID, vehMarker)
                self.__battleUI.minimap.showActionMarker(vehicleID, cmd.getVehMarker())
        return

    def __handlePublicCommand(self, cmd):
        senderInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if senderInfo is None:
            senderInfo = self.__findVehicleInfoByVehicleID(getPlayerVehicleID())
        showReceiver = cmd.showMarkerForReceiver()
        recvMarker, senderMarker = cmd.getVehMarkers(vehicle=senderInfo)
        receiverID = cmd.getFirstTargetID()
        senderID = senderInfo.vehicleID if senderInfo else 0
        minimap = self.__battleUI.minimap
        if showReceiver:
            if receiverID:
                minimap.showActionMarker(receiverID, recvMarker)
                self.__showVehicleMarker(receiverID, recvMarker)
            if senderID:
                minimap.showActionMarker(senderID, senderMarker)
                self.__showVehicleMarker(senderID, senderMarker)
        elif senderID:
            minimap.showActionMarker(senderID, recvMarker)
            self.__showVehicleMarker(senderID, recvMarker)
        return

    def __me_onCommandReceived(self, cmd):
        if cmd.isIgnored():
            LOG_DEBUG('Chat command is ignored', cmd)
            return
        if cmd.getCommandIndex() == CHAT_COMMANDS.ATTENTIONTOCELL.index():
            self.__battleUI.minimap.markCell(cmd.getSecondTargetID(), 3.0)
        elif cmd.isPrivate():
            self.__handlePrivateCommand(cmd)
        else:
            self.__playSound(cmd)
            if cmd.isPublic():
                self.__handlePublicCommand(cmd)
            else:
                self.__handleSimpleCommand(cmd)
