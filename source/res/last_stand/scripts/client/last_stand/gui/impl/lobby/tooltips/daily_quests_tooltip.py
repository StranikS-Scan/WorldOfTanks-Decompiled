# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/daily_quests_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.daily_tooltip_view_model import DailyTooltipViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewardsForTooltips, getQuestFinishTimeLeft

class DailyQuestsTooltip(ViewImpl):
    __slots__ = ('__quest', '__isBadge', '__progressCurrent', '__progressTotal')
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self, quest, isBadge, progressCurrent=0, progressTotal=0):
        settings = ViewSettings(R.views.last_stand.mono.lobby.tooltips.daily_quests_tooltip())
        settings.model = DailyTooltipViewModel()
        super(DailyQuestsTooltip, self).__init__(settings)
        self.__isBadge = isBadge
        self.__quest = quest
        self.__progressCurrent = progressCurrent
        self.__progressTotal = progressTotal

    @property
    def viewModel(self):
        return super(DailyQuestsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsTooltip, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setIsBadge(self.__isBadge)
            tx.setName(self.__quest.getUserName())
            tx.setDescription(self.__quest.getDescription())
            if self.__progressTotal > 0:
                tx.setProgress(self.__progressCurrent)
                tx.setPercent(int(self.__progressCurrent / self.__progressTotal * 100))
            if self.__isBadge:
                tx.setResetTime(self.__quest.getFinishTime())
            else:
                tx.setResetTime(getQuestFinishTimeLeft(self.__quest))
            rewards = tx.getRewards()
            rewards.clear()
            fillRewardsForTooltips(self.__quest.getBonuses(), rewards, self._MAX_BONUSES_IN_VIEW)
