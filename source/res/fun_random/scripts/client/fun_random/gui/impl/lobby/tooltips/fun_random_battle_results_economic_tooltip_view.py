# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_battle_results_economic_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from fun_random.gui.battle_results.tooltips.earned_currency_tooltips import FunEarnedCurrencyTooltipsPacker
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_economic_tooltip_view_model import FunRandomEconomicTooltipViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class FunRandomBattleResultsEconomicTooltipView(ViewImpl):
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueID, currencyType):
        settings = ViewSettings(layoutID=R.views.fun_random.mono.lobby.tooltips.battle_results_economic_tooltip(), model=FunRandomEconomicTooltipViewModel())
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

    def __invalidateAll(self):
        statsCtrl = self.__battleResults.getStatsCtrl(self.arenaUniqueID)
        with self.viewModel.transaction() as model:
            FunEarnedCurrencyTooltipsPacker.packTooltip(model, statsCtrl.getResults(), ctx={'currencyType': self.__currencyType})
