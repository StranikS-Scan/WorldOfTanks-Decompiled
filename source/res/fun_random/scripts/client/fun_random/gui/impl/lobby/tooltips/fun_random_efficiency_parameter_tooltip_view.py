# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_efficiency_parameter_tooltip_view.py
from frameworks.wulf import ViewSettings
from fun_random.gui.shared.tooltips import TooltipType
from gui.battle_results.presenters.wrappers import hasPresenter
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class BattleResultsStatsTooltipView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__efficiencyParam')

    def __init__(self, arenaUniqueID, paramType):
        settings = ViewSettings(layoutID=R.views.lobby.tooltips.BattleResultsStatsTooltipView(), model=EfficiencyTooltipModel())
        super(BattleResultsStatsTooltipView, self).__init__(settings)
        self.__efficiencyParam = paramType
        self.__arenaUniqueID = arenaUniqueID

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(BattleResultsStatsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultsStatsTooltipView, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    @hasPresenter()
    def __invalidateAll(self, presenter=None):
        with self.viewModel.transaction() as model:
            presenter.packTooltips(TooltipType.FUN_EFFICIENCY_PARAMETER, model, ctx={'paramType': self.__efficiencyParam})
