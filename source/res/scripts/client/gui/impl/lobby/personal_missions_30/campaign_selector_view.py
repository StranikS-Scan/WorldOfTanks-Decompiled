# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/campaign_selector_view.py
from typing import TYPE_CHECKING
from AccountCommands import LOCK_REASON
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getSuitableVehicles, switchCampaign, processPM3Operation
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.campaign_model import CampaignModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.campaign_selector_model import CampaignSelectorModel, CampaignSelectorViewState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_model import OperationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel
from gui.impl.lobby.personal_missions_30.personal_mission_constants import PERSONAL_MISSIONS_CAMPAIGN_SELECTOR_SPACE, IntroKeys
from gui.impl.lobby.personal_missions_30.views_helpers import getOperationStatus, getSortedPm3Operations, isIntroShown
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.events_dispatcher import showPersonalMissionOperationsPage
from gui.server_events.finders import getBranchByOperationId, BRANCH_TO_OPERATION_IDS
from gui.shared.event_dispatcher import showPersonalMissionMainWindow, showPM30IntroWindow
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Tuple
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
        self._firstTwoSeasonsAreCompletedWithHonors = False
        self._suitableVehicles = False
        self._isFirstTimeEntrance = False
        self._operations = self._personalMissions.getAllOperations(PM_BRANCH.V2_BRANCHES)
        self._campaigns = self.__eventsCache.getPersonalMissions().getAllCampaigns(branches=PM_BRANCH.ALL)

    @property
    def viewModel(self):
        return super(CampaignSelectorView, self).getViewModel()

    def _finalize(self):
        super(CampaignSelectorView, self)._finalize()
        self._personalMissions = None
        self._campaigns = None
        return

    def _onLoaded(self, *args, **kwargs):
        if not self._suitableVehicles and not self._progressInFirstTwoSeasons:
            return
        showPM30IntroWindow()

    def _getEvents(self):
        return ((self.viewModel.onOperation, self._onEnterTheOperation),
         (self.viewModel.onMoreInfo, self._onMoreInfo),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.switchCampaign, self._switchCampaign),
         (self.__eventsCache.onPMSyncCompleted, self._onEventCacheSyncCompleted),
         (self.__itemsCache.onSyncCompleted, self.__onItemsSyncCompleted),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        switchers = ['disabledPMOperations', 'isPM2QuestEnabled', 'isPM3QuestEnabled']
        if not self._personalMissions.isEnabled():
            self.__onClose()
        elif any((switcher in diff for switcher in switchers)):
            self._onEventCacheSyncCompleted()

    def _onLoading(self, *args, **kwargs):
        super(CampaignSelectorView, self)._onLoading(*args, **kwargs)
        self._suitableVehicles = True if getSuitableVehicles() else False
        self._fillModel()

    def _onEventCacheSyncCompleted(self, *_):
        self._personalMissions = self.__eventsCache.getPersonalMissions()
        self._fillModel()

    def __onItemsSyncCompleted(self, _, __):
        activeCampaigns = self._personalMissions.getActiveCampaigns()
        with self.viewModel.transaction() as vm:
            vm.setBlockedByVehicle(self._isLockedByVeh(activeCampaigns))

    def _onVehicleLockChanged(self, _, lockReason):
        if lockReason[0] == LOCK_REASON.NONE:
            self._fillModel()

    def _onMoreInfo(self, *_):
        pass

    def __onClose(self):
        lsm = getLobbyStateMachine()
        lsm.getStateFromView(self).goBack()

    def _onEnterTheOperation(self, data):
        operationID = int(data.get(self.viewModel.OPERATION_ID, 0))
        if operationID:
            branch = getBranchByOperationId(operationID)
            if branch == PM_BRANCH.PERSONAL_MISSION_3:
                showPersonalMissionMainWindow(operationID)
            else:
                showPersonalMissionOperationsPage(branch, operationID)

    @adisp_process
    def _switchCampaign(self, data):
        waitingId = ACTIVATE_WAITING_ID if self._isFirstTimeEntrance else SWITCH_WAITING_ID
        Waiting.show(waitingId, showBg=False)
        campaignsState = data.get(self.viewModel.CAMPAIGNS_STATE, CampaignSelectorViewState.THIRD.value)
        campaignToActive = PM_BRANCH.REGULAR if campaignsState == CampaignSelectorViewState.FIRST_TWO.value else PM_BRANCH.PERSONAL_MISSION_3
        res = yield switchCampaign(campaignToActive, isFirstTimeEntrance=self._isFirstTimeEntrance)
        if not res.success:
            Waiting.hide(waitingId)
            return
        if self._isFirstTimeEntrance and campaignsState == CampaignSelectorViewState.THIRD.value:
            firstCampaign3OperationID = BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_3][0]
            introKey = IntroKeys.OPERATION_INTRO_VIEW.value % firstCampaign3OperationID
            isFirtOperationEntrance = True
            if self._isFirstTimeEntrance and isIntroShown(introKey):
                isFirtOperationEntrance = False
            res = yield processPM3Operation(PM_BRANCH.PERSONAL_MISSION_3, firstCampaign3OperationID, isFirstTimeEntrance=isFirtOperationEntrance)
            if res.success and self.viewStatus == ViewStatus.LOADED:
                self._fillModel()
                showPersonalMissionMainWindow(firstCampaign3OperationID)
        Waiting.hide(waitingId)

    def _fillModel(self):
        self._operations = self._personalMissions.getAllOperations(PM_BRANCH.V2_BRANCHES)
        isFirstTimeEntrance = not any((operation.isStarted() for operation in self._operations.values()))
        self._isFirstTimeEntrance = isFirstTimeEntrance
        with self.viewModel.transaction() as vm:
            campaignsList = vm.getCampaigns()
            campaignsList.clear()
            isAllOperationsWithHonors = True
            progressInFirstTwoSeasons = False
            firstTwoSeasonsAreCompletedWithHonors = []
            campaignId = None
            for branch in PM_BRANCH.ALL:
                operations = self._personalMissions.getAllOperations((branch,))
                cm = vm.getCampaignsType()()
                operationsList = cm.getOperations()
                isCampaignWithHonors = True
                for operationID, operation in operations.items():
                    om = cm.getOperationsType()()
                    om.setOperationId(operationID)
                    om.setActive(operation.isInProgress())
                    campaignId = operation.getCampaignID()
                    om.setOperationName(operation.getShortUserName())
                    om.setOperationIcon(operation.getIconID())
                    state = getOperationStatus(operation, getSortedPm3Operations())
                    om.setCompleted(operation.isAwardAchieved())
                    om.setState(state)
                    if state != OperationState.COMPLETED_WITH_HONORS:
                        isAllOperationsWithHonors = False
                        isCampaignWithHonors = False
                    operationsList.addViewModel(om)
                    if branch in PM_BRANCH.V1_BRANCHES and operation.isStarted():
                        progressInFirstTwoSeasons = True

                if campaignId is not None:
                    cm.setCampaignName(self._campaigns.get(campaignId).getUserName())
                if branch in PM_BRANCH.V1_BRANCHES:
                    firstTwoSeasonsAreCompletedWithHonors.append(isCampaignWithHonors)
                cm.setCompletedWithHonor(isCampaignWithHonors)
                campaignsList.addViewModel(cm)

            campaignsList.invalidate()
            self._progressInFirstTwoSeasons = progressInFirstTwoSeasons
            self._firstTwoSeasonsAreCompletedWithHonors = all(firstTwoSeasonsAreCompletedWithHonors)
            activeCampaigns = self._personalMissions.getActiveCampaigns()
            self._activeSeason = self._getSeasonState(isAllOperationsWithHonors, activeCampaigns, isFirstTimeEntrance)
            vm.setCampaignSelectorViewState(self._activeSeason)
            if isFirstTimeEntrance and self._progressInFirstTwoSeasons:
                activeCampaigns = (PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.REGULAR], PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_2])
            vm.setBlockedByVehicle(self._isLockedByVeh(activeCampaigns))
            vm.setFirstTimeEntrance(isFirstTimeEntrance)
        return

    def _getSeasonState(self, isAllOperationsWithHonors, activeCampaigns, isFirstTimeEntrance):
        if not self._suitableVehicles and not self._progressInFirstTwoSeasons:
            activeSeason = CampaignSelectorViewState.LOCKED
        elif isAllOperationsWithHonors:
            activeSeason = CampaignSelectorViewState.COMPLETED_WITH_HONOR
        elif isFirstTimeEntrance:
            if self._progressInFirstTwoSeasons and not self._firstTwoSeasonsAreCompletedWithHonors:
                activeSeason = CampaignSelectorViewState.FIRST_TWO
            else:
                activeSeason = CampaignSelectorViewState.THIRD
        elif PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.REGULAR] in activeCampaigns or PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_2] in activeCampaigns:
            activeSeason = CampaignSelectorViewState.FIRST_TWO
        else:
            activeSeason = CampaignSelectorViewState.THIRD
        return activeSeason

    def _isLockedByVeh(self, activeCampaigns):
        for campaign in activeCampaigns:
            campaignType = PM_BRANCH.NAME_TO_TYPE[campaign]
            selectedQuestsInActiveBranch = self._personalMissions.getSelectedQuestsForBranch(campaignType).values()
            lockedChains = self.__eventsCache.getLockedQuestTypes(campaignType)
            for quest in selectedQuestsInActiveBranch:
                if quest.getMajorTag() in lockedChains:
                    return True

        return False


class CampaignSelectorWindow(WindowImpl):
    _OPAQUE_BACKGROUND_ALPHA = 1.0

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = self._OPAQUE_BACKGROUND_ALPHA
        super(CampaignSelectorWindow, self).__init__(content=CampaignSelectorView(R.views.mono.personal_missions_30.campaign_selector()), wndFlags=WindowFlags.WINDOW, layer=layer)
