# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_battle_results_efficiency_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.battle_results.presenters.wrappers import hasPresenter
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from fun_random.gui.battle_results.base_constants import CommonTooltipType

class PersonalEfficiencyParamTooltip(ViewImpl):

    def __init__(self, arenaUniqueID, paramType):
        settings = ViewSettings(layoutID=R.views.lobby.tooltips.BattleResultsStatsTooltipView(), model=EfficiencyTooltipModel())
        super(PersonalEfficiencyParamTooltip, self).__init__(settings)
        self.__efficiencyParam = paramType
        self.__arenaUniqueID = arenaUniqueID

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def _onLoading(self, *args, **kwargs):
        super(PersonalEfficiencyParamTooltip, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    @hasPresenter()
    def __invalidateAll(self, presenter=None):
        with self.getViewModel().transaction() as model:
            presenter.packTooltips(CommonTooltipType.EFFICIENCY_PARAMETER, model, ctx={'paramType': self.__efficiencyParam})
