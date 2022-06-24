# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/fun_random/tooltips/fun_random_modifiers_domain_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.fun_random.tooltips.fun_random_modifiers_domain_tooltip_view_model import FunRandomModifiersDomainTooltipViewModel
from gui.impl.lobby.battle_modifiers.helpers import packModifierModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomModifiersDomainTooltipView(ViewImpl):
    __slots__ = ('__modifiersDomain',)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self, modifiersDomain):
        settings = ViewSettings(layoutID=R.views.lobby.fun_random.tooltips.FunRandomModifiersDomainTooltipView(), model=FunRandomModifiersDomainTooltipViewModel())
        super(FunRandomModifiersDomainTooltipView, self).__init__(settings)
        self.__modifiersDomain = modifiersDomain

    @property
    def viewModel(self):
        return super(FunRandomModifiersDomainTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomModifiersDomainTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setModifiersDomain(self.__modifiersDomain)
            self.__invalidateModifiers(model.getModifiers())

    def __invalidateModifiers(self, modifiers):
        modifiers.clear()
        for modifier in self.__funRandomCtrl.getModifiersDataProvider().getDomainModifiers(self.__modifiersDomain):
            modifiers.addViewModel(packModifierModel(modifier))

        modifiers.invalidate()
