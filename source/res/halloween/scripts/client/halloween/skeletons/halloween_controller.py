# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Any
    from halloween_common.configs.halloween_gsw import GSWModel
    from halloween.gui.game_control.halloween_controller import _HalloweenConfig
    from Event import Event

class IHalloweenController(IGameController):
    onSettingsUpdate = None
    onEventDisabled = None

    def isEnabled(self):
        raise NotImplementedError

    def isBattlesEnabled(self):
        raise NotImplementedError

    def isPromoScreenEnabled(self):
        raise NotImplementedError

    def isIntroVideoEnabled(self):
        raise NotImplementedError

    def isOutroVideoEnabled(self):
        raise NotImplementedError

    def isInfoPageEnabled(self):
        raise NotImplementedError

    def isInfoMetaEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def getHWQuestsCache(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    @staticmethod
    def getGSWConfig():
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

    def hasAccessToVehicle(self, vehTypeCD):
        raise NotImplementedError

    @property
    def remainingEventSeconds(self):
        raise NotImplementedError
