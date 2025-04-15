# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/pages/weekly_quests_page.py
from itertools import izip
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT
from comp7.gui.impl.gen.view_models.views.lobby.enums import MetaRootViews
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.progress_points_model import ProgressPointsModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import getComp7BonusPacker, packTokensRewardsQuestBonuses, packQuestBonuses
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isWeeklyRewardClaimable, isWeeklyRewardClaimed
from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
from comp7.gui.shared.event_dispatcher import showComp7WeeklyQuestsRewardsSelectionWindow
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.weekly_quests_model import ChoiceRewardState
if typing.TYPE_CHECKING:
    from typing import Dict, Iterator, List, Optional, Tuple, Union
    from comp7.gui.game_control.comp7_controller import Comp7Controller
    from comp7.gui.game_control.comp7_weekly_quests_controller import Comp7WeeklyQuestsController, _Comp7WeeklyQuests
    from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.quest_card_model import QuestCardModel
    from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.weekly_quests_model import WeeklyQuestsModel
    from frameworks.wulf import ViewEvent
    from gui.impl.backport import TooltipData
    from gui.server_events.event_items import Quest, TokenQuest
_logger = logging.getLogger(__name__)

class WeeklyQuestsPage(PageSubModelPresenter):
    pageId = MetaRootViews.WEEKLYQUESTS
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)
    __slots__ = ('__tooltipDataById',)

    def __init__(self, viewModel, parentView):
        super(WeeklyQuestsPage, self).__init__(viewModel, parentView)
        self.__tooltipDataById = {}

    @property
    def viewModel(self):
        return super(WeeklyQuestsPage, self).getViewModel()

    def initialize(self):
        super(WeeklyQuestsPage, self).initialize()
        self.__updateData(self.__comp7WeeklyQuestsCtrl.getQuests())

    def finalize(self):
        self.__tooltipDataById.clear()
        super(WeeklyQuestsPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipDataById[tooltipId]
            window = BackportTooltipWindow(tooltipData, self.parentView.getParentWindow(), event)
            window.load()
            return window
        else:
            return

    def _getEvents(self):
        return ((self.__comp7WeeklyQuestsCtrl.onWeeklyQuestsUpdated, self.__onWeeklyQuestsUpdated), (self.viewModel.onGoToRewardsSelection, self.__onGoToRewardsSelection), (self.getViewModel().onAnimationEnd, self.__onAnimationEnd))

    def __onWeeklyQuestsUpdated(self, quests):
        self.__updateData(quests)

    @staticmethod
    def __onGoToRewardsSelection():
        showComp7WeeklyQuestsRewardsSelectionWindow()

    def __updateData(self, quests):
        with self.getViewModel().transaction() as model:
            model.setTimeToNewQuests(quests.getTimeToNewQuests())
            self.__setProgressAnimationToBeShown(model, quests.numCompletedBattleQuests)
            fillViewModelsArray(self.__updateQuestCardModels(self.__sliceOffCompletedWeeksExceptLast(quests, model.QUESTS_PER_WEEK)), model.getQuestCards())
            fillViewModelsArray(self.__updateProgressPointModels(quests.sortedTokenQuests, quests.numBattleQuestsToCompleteByTokenQuestIdx), model.getProgressPoints())
            model.setChoiceRewardState(self.__getClaimWeeklyRewardButtonState())

    @staticmethod
    def __getClaimWeeklyRewardButtonState():
        if isWeeklyRewardClaimed():
            return ChoiceRewardState.CLAIMED
        return ChoiceRewardState.ACTIVE if isWeeklyRewardClaimable() else ChoiceRewardState.DEFAULT

    def __updateQuestCardModels(self, sortedBattleQuests):
        bonusPacker = getComp7BonusPacker()
        questPacker = Comp7WeeklyQuestPacker()
        for combinedID, quest in sortedBattleQuests:
            if not quest.isStarted():
                return
            packedBonuses, tooltipsData = packQuestBonuses(quest.getBonuses(), bonusPacker)
            self.__updateRewardsInTooltips(combinedID, packedBonuses, tooltipsData)
            questCardModel = questPacker.pack(quest)
            fillViewModelsArray(packedBonuses, questCardModel.getRewards())
            yield questCardModel

    def __updateProgressPointModels(self, tokenQuests, numBattleQuestsToCompleteByTokenQuestIdx):
        for (ID, quest), cnt in izip(tokenQuests, numBattleQuestsToCompleteByTokenQuestIdx):
            progressPointsModel = ProgressPointsModel()
            progressPointsModel.setCount(cnt)
            packedBonuses, tooltipsData = packTokensRewardsQuestBonuses(quest)
            self.__updateRewardsInTooltips(ID, packedBonuses, tooltipsData)
            fillViewModelsArray(packedBonuses, progressPointsModel.getRewards())
            yield progressPointsModel

    def __updateRewardsInTooltips(self, qID, packedBonuses, tooltipsData):
        for idx, (packedBonus, tooltipData) in enumerate(izip(packedBonuses, tooltipsData)):
            tooltipId = '%s_%s' % (qID, idx)
            self.__tooltipDataById[tooltipId] = tooltipData
            packedBonus.setTooltipId(tooltipId)

    @staticmethod
    def __sliceOffCompletedWeeksExceptLast(weeklyQuests, questsPerWeek):
        quests = weeklyQuests.sortedBattleQuests
        if not quests:
            _logger.error('There are no quests in WeeklyQuestsPage.')
            return []
        for lastQuestInWeekIndex in xrange(questsPerWeek - 1, weeklyQuests.numBattleQuests, questsPerWeek):
            _, lastQuestOfWeek = quests[lastQuestInWeekIndex]
            if not lastQuestOfWeek.isCompleted():
                firstQuestOfWeekIndex = lastQuestInWeekIndex - questsPerWeek + 1
                if lastQuestOfWeek.isStarted():
                    return quests[firstQuestOfWeekIndex:]
                return quests[firstQuestOfWeekIndex - questsPerWeek:]

        return quests[-questsPerWeek:]

    @staticmethod
    def __setProgressAnimationToBeShown(model, numCompletedBattleQuests):
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        previousQuestsPassed = settings.get(COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT, 0)
        if numCompletedBattleQuests < previousQuestsPassed:
            previousQuestsPassed = numCompletedBattleQuests
            settings[COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT] = previousQuestsPassed
            AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)
        model.setPreviousQuestsPassed(previousQuestsPassed)
        model.setQuestsPassed(numCompletedBattleQuests)

    def __onAnimationEnd(self):
        with self.getViewModel().transaction() as model:
            questsPassed = model.getQuestsPassed()
            model.setPreviousQuestsPassed(questsPassed)
            settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
            settings[COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT] = questsPassed
            AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)
