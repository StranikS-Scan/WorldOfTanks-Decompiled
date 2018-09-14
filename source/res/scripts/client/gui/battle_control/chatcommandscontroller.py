# Embedded file name: scripts/client/gui/battle_control/ChatCommandsController.py
import weakref
import math
import BigWorld
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter
from messenger import MessengerEntry
from messenger.m_constants import MESSENGER_COMMAND_TYPE
from messenger.proto import getBattleCommandFactory
from messenger.proto.events import g_messengerEvents

class ChatCommandsController(object):

    def __init__(self):
        super(ChatCommandsController, self).__init__()
        self.__battleUI = None
        self.__arenaDP = None
        self.__cmdFactories = None
        return

    def start(self, battleUI, arenaDP):
        self.__battleUI = weakref.proxy(battleUI)
        self.__arenaDP = arenaDP
        self.__cmdFactories = getBattleCommandFactory()
        g_messengerEvents.channels.onCommandReceived += self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived += self.__me_onCommandReceived

    def stop(self):
        self.__battleUI = None
        self.__arenaDP = None
        self.__cmdFactories = None
        g_messengerEvents.channels.onCommandReceived -= self.__me_onCommandReceived
        import BattleReplay
        BattleReplay.g_replayCtrl.onCommandReceived -= self.__me_onCommandReceived
        return

    def sendAttentionToCell(self, cellIdx):
        if avatar_getter.isForcedGuiControlMode():
            if not self.__cmdFactories:
                LOG_ERROR('Commands factory is not defined')
                return
            command = self.__cmdFactories.createByCellIdx(cellIdx)
            if command:
                self.__sendChatCommand(command)
            else:
                LOG_ERROR('Minimap command not found', cellIdx)

    def sendCommand(self, cmdName):
        if not avatar_getter.isVehicleAlive():
            return
        if not self.__cmdFactories:
            LOG_ERROR('Commands factory is not defined')
            return
        command = self.__cmdFactories.createByName(cmdName)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Command is not found', cmdName)

    def sendTargetedCommand(self, cmdName, targetID):
        if not avatar_getter.isVehicleAlive():
            return
        if not self.__cmdFactories:
            LOG_ERROR('Commands factory is not defined')
            return
        command = self.__cmdFactories.createByNameTarget(cmdName, targetID)
        if command:
            self.__sendChatCommand(command)
        else:
            LOG_ERROR('Targeted command is not found or targetID is not defined', cmdName)

    def sendReloadingCommand(self):
        if not avatar_getter.isPlayerOnArena():
            return
        inputHandler = avatar_getter.getInputHandler()
        if not inputHandler:
            return
        aim = inputHandler.aim
        if not aim:
            return
        command = self.__cmdFactories.create4Reload(aim.isCasseteClip(), math.ceil(aim.getReloadingTimeLeft()), aim.getAmmoQuantityLeft())
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

    def __showVehicleMarker(self, vehicleID, markerName):
        if vehicleID == avatar_getter.getPlayerVehicleID():
            return
        else:
            entity = BigWorld.entity(vehicleID)
            if entity is not None and entity.isStarted:
                self.__battleUI.vMarkersManager.showActionMarker(entity.marker, markerName)
            return

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
                self.__showVehicleMarker(vehicleID, vMarker)
                self.__battleUI.minimap.showActionMarker(vehicleID, vMarker)

    def __handlePrivateCommand(self, cmd):
        vehicleInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if cmd.isReceiver() or cmd.isSender():
            self.__playSound(cmd)
            if vehicleInfo is None:
                vehicleInfo = self.__findVehicleInfoByVehicleID(avatar_getter.getPlayerVehicleID())
            vehicleID = vehicleInfo.vehicleID if vehicleInfo else 0
            vehMarker = cmd.getVehMarker(vehicle=vehicleInfo)
            if vehMarker and vehicleID:
                self.__showVehicleMarker(vehicleID, vehMarker)
                self.__battleUI.minimap.showActionMarker(vehicleID, cmd.getVehMarker())
        return

    def __handlePublicCommand(self, cmd):
        senderInfo = self.__findVehicleInfoByDatabaseID(cmd.getSenderID())
        if senderInfo is None:
            senderInfo = self.__findVehicleInfoByVehicleID(avatar_getter.getPlayerVehicleID())
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
        if cmd.getCommandType() != MESSENGER_COMMAND_TYPE.BATTLE:
            return
        if cmd.isOnMinimap():
            self.__battleUI.minimap.markCell(cmd.getCellIndex(), 3.0)
        elif cmd.isPrivate():
            self.__handlePrivateCommand(cmd)
        else:
            self.__playSound(cmd)
            if cmd.isPublic():
                self.__handlePublicCommand(cmd)
            else:
                self.__handleSimpleCommand(cmd)
