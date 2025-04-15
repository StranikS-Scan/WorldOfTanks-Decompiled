# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/reroll_tooltip.py
from constants import DailyQuestsLevels
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.tooltips.reroll_tooltip_model import RerollTooltipModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import getRerollTimeout, getRerollTimeoutPrem
from gui.server_events.events_helpers import isPremiumPlusAccount
from gui.server_events.events_helpers import isPremiumQuestsEnable, isRerollEnabled
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.server_events import IEventsCache

class RerollTooltip(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, rerollPremium):
        self._rerollPremium = rerollPremium
        settings = ViewSettings(R.views.lobby.daily.tooltips.RerollTooltip())
        settings.model = RerollTooltipModel()
        super(RerollTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RerollTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RerollTooltip, self)._onLoading(*args, **kwargs)
        if self._rerollPremium:
            self.__setPremQuestData()
        else:
            self.__setStandartQuestData()

    def __setStandartQuestData(self):
        with self.viewModel.transaction() as model:
            model.setRerollCooldown(int(getRerollTimeout() / time_utils.ONE_MINUTE / time_utils.MINUTES_IN_HOUR))
            model.setTimeToUpdate(int(max(self.eventsCache.dailyQuests.getNextAvailableRerollTimestamp() - time_utils.getCurrentLocalServerTimestamp(), 0)))
            model.setIsPremium(self._rerollPremium)
            model.setIsPremiumActive(isPremiumPlusAccount())
            model.setIsBonusCompleted(first(self.eventsCache.getDailyQuests(filterLevels=(DailyQuestsLevels.BONUS,)).values()).isCompleted())
            _isComplited = all((quest.isCompleted() for quest in self.eventsCache.getDailyQuests(filterLevels=DailyQuestsLevels.DAILY_SIMPLE).itervalues()))
            model.setIsCompleted(_isComplited)
            model.setCanReroll(isRerollEnabled() and not self.eventsCache.dailyQuests.isRerollInCooldown() and not _isComplited)

    def __setPremQuestData(self):
        with self.viewModel.transaction() as model:
            model.setRerollCooldown(int(getRerollTimeoutPrem() / time_utils.ONE_MINUTE / time_utils.MINUTES_IN_HOUR))
            model.setTimeToUpdate(int(max(self.eventsCache.dailyQuests.getNextAvailableRerollTimestampPrem() - time_utils.getCurrentLocalServerTimestamp(), 0)))
            model.setIsPremium(self._rerollPremium)
            model.setIsPremiumActive(isPremiumPlusAccount())
            model.setIsBonusCompleted(first(self.eventsCache.getDailyQuests(filterLevels=(DailyQuestsLevels.BONUS,)).values()).isCompleted())
            _isComplited = all((quest.isCompleted() for quest in self.eventsCache.getDailyPremiumQuests().itervalues()))
            model.setIsCompleted(_isComplited)
            model.setCanReroll(not self.eventsCache.dailyQuests.isRerollInCooldownPrem() and not _isComplited and isPremiumPlusAccount() and isPremiumQuestsEnable())
