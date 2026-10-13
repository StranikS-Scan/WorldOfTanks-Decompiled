# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/daily_quests_tooltip.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.daily_tooltip_view_model import DailyTooltipViewModel
from halloween.gui.impl.lobby.hw_helpers import fillRewardsForTooltips
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.server_events.awards_formatters import PreformattedBonus
    from halloween.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestData

class DailyQuestsTooltip(ViewImpl):
    __slots__ = ('__questData',)
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self, questData):
        settings = ViewSettings(R.views.halloween.mono.lobby.tooltips.daily_quests_tooltip())
        settings.model = DailyTooltipViewModel()
        super(DailyQuestsTooltip, self).__init__(settings)
        self.__questData = questData

    @property
    def viewModel(self):
        return super(DailyQuestsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsTooltip, self)._onLoading()
        with self.viewModel.transaction() as tx:
            quest, bonus = self.__questData
            tx.setIsEpicMedal(self._isBonusEpicMedal(bonus))
            tx.setName(quest.getUserName())
            tx.setDescription(quest.getDescription())
            tx.setResetTime(quest.getFinishTime())
            rewards = tx.getRewards()
            rewards.clear()
            fillRewardsForTooltips(quest.getBonuses(), rewards, self._MAX_BONUSES_IN_VIEW)

    def _isBonusEpicMedal(self, bonus):
        return bonus.bonusName == 'dossier_achievement' if bonus else False
