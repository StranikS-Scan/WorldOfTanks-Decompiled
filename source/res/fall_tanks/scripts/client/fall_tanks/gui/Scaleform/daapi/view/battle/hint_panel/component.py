# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/hint_panel/component.py
from gui.Scaleform.daapi.view.battle.shared.hint_panel.component import BattleHintPanel
from fall_tanks.gui.Scaleform.daapi.view.battle.hint_panel import plugins

class FallTanksBattleHintPanel(BattleHintPanel):

    def _createPlugins(self):
        return plugins.createPlugins()
