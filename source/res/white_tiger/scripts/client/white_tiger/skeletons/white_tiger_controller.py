# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/skeletons/white_tiger_controller.py
from typing import Dict
from Event import Event
from skeletons.gui.game_control import IGameController, ISeasonProvider

class IWhiteTigerController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onEventPrbChanged = None
    onEventEnded = None

    def isEnabled(self):
        raise NotImplementedError

    def isInAnnouncement(self):
        raise NotImplementedError

    def isPromoScreenEnabled(self):
        raise NotImplementedError

    def isEventPrbActive(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getTimeLeft(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getWTVehicles(self):
        raise NotImplementedError

    def openHangar(self):
        raise NotImplementedError

    def selectBattle(self, callback=None):
        raise NotImplementedError

    def getSquadConfig(self):
        raise NotImplementedError

    def selectRandomMode(self):
        raise NotImplementedError

    def selectVehicle(self, invID=0):
        raise NotImplementedError

    def isInWhiteTigerMode(self):
        raise NotImplementedError

    def isSelectedVehicleWTVehicle(self):
        raise NotImplementedError

    def getEndDate(self):
        raise NotImplementedError

    def getStartDate(self):
        raise NotImplementedError
