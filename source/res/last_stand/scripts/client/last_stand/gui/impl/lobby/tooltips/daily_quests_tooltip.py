# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/daily_quests_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.daily_tooltip_view_model import DailyTooltipViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewardsForTooltips, getQuestFinishTimeLeft
from last_stand.skeletons.ls_controller import ILSController

class DailyQuestsTooltip(ViewImpl):
    lsCtrl = dependency.descriptor(ILSController)
    _MAX_BONUSES_IN_VIEW = 10

    def __init__(self, quest, completedAllDaily):
        settings = ViewSettings(R.views.last_stand.mono.lobby.tooltips.daily_quests_tooltip())
        settings.model = DailyTooltipViewModel()
        super(DailyQuestsTooltip, self).__init__(settings)
        self.__quest = quest
        self.__allDailyCompleted = completedAllDaily

    @property
    def viewModel(self):
        return super(DailyQuestsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsTooltip, self)._onLoading(*args, **kwargs)
        endDate = int(time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.lsCtrl.getModeSettings().endDate)))
        completedQuest = self.__quest.isCompleted()
        with self.viewModel.transaction() as tx:
            tx.setName(self.__quest.getUserName())
            tx.setDescription(self.__quest.getDescription().replace('\\n', '\n'))
            tx.setCompleted(completedQuest)
            tx.setResetTime(getQuestFinishTimeLeft(self.__quest))
            if self.__allDailyCompleted:
                tx.setResetTime(endDate)
            tx.setAllDailyCompleted(self.__allDailyCompleted)
            rewards = tx.getRewards()
            rewards.clear()
            fillRewardsForTooltips(self.__quest.getBonuses(), rewards, self._MAX_BONUSES_IN_VIEW)
