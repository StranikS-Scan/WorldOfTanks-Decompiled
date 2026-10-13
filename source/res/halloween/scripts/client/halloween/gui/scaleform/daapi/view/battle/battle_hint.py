# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/battle_hint.py
from __future__ import absolute_import, division
from builtins import round
import BattleReplay
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID, HALLOWEEN_BATTLE_HINTS_QUEUE_ID
from halloween.gui.scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from halloween.gui.scaleform.daapi.view.meta.BattleHintProgressMeta import BattleHintProgressMeta
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class BattleHint(BattleHintComponent, BattleHintMeta):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleHint, self).__init__(battleHintsQueueParams=HALLOWEEN_BATTLE_HINTS_QUEUE_ID)

    @property
    def hwBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _populate(self):
        super(BattleHint, self)._populate()
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onBattleGoalChanged += self._onBattleGoalChanged

    def _dispose(self):
        super(BattleHint, self)._dispose()
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onBattleGoalChanged -= self._onBattleGoalChanged
        if BattleReplay.g_replayCtrl.isPlaying:
            self._hideHint()

    def _showHint(self, model, params):
        vo = model.createVO(params)
        if vo:
            self.as_showHintS(vo)

    def _hideHint(self):
        self.as_hideHintS()

    def _cancelFadeOut(self):
        self.as_cancelFadeOutS()

    def _onBattleGoalChanged(self, goalName):
        self.as_clearPinnableHintS()


class ProgressBarBattleHint(BattleHint, BattleHintProgressMeta):

    def _populate(self):
        super(ProgressBarBattleHint, self)._populate()
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress += self._onCollectorSoulsChanged
        self._updateProgressBar()

    def _dispose(self):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress -= self._onCollectorSoulsChanged
        super(ProgressBarBattleHint, self)._dispose()

    def _hideHint(self):
        super(ProgressBarBattleHint, self)._hideHint()
        self._updateProgressBar()

    def _normalizeSoulsLeft(self, soulsLeft, maxSoulsCount):
        return round((maxSoulsCount - soulsLeft) * 100.0 / maxSoulsCount) if maxSoulsCount > 0 else 0

    def _getCollectorSoulsAndCapacity(self):
        if self.hwBattleGuiCtrl:
            souls, capacity = self.hwBattleGuiCtrl.getCurrentCollectorSoulsInfo()
            if souls is not None and capacity is not None:
                return (souls, capacity)
        return (0, 0)

    def _updateProgressBar(self):
        souls, capacity = self._getCollectorSoulsAndCapacity()
        soulsLeft = max(0, capacity - souls)
        normalizedSoulsLeft = self._normalizeSoulsLeft(soulsLeft, capacity)
        self.as_updateProgressS(soulsLeft, normalizedSoulsLeft)

    def _onCollectorSoulsChanged(self, *args):
        self._updateProgressBar()
