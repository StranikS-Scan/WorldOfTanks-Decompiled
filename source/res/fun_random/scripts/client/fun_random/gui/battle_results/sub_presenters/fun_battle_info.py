# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_battle_info.py
from __future__ import absolute_import
import typing
from fun_random.gui.battle_results.packers.fun_packers import FunRandomBattleInfo
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_battle_info_model import FunRandomBattleInfoModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunBattleInfoSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return FunRandomBattleInfoModel

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FunRandomBattleInfo.packModel(model, battleResults)
