# Embedded file name: scripts/client/gui/battle_control/NotificationsController.py
import weakref
import BigWorld
from CTFManager import g_ctfManager

class NotificationsController(object):

    def __init__(self, arenaDP):
        super(NotificationsController, self).__init__()
        self.__ui = None
        self.__arenaDP = weakref.proxy(arenaDP)
        self.__isSolo = False
        return

    def start(self, ui):
        self.__ui = weakref.proxy(ui)
        vehicleID = BigWorld.player().playerVehicleID
        self.__isSolo = not self.__arenaDP.isSquadMan(vehicleID)
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        if g_ctfManager.isFlagBearer(vehicleID):
            self.__ui.showFlagCaptured()

    def stop(self):
        self.__ui = None
        self.__arenaDP = None
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround -= self.__onFlagDroppedToGround
        return

    def __onFlagCapturedByVehicle(self, flagID, flagTeam, vehicleID):
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__ui.showFlagCaptured()

    def __onFlagAbsorbed(self, flagID, flagTeam, vehicleID, respawnTime):
        if vehicleID == BigWorld.player().playerVehicleID:
            if self.__isSolo:
                self.__ui.showFlagAbsorbed()
            else:
                self.__ui.showFlagDelivered()

    def __onFlagDroppedToGround(self, flagID, flagTeam, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == BigWorld.player().playerVehicleID:
            self.__ui.showFlagDropped()
