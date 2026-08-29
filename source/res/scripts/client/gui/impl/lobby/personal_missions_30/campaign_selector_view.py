# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/campaign_selector_view.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getSuitableVehicles, processPMOperation, switchCampaign
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.campaign_model import CampaignModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.campaign_selector_model import CampaignSelectorModel, CampaignSelectorViewState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_model import OperationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel
from gui.impl.lobby.personal_missions_30.personal_mission_constants import PERSONAL_MISSIONS_CAMPAIGN_SELECTOR_SPACE, IntroKeys
from gui.impl.lobby.personal_missions_30.views_helpers import getOperationStatus, isIntroShown, isPMCampaignsStarted, firstUnclaimedOperation, getBranchSortedPmOperations
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.events_dispatcher import showPersonalMissionOperationsPage
from gui.server_events.finders import getBranchByOperationId
from gui.shared.event_dispatcher import showPersonalMissionMainWindow, showPM30IntroWindow
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from personal_missions import PM_BRANCH, PM_SWITCHES
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.server_events.event_items import PMOperation
ACTIVATE_WAITING_ID = 'activateCampaign'
SWITCH_WAITING_ID = 'switchCampaign'

class CampaignSelectorView(ViewImpl):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_CAMPAIGN_SELECTOR_SPACE
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=CampaignSelectorModel())
        super(CampaignSelectorView, self).__init__(settings)
        self._personalMissions = self.__eventsCache.getPersonalMissions()
        self._activeSeason = CampaignSelectorViewState.THIRD
        self._progressInFirstTwoSeasons = False
        self._progressInWithoutAwardListSeasons = False
        self._firstTwoSeasonsAreCompletedWithHonors = False
        self._suitableVehicles = False
        self._isFirstTimeEntrance = False
        self._campaigns = self.__eventsCache.getPersonalMissions().getAllCampaigns(PM_BRANCH.ALL_NAMES)

    @property
    def viewModel(self):
        return super(CampaignSelectorView, self).getViewModel()

    def _finalize(self):
        super(CampaignSelectorView, self)._finalize()
        self._personalMissions = None
        self._campaigns = {}
        return

    def _onLoaded(self, *args, **kwargs):
        if not self._suitableVehicles and not self._progressInFirstTwoSeasons:
            return
        showPM30IntroWindow()

    def _getEvents(self):
        return ((self.viewModel.onOperation, self._onEnterTheOperation),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.switchCampaign, self._switchCampaign),
         (self.__eventsCache.onPMSyncCompleted, self._onEventCacheSyncCompleted),
         (self.__itemsCache.onSyncCompleted, self.__onItemsSyncCompleted),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        switchers = (PM_SWITCHES.DISABLED_PM_OPERATIONS,) + PM_SWITCHES.ALL
        if not self._personalMissions.isEnabled():
            self.__onClose()
        elif any((switcher in diff for switcher in switchers)):
            self._onEventCacheSyncCompleted()

    def _onLoading(self, *args, **kwargs):
        super(CampaignSelectorView, self)._onLoading(*args, **kwargs)
        self._suitableVehicles = bool(getSuitableVehicles())
        self._fillModel()

    def _onEventCacheSyncCompleted(self, *_):
        self._personalMissions = self.__eventsCache.getPersonalMissions()
        self._fillModel()

    def __onItemsSyncCompleted(self, _, diff=None):
        diff = diff or {}
        if not self._suitableVehicles and GUI_ITEM_TYPE.VEHICLE in diff:
            self._suitableVehicles = bool(getSuitableVehicles())
            if self._suitableVehicles:
                self._fillModel()
                showPM30IntroWindow()
        else:
            activeCampaigns = self._personalMissions.getActiveCampaigns()
            with self.viewModel.transaction() as vm:
                vm.setBlockedByVehicle(self._isLockedByVeh(activeCampaigns))

    def __onClose(self):
        lsm = getLobbyStateMachine()
        lsm.getStateFromView(self).goBack()

    def _onEnterTheOperation(self, data):
        operationID = int(data.get(self.viewModel.OPERATION_ID, 0))
        if operationID:
            branch = getBranchByOperationId(operationID)
            if PM_BRANCH.TYPE_TO_NAME[branch] in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
                showPersonalMissionMainWindow(operationID)
            else:
                showPersonalMissionOperationsPage(branch, operationID)

    @adisp_process
    def _switchCampaign(self, data):
        waitingId = ACTIVATE_WAITING_ID if self._isFirstTimeEntrance else SWITCH_WAITING_ID
        Waiting.show(waitingId, showBg=False)
        campaignsState = data.get(self.viewModel.CAMPAIGNS_STATE, CampaignSelectorViewState.THIRD.value)
        if campaignsState == CampaignSelectorViewState.FIRST_TWO.value:
            branchToActivate = first(PM_BRANCH.convertNameToType(PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_1]), PM_BRANCH.REGULAR)
        else:
            lastActiveOperationID = self._personalMissions.getLastActiveOperationID()
            branchToActivate = getBranchByOperationId(lastActiveOperationID) if lastActiveOperationID else PM_BRANCH.PERSONAL_MISSION_3
        res = yield switchCampaign(branchToActivate)
        if res:
            Waiting.hide(waitingId)
            return
        if campaignsState == CampaignSelectorViewState.THIRD.value:
            operations = self._personalMissions.getOperationsForBranch(branchToActivate)
            branchName = PM_BRANCH.TYPE_TO_NAME[branchToActivate]
            needToProcessBranchOperation = not isPMCampaignsStarted((branchName,))
            lastUncompletedOperation = self._getLastUncompletedOperation(operations)
            if needToProcessBranchOperation or lastUncompletedOperation:
                if needToProcessBranchOperation:
                    operationToProcess = firstUnclaimedOperation(operations.values())
                    operationToProcessID = operationToProcess.getID() if operationToProcess else PM_BRANCH.BRANCH_TO_OPERATION_IDS[branchToActivate][0]
                    introKey = IntroKeys.OPERATION_INTRO_VIEW.value % operationToProcessID
                    isFirstTimeEntrance = self._isFirstTimeEntrance
                    isFirstOperationEntrance = not (isFirstTimeEntrance and isIntroShown(introKey, branchToActivate))
                else:
                    operationToProcessID = lastUncompletedOperation.getID()
                    isFirstOperationEntrance = isFirstTimeEntrance = False
                res = yield processPMOperation(branchToActivate, operationToProcessID, isFirstTimeEntrance=isFirstOperationEntrance)
                if res.success and isFirstTimeEntrance and self.viewStatus == ViewStatus.LOADED:
                    showPersonalMissionMainWindow(operationToProcessID)
        Waiting.hide(waitingId)

    def _fillModel(self):
        allOperations = self._personalMissions.getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)
        isBranchWithAwardListActive = self._personalMissions.isBranchWithAwardListActive()
        activeCampaigns = self._personalMissions.getActiveCampaigns()
        lastActiveOperationID = self._personalMissions.getLastActiveOperationID()
        self._isFirstTimeEntrance = not any((operation.isStarted() for operation in allOperations.values()))
        with self.viewModel.transaction() as vm:
            campaignsList = vm.getCampaigns()
            campaignsList.clear()
            isAllOperationsWithHonors = True
            progressInFirstTwoSeasons = False
            progressInWithoutAwardListSeasons = False
            firstTwoSeasonsAreCompletedWithHonors = []
            campaignId = None
            for branch in PM_BRANCH.ALL:
                branchOperations = getBranchSortedPmOperations(branch)
                cm = vm.getCampaignsType()()
                operationsList = cm.getOperations()
                isCampaignWithHonors = True
                isFirstTwoCampaignBranch = PM_BRANCH.TYPE_TO_NAME[branch] in PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_1]
                for operationID, operation in branchOperations.items():
                    om = cm.getOperationsType()()
                    om.setOperationId(operationID)
                    om.setActive(self._isOperationActive(operation, isBranchWithAwardListActive, activeCampaigns, lastActiveOperationID))
                    campaignId = operation.getCampaignID()
                    om.setOperationName(operation.getShortUserName())
                    om.setOperationIcon(operation.getIconID())
                    state = getOperationStatus(operation, branchOperations)
                    om.setCompleted(operation.isAwardAchieved())
                    om.setState(state)
                    if state != OperationState.COMPLETED_WITH_HONORS:
                        isAllOperationsWithHonors = False
                        isCampaignWithHonors = False
                    operationsList.addViewModel(om)
                    if isFirstTwoCampaignBranch and not progressInFirstTwoSeasons:
                        progressInFirstTwoSeasons = operation.isStarted()
                    if operation.isWithoutAwardListBranch() and not progressInWithoutAwardListSeasons:
                        progressInWithoutAwardListSeasons = operation.isStarted()

                if campaignId is not None:
                    cm.setCampaignName(self._campaigns.get(campaignId).getUserName())
                if isFirstTwoCampaignBranch:
                    firstTwoSeasonsAreCompletedWithHonors.append(isCampaignWithHonors)
                cm.setCompletedWithHonor(isCampaignWithHonors)
                campaignsList.addViewModel(cm)

            campaignsList.invalidate()
            self._progressInFirstTwoSeasons = progressInFirstTwoSeasons
            self._progressInWithoutAwardListSeasons = progressInWithoutAwardListSeasons
            self._firstTwoSeasonsAreCompletedWithHonors = all(firstTwoSeasonsAreCompletedWithHonors)
            self._activeSeason = self._getSeasonState(isAllOperationsWithHonors, activeCampaigns, self._isFirstTimeEntrance)
            vm.setCampaignSelectorViewState(self._activeSeason)
            if self._isFirstTimeEntrance and self._progressInFirstTwoSeasons:
                activeCampaigns = PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_1]
            vm.setBlockedByVehicle(self._isLockedByVeh(activeCampaigns))
            vm.setFirstTimeEntrance(self._isFirstTimeEntrance)
        return

    def _getSeasonState(self, isAllOperationsWithHonors, activeCampaigns, isFirstTimeEntrance):
        if not (self._suitableVehicles or self._progressInFirstTwoSeasons or self._progressInWithoutAwardListSeasons):
            activeSeason = CampaignSelectorViewState.LOCKED
        elif isAllOperationsWithHonors:
            activeSeason = CampaignSelectorViewState.COMPLETED_WITH_HONOR
        elif isFirstTimeEntrance:
            if self._progressInFirstTwoSeasons and not self._firstTwoSeasonsAreCompletedWithHonors:
                activeSeason = CampaignSelectorViewState.FIRST_TWO
            else:
                activeSeason = CampaignSelectorViewState.THIRD
        elif PM_BRANCH.PM1_NAME in activeCampaigns or PM_BRANCH.PM2_NAME in activeCampaigns:
            activeSeason = CampaignSelectorViewState.FIRST_TWO
        else:
            activeSeason = CampaignSelectorViewState.THIRD
        return activeSeason

    @staticmethod
    def _getLastUncompletedOperation(operations):
        opsCount = len(operations)
        completedWithHonorsOpsCount = len([ op for op in operations.values() if op.isFullCompleted() ])
        completedWithoutHonorsOps = [ op for op in operations.values() if op.isCompleted() and not op.isFullCompleted() ]
        isOneOpNotCompletedWithHonor = opsCount - completedWithHonorsOpsCount == 1 and completedWithoutHonorsOps
        return completedWithoutHonorsOps[0] if isOneOpNotCompletedWithHonor else None

    def _isLockedByVeh(self, activeCampaigns):
        for branchName in activeCampaigns:
            branchID = PM_BRANCH.NAME_TO_TYPE[branchName]
            selectedQuestsInActiveBranch = self._personalMissions.getSelectedQuestsForBranch(branchID).values()
            lockedChains = self.__eventsCache.getLockedQuestTypes(branchID)
            for quest in selectedQuestsInActiveBranch:
                if quest.getMajorTag() in lockedChains:
                    return True

        return False

    def _isOperationActive(self, operation, isBranchWithAwardListActive, activeCampaigns, lastActiveOperationID):
        if operation.isFullCompleted():
            return False
        if operation.isWithAwardListBranch():
            return operation.isInProgress()
        if isBranchWithAwardListActive:
            return lastActiveOperationID == operation.getID()
        if operation.getBranchName() not in activeCampaigns:
            return False
        selectedQuestInActiveBranch = first(self._personalMissions.getSelectedQuestsForBranch(operation.getBranch()).values())
        if selectedQuestInActiveBranch:
            operationID = selectedQuestInActiveBranch.getOperationID()
            return operationID == operation.getID() and not operation.isPaused()
        return operation.isActive() or operation.isFullCompleted(isFinalRewardReceived=False)


class CampaignSelectorWindow(WindowImpl):
    _OPAQUE_BACKGROUND_ALPHA = 1.0

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = self._OPAQUE_BACKGROUND_ALPHA
        super(CampaignSelectorWindow, self).__init__(content=CampaignSelectorView(R.views.mono.personal_missions_30.campaign_selector()), wndFlags=WindowFlags.WINDOW, layer=layer)
