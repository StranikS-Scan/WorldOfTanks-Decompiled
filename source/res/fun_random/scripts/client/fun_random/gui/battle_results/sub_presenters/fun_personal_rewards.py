# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_personal_rewards.py
from __future__ import absolute_import
import typing
from frameworks.wulf import Array
from fun_random.gui.battle_results.packers.fun_packers import FunRandomPersonalRewards
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_reward_item_model import FunRandomRewardItemModel
from fun_random.gui.impl.lobby.tooltips.fun_random_battle_results_economic_tooltip_view import FunRandomBattleResultsEconomicTooltipView
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen import R
from gui.shared import events
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FunPersonalRewardSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Array[FunRandomRewardItemModel]

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            FunRandomPersonalRewards.packModel(model, battleResults)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.fun_random.mono.lobby.tooltips.battle_results_economic_tooltip():
            currencyType = event.getArgument('currencyType')
            return FunRandomBattleResultsEconomicTooltipView(self.parentView.arenaUniqueID, currencyType)
        return super(FunPersonalRewardSubPresenter, self).createToolTipContent(event, contentID)

    def _getListeners(self):
        return super(FunPersonalRewardSubPresenter, self)._getListeners() + ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusStatusChanged),)

    def __onXpBonusStatusChanged(self, _=None):
        with self.getViewModel().transaction() as model:
            FunRandomPersonalRewards.packModel(model, self.getBattleResults())
