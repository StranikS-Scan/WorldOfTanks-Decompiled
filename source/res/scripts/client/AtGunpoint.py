# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AtGunpoint.py
import BigWorld
from helpers import dependency
from math_utils import almostZero
from skeletons.gui.battle_session import IBattleSessionProvider

class AtGunpoint(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        BigWorld.DynamicScriptComponent.__init__(self)

    def onDestroy(self):
        if self.entity.isMyVehicle:
            if self.attackers is not None:
                for hitYaw in self.attackers:
                    self.__guiSessionProvider.shared.hitDirection.removeArtyHitPrediction(hitYaw)

        return

    def setSlice_attackers(self, _, prev):
        if self.entity.isMyVehicle:
            if self.attackers is not None and self.entity.isAlive():
                for hitYaw in self.attackers:
                    if not prev or all((not almostZero(hitYaw - prevHitYaw) for prevHitYaw in prev)):
                        self.__guiSessionProvider.shared.hitDirection.addArtyHitPrediction(hitYaw)

            if prev is not None:
                for prevHitYaw in prev:
                    if not self.attackers or all((not almostZero(prevHitYaw - hitYaw) for hitYaw in self.attackers)):
                        self.__guiSessionProvider.shared.hitDirection.removeArtyHitPrediction(prevHitYaw)

        return
