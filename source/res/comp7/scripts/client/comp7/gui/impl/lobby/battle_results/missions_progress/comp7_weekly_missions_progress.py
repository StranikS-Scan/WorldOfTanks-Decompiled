# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/missions_progress/comp7_weekly_missions_progress.py
from __future__ import absolute_import
import typing
from shared_utils import first
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_weekly_quest_progress_model import Comp7WeeklyQuestProgressModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_weekly_quests_progress_model import Comp7WeeklyQuestsProgressModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import getWeeklyPBSBonusPacker, packQuestBonuses
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isComp7Quest, getComp7QuestType, getComp7WeeklyQuestsCompleteToken
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestPacker, Comp7TokenQuestPacker
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from comp7_common_const import Comp7QuestType
from frameworks.wulf.view.array import fillViewModelsArray
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.battle_results.progress.progress_helpers import getReceivedTokensInfo
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.pub.view_component import ViewComponent
from gui.server_events import conditions
from helpers import dependency
if typing.TYPE_CHECKING:
    from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel

class Comp7WeeklyMissionsProgressPresenter(ViewComponent[Comp7WeeklyQuestsProgressModel], IProgressionCategoryPresenter):
    __comp7WeeklyQuestsCtrl = dependency.descriptor(IComp7WeeklyQuestsController)

    def __init__(self, categoryProgressFilter, arenaUniqueID, **_):
        super(Comp7WeeklyMissionsProgressPresenter, self).__init__(model=Comp7WeeklyQuestsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__progress = None
        self.__tooltipData = {}
        return

    @classmethod
    def getPathToResource(cls):
        return Comp7WeeklyQuestsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.comp7.shared.BattleResultsWeeklyQuests()

    @property
    def viewModel(self):
        return super(Comp7WeeklyMissionsProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is not None:
                questId, bonusIdx = tooltipId.rsplit(':', 1)
                tooltipData = self.__tooltipData.get(questId, {}).get(bonusIdx)
                if tooltipData is not None:
                    window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                    window.load()
                    return window
        return

    def _finalize(self):
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__tooltipData = None
        super(Comp7WeeklyMissionsProgressPresenter, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(Comp7WeeklyMissionsProgressPresenter, self)._onLoading(*args, **kwargs)
        battleResults = getBattleResults(self.__arenaUniqueID)
        if not battleResults:
            return
        self.__progress = self.__categoryProgressFilter(battleResults.reusable)
        if not self.__progress:
            return
        self.__updateModel()
        parentModel = self.getParentView().viewModel
        plugins = parentModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def __updateModel(self):
        _, questTokensCount = getReceivedTokensInfo(self.__arenaUniqueID)
        with self.viewModel.transaction() as vm:
            questsModel = vm.getWeeklyQuests()
            questsModel.clear()
            comp7Quests = [ q for q in self.__progress if isComp7Quest(q[0].getID()) ]
            weeklyQuests = [ q for q in comp7Quests if getComp7QuestType(q[0].getID()) == Comp7QuestType.WEEKLY ]
            for quest, pCur, pPrev, isReset, isCompleted in weeklyQuests:
                questsModel.addViewModel(self.__packQuestModel(quest, pCur, pPrev, isReset, isCompleted, questTokensCount))

            tokenQuests = [ q for q in comp7Quests if getComp7QuestType(q[0].getID()) == Comp7QuestType.TOKENS ]
            for quest, pCur, pPrev, isReset, isCompleted in tokenQuests:
                questsModel.addViewModel(self.__packQuestModel(quest, pCur, pPrev, isReset, isCompleted, questTokensCount))

            if weeklyQuests and not tokenQuests:
                tokenQuestModel = self.__packUncompletedTokenQuestModel(questTokensCount)
                if tokenQuestModel is not None:
                    questsModel.addViewModel(tokenQuestModel)
            questsModel.invalidate()
        return

    def __packQuestModel(self, quest, pCur, pPrev, reset, complete, questTokensCount):
        questID = quest.getID()
        self.__tooltipData[questID] = {}
        model = Comp7WeeklyQuestProgressModel()
        model.setId(questID)
        if getComp7QuestType(questID) == Comp7QuestType.WEEKLY:
            packer = Comp7WeeklyQuestPacker()
            iconKey, _, totalProgress, description = packer.getData(quest)
            currentProgress, earned = self.__getEarnedPoints(quest, pCur, pPrev)
        else:
            packer = Comp7TokenQuestPacker()
            iconKey, _, totalProgress, description = packer.getData(quest)
            currentProgress, earned = self.__getTokenQuestProgress(questTokensCount)
        model.setIconKey(iconKey)
        model.setDescription(description)
        if not reset:
            model.setCurrentProgress(currentProgress)
            model.setTotalProgress(totalProgress)
            model.setEarned(earned)
            model.setIsCompleted(complete)
        self.__packBonuses(model, quest)
        return model

    def __packUncompletedTokenQuestModel(self, questTokensCount):
        currentProgress, earned = self.__getTokenQuestProgress(questTokensCount)
        if not earned:
            return
        else:
            nextTokenQuest = self.__getNextTokenQuest(currentProgress)
            if nextTokenQuest is None:
                return
            self.__tooltipData[nextTokenQuest.getID()] = {}
            model = Comp7WeeklyQuestProgressModel()
            model.setId(nextTokenQuest.getID())
            packer = Comp7TokenQuestPacker()
            iconKey, _, totalProgress, description = packer.getData(nextTokenQuest)
            model.setIconKey(iconKey)
            model.setDescription(description)
            model.setCurrentProgress(currentProgress)
            model.setTotalProgress(totalProgress)
            model.setEarned(earned)
            model.setIsCompleted(totalProgress <= currentProgress)
            self.__packBonuses(model, nextTokenQuest)
            return model

    def __getNextTokenQuest(self, currentProgress):
        comp7weeklyQuests = self.__comp7WeeklyQuestsCtrl.getQuests()
        allNextQuests = [ quest for _, quest in comp7weeklyQuests.sortedTokenQuests if currentProgress <= self.__getNeededTokensCount(quest) ]
        allNextQuests.sort(key=self.__getNeededTokensCount)
        return first(allNextQuests)

    def __getNeededTokensCount(self, quest):
        return quest.accountReqs.getConditions().find('token').getNeededCount()

    def __getTokenQuestProgress(self, questTokensCount):
        weeklyTokensProgress = questTokensCount.get(getComp7WeeklyQuestsCompleteToken())
        if not weeklyTokensProgress:
            return (0, 0)
        earned = weeklyTokensProgress.get('diff', 0)
        currentProgress = weeklyTokensProgress.get('total', 0)
        return (currentProgress, earned)

    def __packBonuses(self, model, quest):
        bonusPacker = getWeeklyPBSBonusPacker()
        packedBonuses, packedTooltips = packQuestBonuses(quest.getBonuses(), bonusPacker)
        self.__updateRewardsInTooltips(quest.getID(), packedBonuses, packedTooltips)
        fillViewModelsArray(packedBonuses, model.getBonuses())

    def __updateRewardsInTooltips(self, qID, packedBonuses, packedTooltips):
        for idx, tooltipData in enumerate(packedTooltips):
            self.__tooltipData[qID][str(idx)] = tooltipData
            packedBonuses[idx].setTooltipId(str(idx))

    def __getEarnedPoints(self, data, pCur, pPrev):
        for cond in data.bonusCond.getConditions().items:
            if isinstance(cond, conditions.Cumulativable):
                progressData = first(cond.getProgressPerGroup(pCur, pPrev, True).values())
                if progressData:
                    current, _, diff, _ = progressData
                else:
                    current = 0
                    diff = 0
                return (current, diff)
