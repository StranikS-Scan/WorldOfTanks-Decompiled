# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_domain_tooltip_view.py
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from fun_random.gui.feature.util.fun_mixins import FunSubModeHolder
from fun_random.gui.feature.util.fun_wrappers import hasHoldingSubMode

class FunRandomDomainTooltipView(ModifiersDomainTooltipView, FunSubModeHolder):

    @hasHoldingSubMode()
    def getModifiersDataProvider(self):
        return self.getHoldingSubMode().getModifiersDataProvider()

    def _onLoading(self, subModeID=None, *args, **kwargs):
        self.catchSubMode(subModeID or self._funRandomCtrl.subModesHolder.getDesiredSubModeID())
        super(FunRandomDomainTooltipView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        super(FunRandomDomainTooltipView, self)._finalize()
        self.releaseSubMode()
