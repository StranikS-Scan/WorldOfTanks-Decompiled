# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_domain_tooltip_view.py
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomDomainTooltipView(ModifiersDomainTooltipView):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def getModifiersDataProvider(self):
        return self.__funRandomCtrl.getModifiersDataProvider()
