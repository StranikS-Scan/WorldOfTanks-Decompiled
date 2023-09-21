# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_quests_view.py
import typing
import logging
from account_helpers.AccountSettings import AccountSettings, WT_PROGRESSION_QUESTS_TAB
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.wt_event.wt_quests_model import WtQuestsModel, QuestsTabType
from gui.impl.gui_decorators import args2params
from gui.server_events.events_helpers import EventInfoModel
from gui.server_events.events_constants import WT_BOSS_GROUP_ID
from gui.wt_event.wt_event_quest_data_packer import WTQuestUIDataPacker
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.wt_event.wt_quest_model import WtQuestModel
MAX_VISIBLE_QUESTS = 3
HUNTER_QUEST_CHAINS = ['wt_group_hunter_1', 'wt_group_hunter_2', 'wt_group_hunter_3']
_TOOLTIP_PREFIX = 'quests_'

class WTQuestsView(SubModelPresenter):
    __slots__ = ('questContainer', '__tooltipData', '__activeTab')

    def __init__(self, viewModel, parentView):
        super(WTQuestsView, self).__init__(viewModel, parentView)
        self.__tooltipData = {}
        self.__activeTab = QuestsTabType.HARRIER
        self.questContainer = WTQuestsContainer()

    @property
    def viewModel(self):
        return super(WTQuestsView, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(WTQuestsView, self).initialize(args, kwargs)
        tabIndex = AccountSettings.getSettings(WT_PROGRESSION_QUESTS_TAB)
        if tabIndex is not None:
            self.__activeTab = list(QuestsTabType)[tabIndex]
        self.__addListeners()
        self.__populateModel()
        return

    def finalize(self):
        self.__removeListeners()
        self.__tooltipData = None
        super(WTQuestsView, self).finalize()
        return

    def getTooltipItems(self):
        return self.__tooltipData

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __populateModel(self):
        self.__tooltipData = {}
        with self.viewModel.transaction() as model:
            model.setActiveTab(self.__activeTab)
            countdownValue = EventInfoModel.getDailyProgressResetTimeDelta()
            model.setUpdateCountdown(countdownValue)
            self.__fillQuests(model.getHarrierQuests(), model.getHarrierQuestsVisited(), QuestsTabType.HARRIER)
            self.__fillQuests(model.getEngineerQuests(), model.getEngineerQuestsVisited(), QuestsTabType.ENGINEER)

    def __fillQuests(self, quests, visitedArray, tab):
        if tab == QuestsTabType.ENGINEER:
            availableQuests = self.questContainer.getQuests(WT_BOSS_GROUP_ID)
        else:
            availableQuests = []
            for chainID in HUNTER_QUEST_CHAINS:
                harrierQuests = self.questContainer.getQuests(chainID, reverse=True)
                if not harrierQuests:
                    harrierQuests = self.questContainer.getQuests(chainID, allowCompleted=True, reverse=True)
                if not harrierQuests:
                    _logger.error("Can't find quests for group %s", chainID)
                    continue
                availableQuests.append(harrierQuests[0])

        availableQuests = availableQuests[:MAX_VISIBLE_QUESTS]
        availableKeys = []
        quests.clear()
        quests.reserve(len(availableQuests))
        bonusIndexTotal = len(self.__tooltipData)
        for questID, quest in availableQuests:
            packer = WTQuestUIDataPacker(quest)
            questModel = packer.pack()
            bonusTooltipList = packer.getTooltipData()
            for bonusIndex, item in enumerate(questModel.getBonuses()):
                tooltipIdx = _TOOLTIP_PREFIX + str(bonusIndexTotal)
                item.setTooltipId(tooltipIdx)
                if bonusTooltipList:
                    self.__tooltipData[tooltipIdx] = bonusTooltipList[str(bonusIndex)]
                bonusIndexTotal += 1

            quests.addViewModel(questModel)
            availableKeys.append(questID)

        quests.invalidate()
        self.__updateQuestsVisitedArray(visitedArray, availableKeys, tab)

    def __updateQuestsVisitedArray(self, questsVisitedArray, questsIDs, tab):
        questsVisitedArray.clear()
        questsVisitedArray.reserve(len(questsIDs))
        for questID in questsIDs:
            missionCompletedVisited = not self.questContainer.getQuestCompletionChanged(questID)
            self.questContainer.markQuestProgressAsViewed(questID)
            questsVisitedArray.addBool(missionCompletedVisited)

        questsVisitedArray.invalidate()

    @args2params(str)
    def __onSelectedTab(self, tab):
        selectedTab = QuestsTabType(tab)
        if self.__activeTab == selectedTab:
            return
        self.__activeTab = selectedTab
        tabIndex = list(QuestsTabType).index(self.__activeTab)
        AccountSettings.setSettings(WT_PROGRESSION_QUESTS_TAB, tabIndex)
        with self.viewModel.transaction() as model:
            model.setActiveTab(self.__activeTab)

    def __addListeners(self):
        self.viewModel.onSelectedTab += self.__onSelectedTab

    def __removeListeners(self):
        self.viewModel.onSelectedTab -= self.__onSelectedTab


class WTQuestsContainer(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def getQuests(self, groupID, allowCompleted=False, reverse=False):

        def filterQuests(quest):
            return quest.getGroupID() == groupID and (quest.accountReqs.isAvailable() or allowCompleted and quest.isCompleted())

        quests = self.eventsCache.getAllQuests(filterQuests).items()
        return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)

    def getQuestCompletionChanged(self, questID):
        return self.eventsCache.questsProgress.getQuestCompletionChanged(questID)

    def markQuestProgressAsViewed(self, seenQuestID):
        self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
