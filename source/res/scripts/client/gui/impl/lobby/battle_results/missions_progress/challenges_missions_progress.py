# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/challenges_missions_progress.py
from __future__ import absolute_import
from challenges_common import isChallengeFailQuest
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.challenges.challenges_award_manager import AwardsManager
from gui.challenges.challenges_bonuses_packers import getChallengesPostBattleBonusPacker
from gui.challenges.challenges_decorators import createTooltipContentDecorator
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.progression.challenges_missions_progress_model import ChallengesMissionsProgressModel
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.challenges.views_helpers import parseChallengeQuestId
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.events_dispatcher import showChallenges
from gui.shared.missions.packers.events import ChallengeMissionUIDataPacker
from helpers import dependency
from shared_utils import first
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.server_events import IEventsCache

class ChallengesMissionsProgressPresenter(ViewComponent[ChallengesMissionsProgressModel], IProgressionCategoryPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __challenges = dependency.descriptor(IChallengesController)

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(ChallengesMissionsProgressPresenter, self).__init__(model=ChallengesMissionsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        self.__questID = None
        self.__challengeID = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        return

    @classmethod
    def getPathToResource(cls):
        return ChallengesMissionsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.Challenges()

    @property
    def viewModel(self):
        return super(ChallengesMissionsProgressPresenter, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengesMissionsProgressPresenter, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            questId = event.getArgument('questId')
            if questId == self.__questID:
                return AdditionalRewardsTooltip(self.__bonusesModel[int(showFromIndex):])
        return super(ChallengesMissionsProgressPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self.__tooltipData.get(missionParam)
        _, tooltipId = missionParams
        return self.__tooltipData.get(tooltipId, {})

    def _finalize(self):
        self.__questID = None
        self.__challengeID = None
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__allCommonQuests = None
        super(ChallengesMissionsProgressPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _onLoading(self, *args, **kwargs):
        super(ChallengesMissionsProgressPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable, self.__allCommonQuests)

    def _updateModel(self):
        data = first(self.__progress)
        if data is not None:
            quest, _, _, _, _ = data
            with self.viewModel as model:
                self.__createModel(model.challengeQuest, quest)
        return

    def __createModel(self, challengeQuestModel, quest):
        self.__questID = quest.getID()
        self.__tooltipData = {}
        self.__bonusesModel = {}
        self.__challengeID, questIndex = parseChallengeQuestId(self.__questID)
        challenge = self.__challenges.getChallenge(self.__challengeID)
        challengeQuestModel.setId(self.__questID)
        challengeQuestModel.setChallengeName(challenge.name)
        challengeQuestModel.setTotalProgress(len(challenge.questsIDs))
        if isChallengeFailQuest(self.__questID):
            challengeQuestModel.setCurrentProgress(questIndex - 1)
        else:
            challengeQuestModel.setIsCompleted(True)
            challengeQuestModel.setCurrentProgress(questIndex)
        packer = ChallengeMissionUIDataPacker(quest)
        packer.pack(challengeQuestModel)
        bonuses = challengeQuestModel.getBonuses()
        bonuses.clear()
        packBonusModelAndTooltipData(AwardsManager.sortVisibleBonuses(quest.getBonuses(), reverse=True), bonuses, tooltipData=self.__tooltipData, packer=getChallengesPostBattleBonusPacker(), showAttachmentsSets=False)
        self.__bonusesModel = challengeQuestModel.getBonuses()
        self.__setNavigationStatus(challengeQuestModel, challenge)

    def __setNavigationStatus(self, model, challenge):
        model.setNavigationEnabled(self.__challenges.isEnabled and challenge.isAvailable)

    def __onNavigate(self):
        showChallenges(challengeID=self.__challengeID)
