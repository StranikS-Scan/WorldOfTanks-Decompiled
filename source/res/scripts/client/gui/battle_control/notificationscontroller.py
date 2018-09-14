# Embedded file name: scripts/client/gui/battle_control/NotificationsController.py
import weakref
import BigWorld
from CTFManager import g_ctfManager

class NotificationsController(object):

    def __init__(self):
        super(NotificationsController, self).__init__()
        self.__ui = None
        return

    def start(self, ui):
        self.__ui = weakref.proxy(ui)
        g_ctfManager.onFlagCapturedByVehicle += self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed += self.__onFlagAbsorbed
        g_ctfManager.onFlagDroppedToGround += self.__onFlagDroppedToGround
        if g_ctfManager.isFlagBearer(BigWorld.player().playerVehicleID):
            self.__ui.showFlagCaptured()

    def stop(self):
        self.__ui = None
        g_ctfManager.onFlagCapturedByVehicle -= self.__onFlagCapturedByVehicle
        g_ctfManager.onFlagAbsorbed -= self.__onFlagAbsorbed
        return

    def __onFlagCapturedByVehicle(self, flagID, vehicleID):
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__ui.showFlagCaptured()

    def __onFlagAbsorbed(self, flagID, vehicleID, respawnTime):
        if vehicleID == BigWorld.player().playerVehicleID:
            self.__ui.showFlagDelivered()

    def __onFlagDroppedToGround(self, flagID, loserVehicleID, flagPos, respawnTime):
        if loserVehicleID == BigWorld.player().playerVehicleID:
            self.__ui.showFlagDropped()
