# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/NotificationsController.py
import weakref
import BigWorld
from CTFManager import g_ctfManager
from gui.battle_control.arena_info import isFalloutMultiTeam
from gui.battle_control.avatar_getter import getSoundNotifications

class NotificationsController(object):

    def __init__(self, arenaDP):
        super(NotificationsController, self).__init__()
        self.__ui = None
        self.__arenaDP = weakref.proxy(arenaDP)
        self.__playerVehicleID = None
        self.__playerTeam = None
        self.__isTeamPlayer = False
        self.__soundNotifications = None
        self.__captureSndName = 'take_flag'
        self.__deliveredSndName = 'deliver_flag'
        self.__consumedSndName = 'consumed_flag'
        self.__enemyCaptureSndName = 'enemy_take_flag'
        self.__allyCaptureSndName = 'ally_take_flag'
        self.__allyDroppedSndName = 'ally_drop_flag'
        self.__allyDeliveredSndName = 'ally_deliver_flag'
        return

    def start(self, ui):
        self.__ui = weakref.proxy(ui)
        player = BigWorld.player()
        self.__playerVehicleID = player.playerVehicleID
        self.__playerTeam = player.team
        self.__soundNotifications = weakref.proxy(getSoundNotifications())
        arena = player.arena
        arenaType = arena.arenaType
        self.__isTeamPlayer = self.__playerTeam in arenaType.squadTeamNumbers if isFalloutMultiTeam() else True
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved += self.__onFlagRemoved
        if g_ctfManager.getVehicleCarriedFlagID(self.__playerVehicleID) is not None:
            self.__ui.showFlagCaptured()
        return

    def stop(self):
        self.__ui = None
        self.__arenaDP = None
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        g_ctfManager.onFlagRemoved -= self.__onFlagRemoved
        return

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        vehInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        if vehicleID == self.__playerVehicleID:
            self.__soundNotifications.play(self.__captureSndName)
            self.__ui.showFlagCaptured()
        elif vehInfo.team == self.__playerTeam:
            self.__soundNotifications.play(self.__allyCaptureSndName)
        else:
            self.__soundNotifications.play(self.__enemyCaptureSndName)

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        vehInfo = self.__arenaDP.getVehicleInfo(vehicleID)
        if vehicleID == self.__playerVehicleID:
            if self.__isTeamPlayer:
                self.__soundNotifications.play(self.__deliveredSndName)
                self.__ui.showFlagDelivered()
            else:
                self.__soundNotifications.play(self.__consumedSndName)
                self.__ui.showFlagAbsorbed()
        elif vehInfo.team == self.__playerTeam:
            self.__soundNotifications.play(self.__allyDeliveredSndName)

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        vehInfo = self.__arenaDP.getVehicleInfo(loserVehicleID)
        if loserVehicleID == self.__playerVehicleID:
            self.__ui.showFlagDropped()
        elif vehInfo.team == self.__playerTeam:
            self.__soundNotifications.play(self.__allyDroppedSndName)

    def __onFlagRemoved(self, flagID, flagTeam, vehicleID):
        if vehicleID == self.__playerVehicleID:
            self.__ui.showFlagDropped()
