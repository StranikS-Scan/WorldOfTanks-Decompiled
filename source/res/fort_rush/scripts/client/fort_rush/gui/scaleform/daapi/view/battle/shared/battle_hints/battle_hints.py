# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/shared/battle_hints/battle_hints.py
from __future__ import absolute_import
from fort_rush.gui.scaleform.daapi.view.meta.ExampleBattleHintMeta import ExampleBattleHintMeta
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.Scaleform.daapi.view.battle.shared.battle_hint import BattleHint
from gui.battle_control.controllers.battle_hints.queues import BattleHintQueueParams
BATTLE_HINTS_QUEUE_ID = BattleHintQueueParams(name='fort_rush', withFadeOut=True)

class FortRushBattleHint(BattleHint):

    def __init__(self):
        super(FortRushBattleHint, self).__init__(battleHintsQueueParams=BATTLE_HINTS_QUEUE_ID)


class FortRushOffsetBattleHint(BattleHintComponent, ExampleBattleHintMeta):

    def __init__(self):
        super(FortRushOffsetBattleHint, self).__init__(battleHintsQueueParams=BATTLE_HINTS_QUEUE_ID)

    def _showHint(self, model, params):
        vo = model.createVO(params)
        if vo:
            self.as_showHintS(vo)

    def _hideHint(self):
        self.as_hideHintS()

    def _cancelFadeOut(self):
        self.as_cancelFadeOutS()
