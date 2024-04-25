# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/battle_hint.py
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintComponent
from gui.Scaleform.daapi.view.meta.HBBattleHintMeta import HBBattleHintMeta

class BattleHint(BattleHintComponent, HBBattleHintMeta):

    def _showHint(self, voData):
        self.as_showHintS(voData)

    def _hideHint(self):
        self.as_hideHintS()

    def _finishHint(self):
        self.as_closeHintS()
