# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/quests_view.py
import typing
import logging
from frameworks.wulf import ViewFlags, Array
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gui_decorators import args2params
from gui.server_events.events_helpers import EventInfoModel
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from white_tiger.gui.wt_quest_data_packer import WTQuestUIDataPacker
from white_tiger.gui.white_tiger_account_settings import AccountSettingsKeys
from white_tiger.gui.white_tiger_gui_constants import WT_QUEST_BOSS_GROUP_ID, MAX_VISIBLE_QUESTS, HUNTER_QUEST_CHAINS
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.quests_view_model import QuestsViewModel, QuestsTabType
from white_tiger.gui.white_tiger_account_settings import setSettings, getSettings
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.quest_view_model import QuestViewModel
_TOOLTIP_PREFIX = 'quests_'

class QuestsView(ViewComponent[QuestsViewModel]):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID=R.aliases.white_tiger.shared.ProgressionQuests(), **kwargs):
        super(QuestsView, self).__init__(layoutID=layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=QuestsViewModel)
        self.__tooltipData = {}
        self.__activeTab = QuestsTabType.HARRIER
        self.questContainer = QuestsContainer()

    @property
    def viewModel(self):
        return super(QuestsView, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(QuestsView, self).initialize(args, kwargs)
        tabIndex = getSettings(AccountSettingsKeys.WT_PROGRESSION_QUESTS_TAB)
        if tabIndex is not None:
            self.__activeTab = list(QuestsTabType)[tabIndex]
        return

    def _onLoading(self, *args, **kwargs):
        super(QuestsView, self)._onLoading(args, kwargs)
        self.__populateModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onSelectedTab, self.__onSelectedTab), (self.eventsCache.onSyncCompleted, self._onSyncCompleted))

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
            availableQuests = self.questContainer.getQuests(WT_QUEST_BOSS_GROUP_ID)
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
        setSettings(AccountSettingsKeys.WT_PROGRESSION_QUESTS_TAB, tabIndex)
        with self.viewModel.transaction() as model:
            model.setActiveTab(self.__activeTab)

    def _onSyncCompleted(self):
        self.__populateModel()


class QuestsContainer(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def getQuests(self, groupID, allowCompleted=False, reverse=False):

        def filterQuests(quest):
            return quest.accountReqs.isAvailable() or allowCompleted and quest.isCompleted()

        quests = [ (qID, q) for qID, q in self.eventsCache.getAllQuests(filterQuests).iteritems() if q.getGroupID() == groupID ]
        return sorted(quests, key=lambda item: item[1].getPriority(), reverse=reverse)

    def getQuestCompletionChanged(self, questID):
        return self.eventsCache.questsProgress.getQuestCompletionChanged(questID)

    def markQuestProgressAsViewed(self, seenQuestID):
        self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuestID)
