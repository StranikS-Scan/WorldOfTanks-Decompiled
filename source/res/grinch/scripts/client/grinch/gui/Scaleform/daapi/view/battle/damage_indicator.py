# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/damage_indicator.py
import BigWorld
from Math import Matrix
from grinch.gui.Scaleform.daapi.view.battle.grinch_hud import GrinchHudComponent
from gui.battle_control.controllers.hit_direction_ctrl import IHitIndicator, HitType
from gui.battle_control.controllers.hit_direction_ctrl.hit_data import HitData
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class GrinchDamageIndicator(IHitIndicator, GrinchHudComponent):
    _INDICATOR_DURATION = 3
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, alias):
        super(GrinchDamageIndicator, self).__init__()
        self._alias = alias

    @property
    def alias(self):
        return self._alias

    def getHitType(self):
        return HitType.HIT_DAMAGE

    def destroy(self):
        pass

    def getDuration(self):
        return self._INDICATOR_DURATION

    def getBeginAnimationDuration(self):
        pass

    def setVisible(self, flag):
        pass

    def showHitDirection(self, idx, hitData, timeLeft):
        attacker = BigWorld.entity(hitData.getAttackerID())
        matrix = Matrix(attacker.matrix)
        self.hud.addHitDirection(idx, matrix, not hitData.isBlocked())

    def invalidateSettings(self, diff=None):
        pass

    def hideHitDirection(self, idx):
        self.hud.hideHitDirection(idx)
