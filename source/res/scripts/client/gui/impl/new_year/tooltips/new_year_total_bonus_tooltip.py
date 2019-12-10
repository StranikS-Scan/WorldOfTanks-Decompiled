# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_total_bonus_tooltip.py
from frameworks.wulf import ViewFlags, View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_total_bonus_tooltip_model import NewYearTotalBonusTooltipModel
from new_year.ny_bonuses import CreditsBonusHelper
from gui.impl.new_year.new_year_helper import fillBonusFormula
from skeletons.new_year import INewYearController
from helpers import dependency

class NewYearTotalBonusTooltip(View):
    __slots__ = ()
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(NewYearTotalBonusTooltip, self).__init__(ViewSettings(R.views.lobby.new_year.tooltips.new_year_total_bonus_tooltip.NewYearTotalBonusTooltip(), flags=ViewFlags.COMPONENT, model=NewYearTotalBonusTooltipModel()))

    @property
    def viewModel(self):
        return super(NewYearTotalBonusTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        fillBonusFormula(self.viewModel.bonusFormula)
        with self.viewModel.transaction() as tx:
            tx.setMaxBonus(CreditsBonusHelper.getMaxBonus())
            tx.setCreditsBonus(self._nyController.getActiveSettingBonusValue())
            tx.setIsPostNYEnabled(self._nyController.isPostEvent())
