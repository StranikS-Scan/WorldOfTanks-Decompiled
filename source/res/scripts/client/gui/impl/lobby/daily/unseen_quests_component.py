# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/unseen_quests_component.py
from constants import DailyQuestsLevels
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_mark_seen_model import DailyQuestMarkSeenModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.daily.daily_quest_view_constants import QUESTS_LEVELS_IN_TAB
from helpers import dependency
from skeletons.gui.game_control import IUnseenEventsCounter
from skeletons.gui.server_events import IEventsCache

def getAvailableDailyQuests(eventsCache):
    return eventsCache.getDailyQuests(filterLevels=DailyQuestsLevels.DAILY_QUESTS_WITHOUT_EPIC).keys()


class UnseenQuestsComponent(SubModelPresenter):
    __slots__ = ('__currentTabID',)
    __eventsCache = dependency.descriptor(IEventsCache)
    __unseenEventsManager = dependency.descriptor(IUnseenEventsCounter)

    def __init__(self, viewModel, parentView):
        super(UnseenQuestsComponent, self).__init__(viewModel, parentView)
        self.__currentTabID = None
        return

    def initialize(self, *args, **kwargs):
        super(UnseenQuestsComponent, self).initialize(*args, **kwargs)
        self.__updateUnseen()
        self.__currentTabID = self.parentView.getViewModel().getCurrentTabIdx()
        self.__unseenEventsManager.onUnseenEventUpdated += self.__updateUnseen
        self.__unseenEventsManager.onSeenEvents += self.__updateUnseen

    def finalize(self):
        super(UnseenQuestsComponent, self).finalize()
        self.__unseenEventsManager.onUnseenEventUpdated -= self.__updateUnseen
        self.__unseenEventsManager.onSeenEvents -= self.__updateUnseen
        self.__seenAllQuestsInTab(self.__currentTabID)

    def setIsCurrentMissionTab(self, isCurrent):
        if not isCurrent:
            self.__seenAllQuestsInTab(self.__currentTabID)

    def setCurrentTab(self, tabIdx):
        if self.__currentTabID != tabIdx:
            self.__seenAllQuestsInTab(self.__currentTabID)
            self.__currentTabID = tabIdx

    def _getEvents(self):
        return ((self.getViewModel().onQuestsSeen, self.__onQuestsSeen),)

    def __updateUnseen(self, *_):
        availableDailyQuests = getAvailableDailyQuests(self.__eventsCache)
        quests = self.getViewModel().getUnseenQuests()
        quests.clear()
        for qID in availableDailyQuests:
            if self.__unseenEventsManager.isUnseenEvent(qID):
                questModel = DailyQuestMarkSeenModel()
                questModel.setQuestID(qID)
                quests.addViewModel(questModel)

        quests.invalidate()

    @args2params(str)
    def __onQuestsSeen(self, questID):
        self.__unseenEventsManager.seenEvent(questID, 1)

    def __seenAllQuestsInTab(self, tabID):
        quests = self.getViewModel().getUnseenQuests()
        seenEvents = {}
        for q in quests:
            if tabID in QUESTS_LEVELS_IN_TAB.get(self.__eventsCache.getQuestByID(q.getQuestID()).getLevel(), []):
                seenEvents[q.getQuestID()] = 1

        self.__unseenEventsManager.seenEvents(seenEvents)
