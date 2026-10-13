# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/damage_log_panel.py
from __future__ import absolute_import
from gui.battle_control.avatar_getter import getPlayerVehicleID
from gui.impl import backport
from fort_rush.gui.scaleform.daapi.view.meta.FortRushDamageLogPanelMeta import FortRushDamageLogPanelMeta
from fort_rush_common.component_helpers import getScoreComponent

class FortRushDamagePanel(FortRushDamageLogPanelMeta):

    def __init__(self):
        super(FortRushDamagePanel, self).__init__()
        self._scoreComponent = getScoreComponent()
        self._totalScore = 0

    def _populate(self):
        super(FortRushDamagePanel, self)._populate()
        if self._scoreComponent is not None:
            self._scoreComponent.onPersonalScoreUpdated += self._handleFortRushPersonalScoreUpdateEvent
        return

    def _dispose(self):
        if self._scoreComponent is not None:
            self._scoreComponent.onPersonalScoreUpdated -= self._handleFortRushPersonalScoreUpdateEvent
        super(FortRushDamagePanel, self)._dispose()
        return

    def _handleFortRushPersonalScoreUpdateEvent(self, scores):
        score = scores.get(getPlayerVehicleID(), 0)
        if score == self._totalScore:
            return
        self._totalScore = score
        self.as_updateSummaryFortRushValueS(backport.getIntegralFormat(score))
