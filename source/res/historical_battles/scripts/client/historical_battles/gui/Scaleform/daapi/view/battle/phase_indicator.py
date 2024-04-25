# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/phase_indicator.py
from typing import Optional
from ArenaPhasesComponent import ArenaPhasesComponent
from gui.Scaleform.daapi.view.meta.HBPhaseIndicatorMeta import HBPhaseIndicatorMeta

class HistoricalBattlesPhaseIndicator(HBPhaseIndicatorMeta):

    def __init__(self):
        super(HistoricalBattlesPhaseIndicator, self).__init__()
        self._isVisible = False

    def _populate(self):
        ArenaPhasesComponent.onPhasesUpdate += self._update
        self._update(None)
        return

    def _dispose(self):
        ArenaPhasesComponent.onPhasesUpdate -= self._update

    def _setVisible(self, value):
        if self._isVisible != value:
            self._isVisible = value
            self.as_setVisibleS(value)

    def _update(self, arenaPhases):
        canShow = arenaPhases is not None and arenaPhases.canShow()
        self._setVisible(canShow)
        if not canShow:
            return
        else:
            self.as_setDataS(arenaPhases.currentPhase, arenaPhases.phasesCount)
            return
