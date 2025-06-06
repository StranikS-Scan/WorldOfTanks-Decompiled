# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/periodic_rewards_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.daily.tooltips.periodic_rewards_tooltip_model import PeriodicRewardsTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IPlayStreakController
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.play_streak.play_streak_bonus_packer import getPlayStreakBonusPacker

class PeriodicRewardsTooltip(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __playStreakController = dependency.descriptor(IPlayStreakController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PeriodicRewardsTooltipModel()
        self.__tooltipData = {}
        super(PeriodicRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PeriodicRewardsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PeriodicRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setStreakLength(self.__playStreakController.getStreakProgress())
            model.setDailyWin(self.__itemsCache.items.playStreak.getDailyConditionCompleted())
            rewardsCalendar = self.__playStreakController.getRewardsCalendar()
            calendarArray = model.getRewardsCalendar()
            calendarArray.clear()
            for day, bonuses, tags, additionalInfo in rewardsCalendar:
                calendarItemModel = model.getRewardsCalendarType()()
                calendarItemModel.setDay(day)
                bonusArray = calendarItemModel.getRewards()
                bonusArray.reserve(len(bonuses))
                tagArray = calendarItemModel.getTags()
                tagArray.reserve(len(tags))
                additionalInfoArray = calendarItemModel.getAdditionalInfo()
                additionalInfoArray.reserve(len(tags))
                for tag in tags:
                    tagArray.addString(tag)

                for info in additionalInfo:
                    additionalInfoArray.addString(str(info))

                packBonusModelAndTooltipData(bonuses, bonusArray, self.__tooltipData, getPlayStreakBonusPacker())
                calendarArray.addViewModel(calendarItemModel)

            calendarArray.invalidate()
