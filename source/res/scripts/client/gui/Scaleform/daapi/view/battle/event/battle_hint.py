# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_hint.py
from gui.Scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintComponent

class BattleHint(BattleHintComponent, BattleHintMeta):

    def _showHint(self, data):
        self.as_showHintS(data)

    def _hideHint(self):
        self.as_hideHintS()
