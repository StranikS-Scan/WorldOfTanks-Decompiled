# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/extension_stubs/fun_random_controller.py
import logging
from Event import Event, EventManager
from gui.game_control.season_provider import SeasonProvider
from gui.periodic_battles.models import AlertData
from skeletons.gui.game_control import IFunRandomController
from helpers.server_settings import FunRandomConfig
_logger = logging.getLogger(__name__)

class FunRandomController(IFunRandomController, SeasonProvider):

    def __init__(self):
        super(FunRandomController, self).__init__()
        self.__em = EventManager()
        self.onUpdated = Event(self.__em)
        self.onGameModeStatusTick = Event(self.__em)
        self.onGameModeStatusUpdated = Event(self.__em)

    def fini(self):
        self.__em.clear()
        super(FunRandomController, self).fini()

    def isEnabled(self):
        return False

    def isFunRandomPrbActive(self):
        return False

    def isSuitableVehicle(self, vehicle, isSquad=False):
        return False

    def isSuitableVehicleAvailable(self):
        return False

    def hasSuitableVehicles(self):
        return False

    def canGoToMode(self):
        return False

    def getAlertBlock(self):
        return (lambda *_: None, AlertData(), False)

    def getModeSettings(self):
        return FunRandomConfig()

    def getModifiersDataProvider(self):
        return None

    def selectFunRandomBattle(self):
        pass
