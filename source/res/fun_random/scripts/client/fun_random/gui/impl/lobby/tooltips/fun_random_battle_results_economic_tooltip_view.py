# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_battle_results_economic_tooltip_view.py
from frameworks.wulf import ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_economic_tooltip_view_model import FunRandomEconomicTooltipViewModel
from fun_random.gui.shared.tooltips import TooltipType
from gui.battle_results.presenters.wrappers import hasPresenter
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class FunRandomBattleResultsEconomicTooltipView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__currencyType')

    def __init__(self, arenaUniqueID, currencyType):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.tooltips.FunRandomBattleResultsEconomicTooltipView(), model=FunRandomEconomicTooltipViewModel())
        super(FunRandomBattleResultsEconomicTooltipView, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__currencyType = currencyType

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(FunRandomBattleResultsEconomicTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomBattleResultsEconomicTooltipView, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    @hasPresenter()
    def __invalidateAll(self, presenter=None):
        with self.viewModel.transaction() as model:
            presenter.packTooltips(TooltipType.FUN_EARNED_CURRENCY, model, ctx={'currencyType': self.__currencyType})
