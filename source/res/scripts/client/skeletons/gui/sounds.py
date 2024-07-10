# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/sounds.py
import typing
from gui.battle_control.controllers.interfaces import IBattleController

class ISoundsController(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self, isDisconnected=False):
        raise NotImplementedError

    @property
    def system(self):
        raise NotImplementedError

    def enable(self):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def setEnvForSpace(self, spaceID, newEnv):
        raise NotImplementedError


class IShotsResultSoundController(IBattleController):

    def getBestSoundEventName(self, bestSound):
        raise NotImplementedError

    def getBestShotResultSound(self, currBest, newSoundName, otherData):
        raise NotImplementedError

    def getVehicleHitResultSound(self, enemyVehID, hitFlags, enemiesHitCount):
        raise NotImplementedError
