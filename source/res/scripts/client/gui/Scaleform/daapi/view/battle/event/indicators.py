# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/indicators.py
from gui.wt_event.wt_event_helpers import isBoss
from helpers import dependency
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.Scaleform.daapi.view.battle.shared.indicators import DamageIndicator
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
_SHIELD_DEBUFF_ARENA_TIMER = 'wtShieldDebuffDuration'

def createDamageIndicator():
    return WTDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


_BOSS_DAMAGE_INDICATOR_ALPHA_PER_GENERATOR = {0: 1,
 1: 0.8,
 2: 0.6,
 3: 0.4,
 4: 0.2}

class WTDamageIndicator(DamageIndicator):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hitsCount):
        super(WTDamageIndicator, self).__init__(hitsCount)
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter += self.__onPublicCounter
            feedback.onArenaTimer += self.__onArenaTimer
        self.__isBoss = False
        self.__generatorsLeft = 0
        self.__debufActive = False

    def invalidateSettings(self, diff=None):
        super(WTDamageIndicator, self).invalidateSettings(diff)
        info = self.sessionProvider.getCtx().getVehicleInfo(avatar_getter.getPlayerVehicleID())
        self.__isBoss = isBoss(info.vehicleType.tags)

    def destroy(self):
        super(WTDamageIndicator, self).destroy()
        feedback = self.sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter -= self.__onPublicCounter
            feedback.onArenaTimer -= self.__onArenaTimer

    def showHitDirection(self, idx, hitData, timeLeft):
        if self.__isBoss:
            generatorLeft = 0 if self.__debufActive else self.__generatorsLeft
            alpha = _BOSS_DAMAGE_INDICATOR_ALPHA_PER_GENERATOR.get(generatorLeft, 1)
            self.as_setAlphaS(idx, alpha)
        super(WTDamageIndicator, self).showHitDirection(idx, hitData, timeLeft)

    def __onPublicCounter(self, count, maxCount):
        self.__generatorsLeft = count

    def __onArenaTimer(self, name, totalTime, remainingTime):
        if name == _SHIELD_DEBUFF_ARENA_TIMER:
            self.__debufActive = remainingTime > 0
