# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/ammunition_panel/prebattle_ammunition_panel_view.py
from comp7_core.gui.impl.battle.ammunition_panel.prebattle_ammunition_panel_view import Comp7CorePrebattleAmmunitionPanelView
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7PrebattleAmmunitionPanelView(Comp7CorePrebattleAmmunitionPanelView):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller
