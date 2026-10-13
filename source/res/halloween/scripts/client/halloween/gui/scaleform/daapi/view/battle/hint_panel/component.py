# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/hint_panel/component.py
from __future__ import absolute_import
from halloween.gui.scaleform.daapi.view.battle.hint_panel import plugins
from gui.Scaleform.daapi.view.battle.shared.hint_panel.component import BattleHintPanel

class HWBattleHintPanel(BattleHintPanel):

    def _createPlugins(self):
        commonPlugins = super(HWBattleHintPanel, self)._createPlugins()
        return plugins.updatePlugins(commonPlugins)
