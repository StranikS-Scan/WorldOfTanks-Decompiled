# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/battle_hint.py
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintComponent
from white_tiger.gui.Scaleform.daapi.view.meta.WTBattleHintMeta import WTBattleHintMeta

class BattleHint(BattleHintComponent, WTBattleHintMeta):

    def _showHint(self, data):
        self.as_showHintS(data)

    def _hideHint(self):
        if self.currentHint:
            self.as_hideHintS()
