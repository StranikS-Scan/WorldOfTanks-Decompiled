# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/missions_progress/personal_missions_progress.py
import typing
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.battle_results.progress.progress_helpers import isPMOperationAndMissionEnabled
from gui.impl.gen.view_models.views.lobby.battle_results.progression.personal_missions_progress_model import PersonalMissionsProgressModel
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen import R
from gui.impl.lobby.personal_missions_30.personal_mission_constants import MISSIONS_ROLES_TO_CATEGORIES
from gui.impl.lobby.personal_missions_30.views_helpers import getMissionConfigData
from gui.impl.lobby.personal_missions_30.bonus_packers import getBonusPacker, packMissionsBonusModelAndTooltipData
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.server_events.events_dispatcher import showPersonalMissionsChain
from gui.impl.lobby.personal_missions_30.tooltips.mission_progress_tooltip import MissionProgressTooltip
from gui.impl.backport import BackportTooltipWindow
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.gen.view_models.views.lobby.battle_results.progression.personal_missions_progress_model import PM3Status
from gui.impl.lobby.personal_missions_30.tooltips.missions_category_tooltip import MissionsCategoryTooltip
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from gui.server_events.finders import getBranchByOperationId
from helpers import dependency
from personal_missions import PM_BRANCH, PM_SWITCHES
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.impl.gen.view_models.views.lobby.personal_missions_30.quest_model import QuestModel

class PersonalMissionsProgressPresenter(ViewComponent[PersonalMissionsProgressModel], IProgressionCategoryPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, categoryProgressFilter, arenaUniqueID, *args, **kwargs):
        super(PersonalMissionsProgressPresenter, self).__init__(model=PersonalMissionsProgressModel)
        self.__personalMissions = self.__eventsCache.getPersonalMissions()
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__progress = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        self.__currentOperationOfPbs = None
        return

    @classmethod
    def getPathToResource(cls):
        return PersonalMissionsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.battle_results.progression.PersonalMissions()

    @property
    def viewModel(self):
        return super(PersonalMissionsProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
        return super(PersonalMissionsProgressPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        quest, isCompleted = self.__progress[0]
        if contentID == R.views.mono.personal_missions_30.tooltips.mission_progress_tooltip():
            return MissionProgressTooltip(mission=quest, isCompleted=isCompleted)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            bonuses = self.__bonusesModel[quest.getID()]
            return AdditionalRewardsTooltip(bonuses[int(showFromIndex):])
        if contentID == R.views.mono.personal_missions_30.tooltips.missions_category_tooltip():
            operationID, _ = self.__currentOperationOfPbs
            operation = self.__personalMissions.getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES).get(operationID)
            return MissionsCategoryTooltip(category=MissionCategory(event.getArgument('category')), operation=operation)
        return super(PersonalMissionsProgressPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate), (self.__eventsCache.getPersonalMissions().onSwitcherUpdated, self.__onSwitcherUpdated), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__currentOperationOfPbs = None
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__personalMissions = None
        super(PersonalMissionsProgressPresenter, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsProgressPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable)

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            event, isCompleted = self.__progress[0]
            eventId = event.getID()
            questConfig = getMissionConfigData(event)
            maxProgressValue = questConfig.maxProgressValue
            curBattlesUniqueVehiclesCount = len(event.getConditionsProgress().get('battlesUniqueVehicles', {}))
            currentProgressValue = maxProgressValue if isCompleted else curBattlesUniqueVehiclesCount
            pmType = event.getPMType()
            self.__currentOperationOfPbs = (pmType.tileID, MissionCategory(pmType.classifier.commonRole.lower()))
            pmOperations = self.__personalMissions.getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)
            operationFromPBS = pmOperations.get(pmType.tileID)
            bonusPacker = getBonusPacker(isOperationCompleted=operationFromPBS.isCompleted())
            model.setMissionName(event.getUserName())
            model.setMissionCategory(MISSIONS_ROLES_TO_CATEGORIES[pmType.getMajorTag()])
            model.setCurrentProgress(currentProgressValue)
            model.setMaxProgress(maxProgressValue)
            model.setAllQuestsRequired(questConfig.allQuestsRequired)
            model.setCurrentPM3Status(self.__getCampaignStatus(event.isCompleted(), pmOperations, operationFromPBS))
            model.setNavigationEnabled(isPMOperationAndMissionEnabled(event))
            questsArray = model.getQuests()
            questsArray.clear()
            for questID, questDetails in questConfig.questsDetails.items():
                questModel = model.getQuestsType()()
                questModel.setId(questID)
                questModel.setQuestType(questDetails['icon'])
                questModel.setSummary(questDetails['title'])
                questModel.setQuestCondition(questDetails['description'])
                questsArray.addViewModel(questModel)

            questsArray.invalidate()
            self.__fillRewards(eventId, model.getRewards(), event.getBonuses(), bonusPacker)

    @staticmethod
    def __getCampaignStatus(isQuestFullyCompleted, pmOperations, operationFromPBS):
        if all((operation.isFullCompleted(isFinalRewardReceived=False) for operation in pmOperations.values())):
            return PM3Status.CAMPAIGN_COMPLETED_WITH_HONOR
        if operationFromPBS.isFullCompleted(isFinalRewardReceived=False):
            return PM3Status.OPERATION_COMPLETED_WITH_HONOR
        return PM3Status.OPERATION_MISSION_PROGRESS if not isQuestFullyCompleted else PM3Status.OPERATION_MISSION_COMPLETE

    def __getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def __onNavigate(self):
        if self.__currentOperationOfPbs is not None:
            operationID, missionCategory = self.__currentOperationOfPbs
            showPersonalMissionsChain(operationID, 0, missionCategory)
        return

    def __fillRewards(self, eventId, rewardsModel, bonuses, packer):
        rewardsModel.clear()
        packMissionsBonusModelAndTooltipData(bonuses, packer, rewardsModel, self.__tooltipData)
        rewardsModel.invalidate()
        self.__bonusesModel[eventId] = rewardsModel

    def __onSwitcherUpdated(self):
        if not self.__progress:
            return
        self.__personalMissions = self.__eventsCache.getPersonalMissions()
        event, _ = self.__progress[0]
        pmEnabled = self.__personalMissions.isEnabled(getBranchByOperationId(event.getOperationID()))
        pmOperationEnabled = isPMOperationAndMissionEnabled(event)
        self.viewModel.setNavigationEnabled(pmEnabled and pmOperationEnabled)

    def __onServerSettingsChanged(self, diff=None):
        if not self.__progress:
            return
        else:
            self.__personalMissions = self.__eventsCache.getPersonalMissions()
            event, _ = self.__progress[0]
            operationID = event.getOperationID()
            navigationEnabled = self.__personalMissions.isEnabled(getBranchByOperationId(operationID))
            if diff.get(PM_SWITCHES.DISABLED_PM_OPERATIONS) is not None:
                disabledOperations = set(self.__personalMissions.getDisabledPMOperations())
                navigationEnabled = navigationEnabled and operationID not in disabledOperations
            self.viewModel.setNavigationEnabled(navigationEnabled)
            return
