# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/indicators.py
from helpers import dependency
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN, VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator, SixthSenseIndicator
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from white_tiger_common.wt_constants import WT_COMPONENT_NAMES
from wt_settings import g_wt_config

def createDamageIndicator():
    return WhiteTigerDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


_BOSS_DAMAGE_INDICATOR_ALPHA_PER_GENERATOR = {0: 1,
 1: 0.8,
 2: 0.6,
 3: 0.4,
 4: 0.2}

class WhiteTigerDamageIndicator(_DamageIndicator):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hitsCount):
        super(WhiteTigerDamageIndicator, self).__init__(hitsCount)
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter += self.__onPublicCounter
            feedback.onArenaTimer += self.__onArenaTimer
        self.__isBoss = False
        self.__generatorsLeft = 0
        self.__debufActive = False
        root = self.movie.root.dmgIndicator
        self._as_setAlpha = root.as_setAlpha

    def invalidateSettings(self, diff=None):
        super(WhiteTigerDamageIndicator, self).invalidateSettings(diff)
        info = self.sessionProvider.getCtx().getVehicleInfo(avatar_getter.getPlayerVehicleID())
        vehCD = info.vehicleType.compactDescr
        self.__isBoss = g_wt_config.isAnyTypeBoss(vehCD)

    def destroy(self):
        feedback = self.sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter -= self.__onPublicCounter
            feedback.onArenaTimer -= self.__onArenaTimer
        self._as_setAlpha = None
        super(WhiteTigerDamageIndicator, self).destroy()
        return

    def showHitDirection(self, idx, hitData, timeLeft):
        if self.__isBoss:
            generatorLeft = 0 if self.__debufActive else self.__generatorsLeft
            alpha = _BOSS_DAMAGE_INDICATOR_ALPHA_PER_GENERATOR.get(generatorLeft, 1)
            self.as_setAlphaS(idx, alpha)
        super(WhiteTigerDamageIndicator, self).showHitDirection(idx, hitData, timeLeft)

    def as_setAlphaS(self, itemIdx, alpha):
        self._as_setAlpha(itemIdx, alpha)

    def __onPublicCounter(self, count, maxCount, counterName):
        if counterName == WT_COMPONENT_NAMES.GENERATORS_COUNTER:
            self.__generatorsLeft = count

    def __onArenaTimer(self, name, remainingTime):
        if name == WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER:
            self.__debufActive = remainingTime > 0


class WTSixthSenseIndicator(SixthSenseIndicator):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTSixthSenseIndicator, self).__init__()
        self.__isBoss = False
        self.__ignoreObservation = False
        self.__isSpotted = False

    def _populate(self):
        super(WTSixthSenseIndicator, self)._populate()
        info = self.sessionProvider.getCtx().getVehicleInfo(avatar_getter.getPlayerVehicleID())
        vehCD = info.vehicleType.compactDescr
        self.__isBoss = g_wt_config.isAnyTypeBoss(vehCD)

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.WT_BOSS_INVISIBILITY and self.__isBoss:
            self.__handleLantern(value)
            return
        if state != VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            return
        self.__isSpotted = bool(value)
        if not self.__ignoreObservation:
            super(WTSixthSenseIndicator, self)._onVehicleStateUpdated(state, value)

    def __handleLantern(self, value):
        self.__ignoreObservation = value.visible
        observed = int(not self.__ignoreObservation and self.__isSpotted)
        super(WTSixthSenseIndicator, self)._onVehicleStateUpdated(VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY, observed)
