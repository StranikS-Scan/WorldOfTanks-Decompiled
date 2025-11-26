# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_battle_results_efficiency_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from fun_random.gui.battle_results.tooltips.total_efficiency_tooltips import FunEfficiencyTooltipsPacker
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class PersonalEfficiencyParamTooltip(ViewImpl):
    __battleResults = dependency.descriptor(IBattleResultsService)

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

    def __invalidateAll(self):
        statsCtrl = self.__battleResults.getStatsCtrl(self.arenaUniqueID)
        with self.getViewModel().transaction() as model:
            FunEfficiencyTooltipsPacker.packTooltip(model, statsCtrl.getResults(), ctx={'paramType': self.__efficiencyParam})
