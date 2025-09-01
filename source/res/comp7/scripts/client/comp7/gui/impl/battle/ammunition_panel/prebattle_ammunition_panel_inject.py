# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/ammunition_panel/prebattle_ammunition_panel_inject.py
from comp7.gui.impl.battle.ammunition_panel.prebattle_ammunition_panel_view import Comp7PrebattleAmmunitionPanelView
from comp7_core.gui.impl.battle.ammunition_panel.prebattle_ammunition_panel_inject import Comp7CorePrebattleAmmunitionPanelInject

class Comp7PrebattleAmmunitionPanelInject(Comp7CorePrebattleAmmunitionPanelInject):

    def _makeInjectView(self, vehicle, *args):
        return Comp7PrebattleAmmunitionPanelView(vehicle, *args)
