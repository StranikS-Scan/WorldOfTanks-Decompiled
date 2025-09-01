# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_controller import _LSConfig, _VehiclesConfig
    from Event import Event

class ILSController(IGameController):
    onSettingsUpdate = None
    onEventDisabled = None

    @property
    def lootBoxesEvent(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isBattlesEnabled(self):
        raise NotImplementedError

    def isPromoScreenEnabled(self):
        raise NotImplementedError

    def isIntroVideoEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def selectBattle(self, *args, **kwargs):
        raise NotImplementedError

    def openHangar(self):
        raise NotImplementedError

    def isEventPrb(self):
        raise NotImplementedError

    def selectRandomMode(self):
        raise NotImplementedError

    def selectVehicle(self, invID):
        raise NotImplementedError

    def getVehiclesConfig(self):
        raise NotImplementedError

    def getSuitableVehicles(self):
        raise NotImplementedError
