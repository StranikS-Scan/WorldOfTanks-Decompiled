# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/personal_missions_widget.py
import logging
from account_helpers.settings_core.settings_constants import PersonalMission3
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getCurrentOperationLastInstalledDetail
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatus
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.personal_missions_30.personal_mission_constants import PM3_CAMPAIGN_ID
from gui.impl.lobby.personal_missions_30.views_helpers import getDetailNameByToken, getVehicleDetails, getDetailedOperationStatus, getSortedPm3Operations
from gui.server_events.pm_constants import IS_PM3_QUEST_ENABLED, DISABLED_PM_OPERATIONS
from gui.shared.event_dispatcher import showPersonalMissionMainWindow, showPersonalMissionCampaignSelectorWindow
from helpers import dependency
from personal_missions import PM_BRANCH
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.personal_missions_model import PersonalMissionsModel, State
from gui.impl.gen import R
from gui.server_events.event_items import PMOperation
_logger = logging.getLogger(__name__)
MIN_PM_POINTS = 0

class PersonalMissionsWindgetPresenter(ViewComponent[PersonalMissionsModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.PersonalMissions()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__personalMissionsCache = self.__eventsCache.getPersonalMissions()
        self.__pm3Campaign = self.__personalMissionsCache.getCampaignsForBranch(PM_BRANCH.PERSONAL_MISSION_3).get(PM3_CAMPAIGN_ID)
        self.__pm3Operations = getSortedPm3Operations()
        self.__currentOperation = None
        self.__linkedOperation = None
        super(PersonalMissionsWindgetPresenter, self).__init__(model=PersonalMissionsModel)
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsWindgetPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(PersonalMissionsWindgetPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsWindgetPresenter, self)._onLoading()
        self.__fillModel()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__eventsCache.onPMSyncCompleted, self.__onCacheSyncCompleted),
         (self.viewModel.goToOperation, self.__goToOperation),
         (self.viewModel.goToCampaigns, self.__goToCampaigns))

    def _finalize(self):
        self.__personalMissionsCache = {}
        self.__pm3Campaign = None
        self.__pm3Operations = {}
        self.__currentOperation = None
        self.__linkedOperation = None
        super(PersonalMissionsWindgetPresenter, self)._finalize()
        return

    def __onServerSettingsChanged(self, diff):
        if IS_PM3_QUEST_ENABLED in diff or DISABLED_PM_OPERATIONS in diff:
            self.__fillModel()

    def __onCacheSyncCompleted(self, *_):
        self.__fillModel()

    def __goToOperation(self):
        showPersonalMissionMainWindow(self.__linkedOperation.getID())

    def __goToCampaigns(self):
        showPersonalMissionCampaignSelectorWindow()

    def __getInProgressOperation(self):
        return findFirst(lambda op: op.isInProgress(), self.__pm3Operations.values()) if self.__pm3Operations else None

    def __getProgress(self):
        detailProgress = 0
        missionsProgress = 0
        if self.__currentOperation is not None:
            detailProgress = getCurrentOperationLastInstalledDetail(self.__currentOperation)
            missionsProgress = len(self.__currentOperation.getCompletedQuests())
        return (detailProgress, missionsProgress)

    def __getTotalPoints(self):
        return self.__personalMissionsCache.getOperationPmPointsData(PM_BRANCH.PERSONAL_MISSION_3, self.__currentOperation.getID()) if self.__currentOperation else (0, 0)

    def __isFirstTimeEntrance(self):
        return not self.__personalMissionsCache.isPM3Activated()

    def __fillModel(self):
        self.__pm3Operations = getSortedPm3Operations()
        _, previousMissionsProgress = self.__getProgress()
        self.__linkedOperation = self.__currentOperation = self.__getInProgressOperation()
        status, nextOperationID = getDetailedOperationStatus(self.__currentOperation) if self.__currentOperation else (None, None)
        nextOperation = self.__personalMissionsCache.getAllOperations(PM_BRANCH.V2_BRANCHES).get(nextOperationID) if nextOperationID else None
        if (not self.__currentOperation or self.__currentOperation and status == OperationStatus.PAUSED) and not self.__isFirstTimeEntrance():
            currentOperationID = self.__settingsCore.serverSettings.getLastFullCompletedPM3OperationID()
            if not currentOperationID:
                for operation in reversed(self.__pm3Operations.values()):
                    if operation.isFullCompleted():
                        currentOperationID = operation.getID()
                        self.__settingsCore.serverSettings.setPersonalMission3Data({PersonalMission3.LAST_FULL_COMPLETED_OP: currentOperationID})

            self.__currentOperation = self.__personalMissionsCache.getAllOperations(PM_BRANCH.V2_BRANCHES).get(currentOperationID)
        totalPoints, _ = self.__getTotalPoints()
        _, currentMissionsProgress = self.__getProgress()
        areAllOperationsCompleted = all((op.isCompleted() for op in self.__pm3Operations.values()))
        with self.viewModel.transaction() as tx:
            if self.__currentOperation:
                tx.setCurrentOperationName(self.__currentOperation.getUserName())
                tx.setCurrentOperationId(self.__currentOperation.getID())
                tx.setTotalProgress(self.__currentOperation.getQuestsCount())
                tx.setVehicleName(self.__currentOperation.getPM3VehicleBonus().descriptor.type.userString)
            if self.__isFirstTimeEntrance():
                tx.setState(State.CAMPAIGN_NOT_ACTIVATED)
                tx.setCampaignName(self.__pm3Campaign.getUserName())
            elif areAllOperationsCompleted and self.__currentOperation and not self.__currentOperation.isFullCompleted():
                tx.setState(State.IN_PROGRESS_FOR_HONORS)
                tx.setPreviousProgress(previousMissionsProgress)
                tx.setCurrentProgress(currentMissionsProgress)
            elif status in (OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR, OperationStatus.NOT_ALL_COMPLETED) or status == OperationStatus.PAUSED and self.__currentOperation:
                tx.setAllOperationsCompleted(status == OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR)
                self.__linkedOperation = nextOperation
                tx.setState(State.COMPLETED_WITH_HONORS)
            elif status == OperationStatus.NEXT_OPERATION_AVAILABLE or self.__currentOperation and self.__currentOperation.isCompleted() and not self.__currentOperation.isFullCompleted():
                nextOperation = findFirst(lambda o: o.getID() != self.__currentOperation.getID() and not o.isCompleted(), self.__pm3Operations.values())
                self.__linkedOperation = nextOperation
                tx.setState(State.COMPLETED)
            elif status == OperationStatus.ACTIVE:
                tx.setState(State.IN_PROGRESS)
                self.__fillDetailProgress(tx, totalPoints)
            if nextOperation:
                tx.setNextOperationName(nextOperation.getUserName())
                tx.setNextOperationId(nextOperation.getID())
        return

    def __fillDetailProgress(self, model, totalPoints):
        vehDetails = getVehicleDetails(self.__currentOperation)
        lastInstallDetailID = getCurrentOperationLastInstalledDetail(self.__currentOperation)
        minMilestonePoints = MIN_PM_POINTS if lastInstallDetailID is 0 else vehDetails[lastInstallDetailID - 1][1]
        maxMilestonePoints = vehDetails[lastInstallDetailID][1]
        maxDetailPoints = maxMilestonePoints - minMilestonePoints
        nextDetailID = lastInstallDetailID + 1
        detailID = getDetailNameByToken(vehDetails[lastInstallDetailID][0])
        model.setStageNumber(nextDetailID)
        model.setDetailId(detailID)
        previousPMPointsProgress = self.__settingsCore.serverSettings.getPersonalMission3Data().get(PersonalMission3.CHECKED_PM3_POINTS, 0)
        model.setPreviousProgress(previousPMPointsProgress - minMilestonePoints)
        currentDetailPoints = totalPoints - minMilestonePoints if totalPoints < maxMilestonePoints else maxDetailPoints
        model.setCurrentProgress(currentDetailPoints)
        model.setTotalProgress(maxDetailPoints)
        self.__settingsCore.serverSettings.setPersonalMission3Data({PersonalMission3.CHECKED_PM3_POINTS: totalPoints})
