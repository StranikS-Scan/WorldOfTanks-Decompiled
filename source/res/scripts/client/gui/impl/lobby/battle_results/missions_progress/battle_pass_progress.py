# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/battle_pass_progress.py
import typing
from battle_pass_common import BattlePassConsts, NON_CHAPTER_ID, isPostProgressionChapter
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.progression.battle_pass_progress_model import BattlePassProgressModel
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalBattlePassRewardsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.impl.wrappers.user_list_model import UserListModel
from gui.shared.event_dispatcher import showBattlePass
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import BattlePassProgress

class BattlePassProgressPresenter(ViewComponent[BattlePassProgressModel], IProgressionCategoryPresenter):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, categoryProgressFilter, arenaUniqueID, *args, **kwargs):
        super(BattlePassProgressPresenter, self).__init__(model=BattlePassProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__progress = None
        self.__tooltipItems = {}
        self.__chapter = None
        return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassProgressPresenter, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalBattlePassRewardsTooltip():
            showFromIndex = int(event.getArgument('showFromIndex'))
            rewardType = event.getArgument('rewardType')
            level = int(event.getArgument('level'))
            chapter = int(event.getArgument('chapter'))
            if rewardType == BattlePassConsts.REWARD_BOTH:
                freeAwards = self.__progress.getLevelAwardsByType(chapter, level + 1, BattlePassConsts.REWARD_FREE)
                paidAwards = self.__progress.getLevelAwardsByType(chapter, level + 1, BattlePassConsts.REWARD_PAID)
                awards = freeAwards + paidAwards
            else:
                awards = self.__progress.getLevelAwardsByType(chapter, level + 1, rewardType)
            model = AdditionalRewardsTooltipModel().getBonus()
            packBonusModelAndTooltipData(awards, model)
            return AdditionalBattlePassRewardsTooltip(model[int(showFromIndex):])

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    @classmethod
    def getPathToResource(cls):
        return BattlePassProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.BattlePass()

    @property
    def viewModel(self):
        return super(BattlePassProgressPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())
        self.__packBattlePassProgress()

    def _finalize(self):
        self.__tooltipItems = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__progress = None
        self.__chapter = None
        super(BattlePassProgressPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate), (self.__battlePassController.onBattlePassSettingsChange, self.__onSettingsChange), (self.__battlePassController.onSeasonStateChanged, self.__onSeasonStateChanged))

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable)

    def __packBattlePassProgress(self):
        with self.viewModel.transaction() as model:
            if not self.__progress:
                return
            isHoliday = self.__battlePassController.isHoliday()
            currentChapter = self.__progress.currentChapterID
            previousChapter = self.__progress.previousChapterID
            model.setPreviousChapterID(self.__progress.previousChapterID)
            model.setCurrentChapterID(currentChapter)
            if currentChapter == NON_CHAPTER_ID and previousChapter != NON_CHAPTER_ID:
                self.__chapter = previousChapter
            else:
                self.__chapter = currentChapter
            maxLevelPoints = self.__progress.getMaxLevelPoints(currentChapter)
            level = self.__progress.getCurrentLevel(currentChapter)
            previousMaxLevelPoints = self.__progress.getMaxLevelPoints(previousChapter)
            self.__packAwards(self.__progress, self.__chapter, level, model)
            model.setHasBattlePass(self.__progress.hasBattlePass)
            model.setBattlePassComplete(self.__progress.battlePassComplete)
            model.setAvailablePoints(self.__progress.availablePoints)
            model.setBpTopPoints(self.__progress.bpTopPoints)
            model.setPointsAux(self.__progress.pointsAux)
            model.setQuestPoints(self.__progress.questPoints)
            model.setBonusCapPoints(self.__progress.bonusCapPoints)
            model.setCurrentLevelPoints(self.__progress.getCurrentLevelPoints(self.__chapter))
            model.setMaxLevelPoints(maxLevelPoints)
            model.setCurrentLevel(level)
            pointsDiff = self.__progress.getPointsDiff(self.__chapter) if not isHoliday else self.__progress.getPointsDiff(currentChapter)
            model.setPointsDiff(pointsDiff)
            model.setLevelReached(self.__progress.isLevelReached(self.__chapter))
            model.setPreviousMaxLevelPoints(previousMaxLevelPoints)
            model.setExtraChapter(self.__battlePassController.isExtraChapter(self.__chapter))
            model.setPreviousChapterBought(self.__battlePassController.isBought(previousChapter))
            if currentChapter != previousChapter and self.__progress.battlePassComplete:
                model.setLevelMax(True)
                model.setPreviousLevel(self.__progress.getPreviousLevel(previousChapter))
            else:
                model.setPreviousLevel(self.__progress.getPreviousLevel(self.__chapter))
                model.setLevelMax(self.__progress.isLevelMax(self.__chapter))
            model.setNavigationEnabled(not self.__battlePassController.isDisabled())
            model.setHolidayBattlePass(isHoliday)
            if maxLevelPoints != 0:
                numberOfLevels = self.__battlePassController.getLevelsConfig(currentChapter)[-1] / maxLevelPoints
            else:
                numberOfLevels = 0
            if previousMaxLevelPoints:
                model.setLevelsInPreviousChapter(self.__battlePassController.getLevelsConfig(previousChapter)[-1] / previousMaxLevelPoints)
            model.setLevelsInPostProgression(numberOfLevels)

    def __packAwards(self, progress, currentChapter, level, model):
        rewardTypes = [(BattlePassConsts.REWARD_FREE, model.getCurrentFreeAwards()), (BattlePassConsts.REWARD_PAID, model.getCurrentPaidAwards())]
        for rewardType, currentAwardsModel in rewardTypes:
            currentAwards = progress.getLevelAwardsByType(progress.currentChapterID, level + 1, rewardType)
            packBonusModelAndTooltipData(currentAwards, currentAwardsModel, self.__tooltipItems)

        if currentChapter != progress.previousChapterID and progress.battlePassComplete:
            chapter = progress.previousChapterID
        else:
            chapter = progress.currentChapterID
        if progress.isLevelReached(chapter) or progress.isLevelReached(progress.previousChapterID):
            previousModels = [(BattlePassConsts.REWARD_FREE, model.getPreviousFreeAwards()), (BattlePassConsts.REWARD_PAID, model.getPreviousPaidAwards())]
            for rewardType, getPrevModel in previousModels:
                previousAwardsModel = getPrevModel
                previousAwardsModel.clear()
                if progress.currentChapterID != progress.previousChapterID:
                    for lvl in xrange(progress.getPreviousLevel(progress.previousChapterID), progress.getCurrentLevel(progress.previousChapterID)):
                        previousAwards = progress.getLevelAwardsByType(progress.previousChapterID, lvl + 1, rewardType)
                        previousAwardModel = UserListModel()
                        packBonusModelAndTooltipData(previousAwards, previousAwardModel, self.__tooltipItems)
                        previousAwardsModel.addViewModel(previousAwardModel)

                for lvl in xrange(progress.getPreviousLevel(currentChapter), progress.getCurrentLevel(currentChapter)):
                    previousAwards = progress.getLevelAwardsByType(currentChapter, lvl + 1, rewardType)
                    previousAwardModel = UserListModel()
                    packBonusModelAndTooltipData(previousAwards, previousAwardModel, self.__tooltipItems)
                    previousAwardsModel.addViewModel(previousAwardModel)

                previousAwardsModel.invalidate()

    def __onNavigate(self):
        chapterID = self.__chapter if not isPostProgressionChapter(self.__chapter) and not self.__progress.hasBattlePass and self.__battlePassController.isChapterExists(self.__chapter) else None
        showBattlePass(R.aliases.battle_pass.Progression() if chapterID else None, chapterID, directNavigation=True)
        return

    def __onSettingsChange(self, *_):
        self.viewModel.setNavigationEnabled(not self.__battlePassController.isDisabled() and not self.__battlePassController.isPaused())

    def __onSeasonStateChanged(self):
        self.viewModel.setNavigationEnabled(not self.__battlePassController.isDisabled())
