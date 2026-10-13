# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/phase_indicator.py
from __future__ import absolute_import
from typing import Optional
from HWArenaPhasesComponent import HWArenaPhasesComponent
from halloween.gui.scaleform.daapi.view.meta.PhaseIndicatorMeta import PhaseIndicatorMeta

class HWPhaseIndicator(PhaseIndicatorMeta):

    def _populate(self):
        super(HWPhaseIndicator, self)._populate()
        HWArenaPhasesComponent.onPhaseChanged += self._update

    def _dispose(self):
        HWArenaPhasesComponent.onPhaseChanged -= self._update
        super(HWPhaseIndicator, self)._dispose()

    def _update(self, arenaPhases):
        if arenaPhases:
            self.as_setDataS(arenaPhases.activePhase, arenaPhases.phasesCount)
