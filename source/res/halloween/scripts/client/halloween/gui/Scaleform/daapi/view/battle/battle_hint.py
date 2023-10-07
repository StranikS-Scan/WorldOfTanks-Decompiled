# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/battle_hint.py
from gui.Scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from halloween.gui.battle_control.controllers.battle_hints_ctrl import BattleHintComponent

class BattleHint(BattleHintComponent, BattleHintMeta):

    def _showHint(self, data):
        self.as_showHintS(data)

    def _hideHint(self):
        if self.currentHint:
            self.as_hideHintS()
