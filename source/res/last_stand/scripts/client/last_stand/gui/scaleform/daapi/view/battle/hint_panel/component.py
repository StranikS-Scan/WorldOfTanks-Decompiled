# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/hint_panel/component.py
from last_stand.gui.scaleform.daapi.view.battle.hint_panel import plugins
from gui.Scaleform.daapi.view.battle.shared.hint_panel.component import BattleHintPanel

class LSBattleHintPanel(BattleHintPanel):

    def _createPlugins(self):
        commonPlugins = super(LSBattleHintPanel, self)._createPlugins()
        return plugins.updatePlugins(commonPlugins)
