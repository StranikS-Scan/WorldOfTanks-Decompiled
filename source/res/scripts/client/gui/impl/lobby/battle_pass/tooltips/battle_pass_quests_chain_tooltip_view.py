# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_quests_chain_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_quests_chain_tooltip_view_model import BattlePassQuestsChainTooltipViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.key_value_model import KeyValueModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_list_model import UserListModel
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class BattlePassQuestsChainTooltipView(ViewImpl):
    __slots__ = ('__token',)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, token):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassQuestsChainTooltipView())
        settings.model = BattlePassQuestsChainTooltipViewModel()
        super(BattlePassQuestsChainTooltipView, self).__init__(settings)
        self.__token = token

    @property
    def viewModel(self):
        return super(BattlePassQuestsChainTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassQuestsChainTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            self.__setRewards(tx.rewards)

    def __setRewards(self, rewardsVM):
        rewardsVM.clearItems()
        rewards = rewardsVM.getItems()
        for bonus in self.__getBonuses():
            reward = KeyValueModel()
            reward.setKey(bonus.getName())
            reward.setValue(bonus.getValue())
            rewards.addViewModel(reward)

        rewardsVM.invalidate()

    def __getBonuses(self):
        return first(self.__eventsCache.getAllQuests(lambda q: q.getID() == self.__token).values()).getBonuses()
