# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/phase_indicator.py
import BigWorld
from typing import Optional
from gui.impl import backport
from gui.impl.gen import R
from historical_battles_common.hb_constants import GoalState, GoalId
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from ArenaPhasesComponent import ArenaPhasesComponent
from HBGoalComponent import HBGoalComponent
from historical_battles.gui.Scaleform.daapi.view.meta.HBPhaseIndicatorMeta import HBPhaseIndicatorMeta
from historical_battles.gui.Scaleform.genConsts.HB_PHASE_INDICATOR_STATE import HB_PHASE_INDICATOR_STATE

def _getDefaultFrontStateType():
    stateTypes = {ARENA_BONUS_TYPE.HB_OFFENCE: HB_PHASE_INDICATOR_STATE.OFFENCE,
     ARENA_BONUS_TYPE.HB_DEFENCE: HB_PHASE_INDICATOR_STATE.DEFENCE}
    return stateTypes.get(BigWorld.player().arena.bonusType)


class HistoricalBattlesPhaseIndicator(HBPhaseIndicatorMeta):
    __GOAL_TO_STATE_MAP = {GoalId.OFFENCE_MAIN.value: HB_PHASE_INDICATOR_STATE.OFFENCE,
     GoalId.OFFENCE_COUNTER_ATTACKER.value: HB_PHASE_INDICATOR_STATE.DEFENCE,
     GoalId.BOSS.value: HB_PHASE_INDICATOR_STATE.BOSS,
     GoalId.BOSS_ONE.value: HB_PHASE_INDICATOR_STATE.BOSS,
     GoalId.BOSS_FEW.value: HB_PHASE_INDICATOR_STATE.BOSS,
     GoalId.DEFENCE_COUNTER_ATTACK.value: HB_PHASE_INDICATOR_STATE.OFFENCE,
     GoalId.DEFENCE_SPG.value: HB_PHASE_INDICATOR_STATE.DEFENCE}

    def __init__(self):
        super(HistoricalBattlesPhaseIndicator, self).__init__()
        self.__isVisible = False
        self.__stateType = _getDefaultFrontStateType()
        self.__currentPhase = 0
        self.__phasesCount = 0
        self.__wavesCount = 0
        self.__currentWave = 0
        self.__isOffence = BigWorld.player().arena.bonusType == ARENA_BONUS_TYPE.HB_OFFENCE

    def _populate(self):
        super(HistoricalBattlesPhaseIndicator, self)._populate()
        ArenaPhasesComponent.onPhasesUpdate += self.__phaseUpdate
        HBGoalComponent.onGoalsUpdated += self.__goalsUpdate

    def _dispose(self):
        ArenaPhasesComponent.onPhasesUpdate -= self.__phaseUpdate
        HBGoalComponent.onGoalsUpdated -= self.__goalsUpdate
        super(HistoricalBattlesPhaseIndicator, self)._dispose()

    def _setVisible(self, value):
        if self.__isVisible != value:
            self.__isVisible = value
            self.as_setVisibleS(value)

    def __goalsUpdate(self, goalsInfo):
        if goalsInfo:
            lastGoal = goalsInfo[-1]
            self.__stateType = self.__GOAL_TO_STATE_MAP.get(lastGoal['id'], HB_PHASE_INDICATOR_STATE.DEFENCE)
            if lastGoal['state'] == GoalState.LOSE or lastGoal['state'] == GoalState.WIN and self.__currentPhase == self.__phasesCount:
                self._setVisible(False)
            self.__update()

    def __phaseUpdate(self, arenaPhases):
        self._setVisible(arenaPhases is not None and arenaPhases.canShow())
        self.__currentPhase = arenaPhases.currentPhase
        self.__phasesCount = arenaPhases.phasesCount
        self.__wavesCount = arenaPhases.wavesCount
        self.__currentWave = arenaPhases.currentWave
        self.__update()
        return

    def __update(self):
        if not self.__isVisible:
            return
        state = backport.text(R.strings.hb_battle.phaseIndicator.state.dyn(self.__stateType)())
        self.as_setDataS({'state': self.__stateType,
         'phase': backport.text(R.strings.hb_battle.phaseIndicator.phase(), current=self.__currentPhase, total=self.__phasesCount, state=state),
         'wave': '' if self.__wavesCount <= 1 or self.__isOffence else backport.text(R.strings.hb_battle.phaseIndicator.wave(), current=self.__currentWave, total=self.__wavesCount)})
