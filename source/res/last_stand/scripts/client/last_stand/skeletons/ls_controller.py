# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_controller import _LSConfig, _VehiclesConfig
    from Event import Event
    from gui.shared.utils.requesters import RequestCriteria

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

    def isInfoPageEnabled(self):
        raise NotImplementedError

    def isMetaInfoEnabled(self):
        raise NotImplementedError

    def isLootBoxEntryPointEnabled(self):
        raise NotImplementedError

    def isParallaxEnabled(self):
        raise NotImplementedError

    def isHangar3dPointVisible(self):
        raise NotImplementedError

    def isHangar3dPointRewardVisible(self):
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

    def getVehiclesConfig(self):
        raise NotImplementedError

    def getSuitableVehicles(self, criteria=None):
        raise NotImplementedError

    def getVehiclesCriteria(self):
        raise NotImplementedError
