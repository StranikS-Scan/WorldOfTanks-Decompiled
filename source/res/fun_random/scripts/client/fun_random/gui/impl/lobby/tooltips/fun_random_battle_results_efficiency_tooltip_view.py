# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_battle_results_efficiency_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class PersonalEfficiencyParamTooltip(ViewImpl):
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueID, paramType, packer):
        settings = ViewSettings(layoutID=R.views.lobby.tooltips.BattleResultsStatsTooltipView(), model=EfficiencyTooltipModel())
        super(PersonalEfficiencyParamTooltip, self).__init__(settings)
        self.__efficiencyParam = paramType
        self.__arenaUniqueID = arenaUniqueID
        self.__packer = packer

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    def _onLoading(self, *args, **kwargs):
        super(PersonalEfficiencyParamTooltip, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    def _finalize(self):
        self.__packer = None
        super(PersonalEfficiencyParamTooltip, self)._finalize()
        return

    def __invalidateAll(self):
        statsCtrl = self.__battleResults.getStatsCtrl(self.arenaUniqueID)
        with self.getViewModel().transaction() as model:
            self.__packer.packTooltip(model, statsCtrl.getResults(), ctx={'paramType': self.__efficiencyParam})
