# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_personal_info.py
from __future__ import absolute_import
import typing
from gui.battle_results.presenters.packers.user_info import PersonalInfo
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_battle_results_view_model import FunBattleResultsViewModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunPersonalInfoSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return FunBattleResultsViewModel

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            PersonalInfo.packModel(model, battleResults)
