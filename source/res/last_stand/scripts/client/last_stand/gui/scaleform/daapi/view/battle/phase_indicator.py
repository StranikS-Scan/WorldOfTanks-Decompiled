# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/phase_indicator.py
from typing import Optional
from LSArenaPhasesComponent import LSArenaPhasesComponent
from gui.impl import backport
from last_stand.gui.scaleform.daapi.view.meta.PhaseIndicatorMeta import PhaseIndicatorMeta
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.battle_session import IBattleSessionProvider
_R_INDICATOR = R.strings.last_stand_battle.arena
_PHASE = 'phase'
_WAVE = 'wave'

class LSPhaseIndicator(PhaseIndicatorMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(LSPhaseIndicator, self)._populate()
        LSArenaPhasesComponent.onPhaseChanged += self._update

    def _dispose(self):
        LSArenaPhasesComponent.onPhaseChanged -= self._update
        super(LSPhaseIndicator, self)._dispose()

    def _update(self, arenaPhases):
        if not arenaPhases:
            return
        self.__updateProgressInfo(arenaPhases.activePhase, arenaPhases.phasesCount)

    def __updateProgressInfo(self, activePhase, phasesCount):
        progressInfo = backport.text(_R_INDICATOR.dyn(_WAVE)(), current=activePhase, total=phasesCount)
        self.as_setDataS(progressInfo)
