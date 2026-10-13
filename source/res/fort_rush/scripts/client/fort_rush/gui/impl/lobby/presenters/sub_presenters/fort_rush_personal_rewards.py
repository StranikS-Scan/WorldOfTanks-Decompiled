# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/sub_presenters/fort_rush_personal_rewards.py
from __future__ import absolute_import
import typing
from frameworks.wulf import Array
from fort_rush.gui.fort_rush_presenters_packers import FortRushPersonalRewards
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.fort_rush_reward_item_model import FortRushRewardItemModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults

class FortRushPersonalRewardSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Array[FortRushRewardItemModel]

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FortRushPersonalRewards.packModel(model, battleResults)
