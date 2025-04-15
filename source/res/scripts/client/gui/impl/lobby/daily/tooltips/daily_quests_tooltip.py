# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/tooltips/daily_quests_tooltip.py
from constants import PREMIUM_TYPE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_constants import DailyQuestsConstants
from gui.impl.gen.view_models.views.lobby.daily.tooltips.daily_quest_tooltip_model import DailyQuestTooltipModel
from gui.impl.lobby.daily.daily_quest_view_constants import WIDGET_GROUP_TO_LEVELS
from gui.impl.lobby.daily.daily_quests_model_helpers import addSubscriptionBonusesToQuest
from gui.impl.lobby.daily.daily_helpers import modifyPostbattleConditions
from gui.impl.pub import ViewImpl
from gui.server_events.events_helpers import dailyQuestsSortFunc
from gui.shared.missions.packers.events import getEventUIDataPacker
from helpers import dependency
from helpers.time_utils import getDayTimeLeft, getGameWeekTimeLeft
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class DailyQuestsTooltip(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __subsController = dependency.descriptor(IWotPlusController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__quests', '__groupId')

    def __init__(self, groupId):
        settings = ViewSettings(R.views.lobby.daily.tooltips.DailyQuestTooltip())
        settings.flags = ViewFlags.VIEW
        settings.model = DailyQuestTooltipModel()
        super(DailyQuestsTooltip, self).__init__(settings)
        self.__groupId = groupId
        self.__quests = sorted(self.__eventsCache.getDailyQuests(filterLevels=WIDGET_GROUP_TO_LEVELS.get(groupId, {})).values(), key=dailyQuestsSortFunc)

    @property
    def viewModel(self):
        return super(DailyQuestsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as viewModel:
            questsArray = viewModel.getQuests()
            subsQuestsByLevels = {q.getLevel():q for q in self.__eventsCache.getDailyQuestsSub().itervalues()}
            for quest in self.__quests:
                packer = getEventUIDataPacker(quest)
                model = packer.pack()
                addSubscriptionBonusesToQuest(model, subsQuestsByLevels)
                modifyPostbattleConditions(quest, model)
                questsArray.addViewModel(model)

            questsArray.invalidate()
            viewModel.setTimeToUpdate(self.__getTimeToUpdate())
            viewModel.setIsPremiumActive(self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS))
            viewModel.setIsSubscriptionActive(self.__subsController.isEnabled())
            viewModel.setGroupId(self.__groupId)

    def __getTimeToUpdate(self):
        return getGameWeekTimeLeft() if self.__groupId == DailyQuestsConstants.EPIC_GROUP_ID else getDayTimeLeft()
