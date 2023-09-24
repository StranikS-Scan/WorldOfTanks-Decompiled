# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/weekly_quests_page.py
import logging
from collections import namedtuple
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT
from comp7_common import COMP7_TOKEN_WEEKLY_REWARD_ID
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progress_points_model import ProgressPointsModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.weekly_quests_model import WeeklyQuestsModel, SeasonState
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.lobby.comp7.comp7_bonus_packer import getComp7BonusPacker, packTokensRewardsQuestBonuses, packQuestBonuses
from gui.impl.lobby.comp7.comp7_quest_helpers import getComp7TokensQuests, getComp7WeeklyQuests
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.periodic_battles.models import PeriodType
from gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)
_BonusData = namedtuple('_BonusData', ('bonus', 'tooltip'))

class WeeklyQuestsPage(PageSubModelPresenter):
    __slots__ = ('__quests', '__bonusData', '__questsTimer')
    __eventsCache = dependency.descriptor(IEventsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, viewModel, parentView):
        super(WeeklyQuestsPage, self).__init__(viewModel, parentView)
        self.__quests = {}
        self.__bonusData = {}
        self.__questsTimer = CallbackDelayer()

    @property
    def pageId(self):
        return MetaRootViews.WEEKLYQUESTS

    @property
    def viewModel(self):
        return super(WeeklyQuestsPage, self).getViewModel()

    def initialize(self):
        super(WeeklyQuestsPage, self).initialize()
        self.__updateData()

    def finalize(self):
        self.__quests.clear()
        self.__bonusData = {}
        self.__questsTimer.clearCallbacks()
        super(WeeklyQuestsPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            bonusData = self.__bonusData[tooltipId]
            window = backport.BackportTooltipWindow(bonusData.tooltip, self.parentView.getParentWindow())
            window.load()
            return window
        else:
            return

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self.__onEventsSyncCompleted), (self.__comp7Controller.onStatusUpdated, self.__onStatusUpdated))

    def __updateData(self):
        self.__quests = getComp7WeeklyQuests()
        with self.viewModel.transaction() as tx:
            self.__updateTimer(tx)
            self.__updateQuests(tx)
            self.__updateProgression(tx)

    def __updateTimer(self, model):
        if self.__quests:
            quest = next(iter(self.__quests.values()))
            model.setResetTimeLeft(quest.getFinishTimeLeft())
            self.__questsTimer.delayCallback(quest.getFinishTimeLeft(), self.__updateData)
        model.setSeasonState(self.__getPeriodState())

    def __getPeriodState(self):
        periodInfo = self.__comp7Controller.getPeriodInfo()
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
            return SeasonState.NOTSTARTED
        if periodInfo.periodType in (PeriodType.AFTER_SEASON,
         PeriodType.AFTER_CYCLE,
         PeriodType.ALL_NOT_AVAILABLE_END,
         PeriodType.NOT_AVAILABLE_END,
         PeriodType.STANDALONE_NOT_AVAILABLE_END):
            return SeasonState.FINISHED
        return SeasonState.LASTWEEK if periodInfo.cycleBorderRight.delta(currentTime) < time_utils.ONE_WEEK else SeasonState.ACTIVE

    def __updateQuests(self, model):
        questCards = []
        sortedQuestsIds = sorted(self.__quests.keys())
        for qID in sortedQuestsIds:
            quest = self.__quests[qID]
            questCardModel = Comp7WeeklyQuestPacker(quest, self.__getPeriodState()).pack()
            packedBonuses, tooltipsData = packQuestBonuses(quest.getBonuses(), getComp7BonusPacker())
            self.__updateRewards(qID, questCardModel, packedBonuses, tooltipsData)
            questCards.append(questCardModel)

        fillViewModelsArray(questCards, model.getQuestCards())

    def __updateProgression(self, model):
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        lastTokensCount = settings.get(COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT, 0)
        currentTokensCount = self.__eventsCache.questsProgress.getTokenCount(COMP7_TOKEN_WEEKLY_REWARD_ID)
        model.setPreviousTokenValue(lastTokensCount)
        model.setCurrentTokenValue(currentTokensCount)
        self.__updateProgressionPoints(model)
        settings[COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT] = currentTokensCount
        AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)

    def __updateProgressionPoints(self, model):
        progressPointsModels = []
        quests = getComp7TokensQuests()
        for qID in sorted(quests.keys()):
            quest = quests[qID]
            progressPointsModel = ProgressPointsModel()
            progressPointsModel.setCount(qID)
            packedBonuses, tooltipsData = packTokensRewardsQuestBonuses(quest)
            self.__updateRewards(qID, progressPointsModel, packedBonuses, tooltipsData)
            progressPointsModels.append(progressPointsModel)

        fillViewModelsArray(progressPointsModels, model.getProgressPoints())

    def __updateRewards(self, qID, model, packedBonuses, tooltipsData):
        rewards = []
        for idx, (packedBonus, tooltipData) in enumerate(zip(packedBonuses, tooltipsData)):
            tooltipId = '%s_%s' % (qID, idx)
            packedBonus.setTooltipId(tooltipId)
            rewards.append(packedBonus)
            self.__bonusData[tooltipId] = _BonusData(packedBonus, tooltipData)

        fillViewModelsArray(rewards, model.getRewards())

    def __onEventsSyncCompleted(self):
        self.__updateData()

    def __onStatusUpdated(self, _):
        self.__updateData()
