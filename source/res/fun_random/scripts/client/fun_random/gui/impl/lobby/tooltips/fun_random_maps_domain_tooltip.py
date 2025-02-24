# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_maps_domain_tooltip.py
import typing
from battle_modifiers.gui.impl.lobby.tooltips.modifiers_domain_tooltip_view import ModifiersDomainTooltipView
from fun_random.gui.feature.util.fun_wrappers import hasHoldingSubMode
from gui.impl.gen import R
from fun_random.gui.feature.util.fun_mixins import FunSubModeHolder
if typing.TYPE_CHECKING:
    from battle_modifiers.gui.impl.gen.view_models.views.lobby.tooltips.modifiers_domain_tooltip_view_model import ModifiersDomainTooltipViewModel

class FunRandomMapsDomainTooltip(ModifiersDomainTooltipView, FunSubModeHolder):
    __slots__ = ()

    def __init__(self, modifiersDomain):
        layoutID = R.views.fun_random.lobby.tooltips.FunRandomMapsDomainTooltip()
        super(FunRandomMapsDomainTooltip, self).__init__(modifiersDomain, layoutID=layoutID)

    def _onLoading(self, *args, **kwargs):
        self.catchSubMode(self._funRandomCtrl.subModesHolder.getDesiredSubModeID())
        super(FunRandomMapsDomainTooltip, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        super(FunRandomMapsDomainTooltip, self)._finalize()
        self.releaseSubMode()

    @property
    def viewModel(self):
        return super(FunRandomMapsDomainTooltip, self).getViewModel()

    @hasHoldingSubMode()
    def getModifiersDataProvider(self):
        return self.getHoldingSubMode().getModifiersDataProvider()
