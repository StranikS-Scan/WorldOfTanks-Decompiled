# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AtGunpoint.py
import BigWorld
from helpers import dependency
from math_utils import almostZero
from skeletons.gui.battle_session import IBattleSessionProvider
ARTY_HIT_PREDICTION_EPSILON_YAW = 1e-05

class AtGunpoint(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        BigWorld.DynamicScriptComponent.__init__(self)

    def _avatar(self):
        avatar = BigWorld.player()
        if avatar.isObserver():
            attachedVehicle = avatar.getVehicleAttached()
            if not attachedVehicle or attachedVehicle.id != self.entity.id:
                return None
        return avatar

    def onDestroy(self):
        if self.entity.isMyVehicle:
            if self.attackers is not None:
                for hitYaw in self.attackers:
                    self.__guiSessionProvider.shared.hitDirection.removeArtyHitPrediction(hitYaw)

        return

    def setSlice_attackers(self, path, prev):
        if self.entity.isMyVehicle:
            if self.attackers is not None and self.entity.isAlive():
                newAttackers = self.attackers[path[-1][0]:path[-1][1]]
                for hitYaw in newAttackers:
                    if not prev or all((not self.__isSameYaw(prevHitYaw, hitYaw) for prevHitYaw in prev)):
                        if self._avatar() is not None:
                            self.__guiSessionProvider.shared.hitDirection.addArtyHitPrediction(hitYaw)

            if prev is not None:
                for prevHitYaw in prev:
                    if not self.attackers or all((not self.__isSameYaw(prevHitYaw, hitYaw) for hitYaw in self.attackers)):
                        self.__guiSessionProvider.shared.hitDirection.removeArtyHitPrediction(prevHitYaw)

        return

    def __isSameYaw(self, a, b):
        return almostZero(a - b, epsilon=ARTY_HIT_PREDICTION_EPSILON_YAW)
