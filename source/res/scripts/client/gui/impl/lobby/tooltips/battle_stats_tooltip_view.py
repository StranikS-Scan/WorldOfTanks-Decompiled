# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/battle_stats_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.battle_results.presenters.wrappers import hasPresenter
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class BattleResultsStatsTooltipView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__efficiencyParam', '__tooltipType')

    def __init__(self, arenaUniqueID, paramType, tooltipType):
        settings = ViewSettings(layoutID=R.views.lobby.tooltips.BattleResultsStatsTooltipView(), model=EfficiencyTooltipModel())
        super(BattleResultsStatsTooltipView, self).__init__(settings)
        self.__efficiencyParam = paramType
        self.__arenaUniqueID = arenaUniqueID
        self.__tooltipType = tooltipType

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
            presenter.packTooltips(self.__tooltipType, model, ctx={'paramType': self.__efficiencyParam})
