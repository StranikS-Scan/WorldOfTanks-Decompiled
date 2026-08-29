# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/personal_missions_widget.py
from __future__ import absolute_import
import typing
from account_helpers.settings_core.settings_constants import PersonalMission3
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatus
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.personal_missions_30.views_helpers import getDetailNameByToken, getVehicleDetails, getDetailedOperationStatus, getBranchesSortedPmOperations, getPersonalMissionData, getCheckedPMPointsKey, setPersonalMissionData, getCurrentOperationLastInstalledDetail
from gui.shared.event_dispatcher import showPersonalMissionMainWindow, showPersonalMissionCampaignSelectorWindow
from helpers import dependency
from personal_missions import PM_BRANCH, PM_SWITCHES
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.personal_missions_model import PersonalMissionsModel, State
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional
    from collections import OrderedDict
    from gui.server_events.event_items import PMOperation
    UnpackedOp = Tuple[Optional[PMOperation], Optional[PMOperation], Optional[OperationStatus]]
MIN_PM_POINTS = 0
_OP_NOT_COMPLETE = {OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR, OperationStatus.NOT_ALL_COMPLETED}
_NEXT_OP_AVAILABLE = OperationStatus.NEXT_OPERATION_AVAILABLE

class PersonalMissionsWindgetPresenter(ViewComponent[PersonalMissionsModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.PersonalMissions()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__pmCache = self.__eventsCache.getPersonalMissions()
        self.__currentOperation = None
        self.__linkedOperation = None
        super(PersonalMissionsWindgetPresenter, self).__init__(model=PersonalMissionsModel)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

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
        self.__pmCache = None
        self.__currentOperation = None
        self.__linkedOperation = None
        super(PersonalMissionsWindgetPresenter, self)._finalize()
        return

    def __onServerSettingsChanged(self, diff):
        switchers = (PM_SWITCHES.DISABLED_PM_OPERATIONS,) + PM_SWITCHES.WITHOUT_AWARD_LIST_SWITCHERS
        if any((switcher in diff for switcher in switchers)):
            self.__fillModel()

    def __onCacheSyncCompleted(self, *_):
        self.__fillModel()

    def __goToOperation(self):
        showPersonalMissionMainWindow(self.__linkedOperation.getID())

    def __goToCampaigns(self):
        showPersonalMissionCampaignSelectorWindow()

    def __findAndUnpackFirstInProgressOperation(self, opsByID):
        activeCampaigns = self.__pmCache.getActiveCampaigns()
        inProgressOperations = [ operation for operation in opsByID.values() if operation.isInProgress() ]
        activeCampaignInProgressOperation = first((operation for operation in inProgressOperations if operation.getBranchName() in activeCampaigns))
        operationInProgress = activeCampaignInProgressOperation or first(inProgressOperations)
        if operationInProgress:
            status, nextOp = getDetailedOperationStatus(operationInProgress, opsByID)
            return (operationInProgress, nextOp, status)
        else:
            return (None, None, None)

    def __findAndUnpackNextOpIfNoCurrent(self, isWithoutAwardListBranchActivated, opsByID, unpackedOp):
        currOp, nextOp, status = unpackedOp
        if isWithoutAwardListBranchActivated and (not currOp or currOp and status == OperationStatus.PAUSED):
            serverSettings = self.__settingsCore.serverSettings
            currentOperationID = serverSettings.getLastFullCompletedPM3OperationID()
            if not currentOperationID:
                for operation in reversed(opsByID.values()):
                    if operation.isFullCompleted():
                        currentOperationID = operation.getID()
                        serverSettings.setPersonalMission3Data({PersonalMission3.LAST_FULL_COMPLETED_OP: currentOperationID})

            currOp = opsByID.get(currentOperationID)
            if currOp:
                status, nextOp = getDetailedOperationStatus(currOp, opsByID)
        return (currOp, nextOp, status)

    def __fillModel(self):
        opsByID = getBranchesSortedPmOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)
        prevOp = self.__currentOperation
        isWithoutAwardListBranchActivated = self.__pmCache.isWithoutAwardListBranchActivated()
        unpackedOp = self.__findAndUnpackFirstInProgressOperation(opsByID)
        currOp, nextOp, status = self.__findAndUnpackNextOpIfNoCurrent(isWithoutAwardListBranchActivated, opsByID, unpackedOp)
        with self.getViewModel().transaction() as tx:
            if currOp:
                tx.setCurrentOperationName(currOp.getUserName())
                tx.setCurrentOperationId(currOp.getID())
                tx.setTotalProgress(currOp.getQuestsCount())
                tx.setVehicleName(currOp.getPMAwardListVehicleBonus().descriptor.type.userString)
            linkedOp = currOp
            if not isWithoutAwardListBranchActivated:
                tx.setState(State.CAMPAIGN_NOT_ACTIVATED)
                branchID = currOp.getBranch() if currOp else PM_BRANCH.PERSONAL_MISSION_3
                campaign = self.__pmCache.getCampaignsForBranch(branchID).get(PM_BRANCH.PM_CAMPAIGNS_IDS[branchID])
                tx.setCampaignName(campaign.getUserName())
            elif currOp and not currOp.isFullCompleted() and all((op.isCompleted() for op in opsByID.values())):
                tx.setState(State.IN_PROGRESS_FOR_HONORS)
                tx.setPreviousProgress(len(prevOp.getCompletedQuests()) if prevOp else 0)
                tx.setCurrentProgress(len(currOp.getCompletedQuests()) if currOp else 0)
            elif status in _OP_NOT_COMPLETE or status == OperationStatus.PAUSED and currOp:
                tx.setState(State.COMPLETED_WITH_HONORS)
                tx.setAllOperationsCompleted(status == OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR)
                linkedOp = nextOp
            elif status == _NEXT_OP_AVAILABLE or currOp and currOp.isCompleted() and not currOp.isFullCompleted():
                tx.setState(State.COMPLETED)
                currOpID = currOp.getID()
                for op in opsByID.values():
                    if op.getID() != currOpID and not op.isCompleted():
                        linkedOp = nextOp = op
                        break

            elif status == OperationStatus.ACTIVE:
                tx.setState(State.IN_PROGRESS)
                self.__fillDetailProgress(tx, currOp)
            if nextOp:
                tx.setNextOperationName(nextOp.getUserName())
                tx.setNextOperationId(nextOp.getID())
        self.__currentOperation = currOp
        self.__linkedOperation = linkedOp

    def __fillDetailProgress(self, model, operation):
        branchID = operation.getBranch()
        checkedPMPointsKey = getCheckedPMPointsKey(branchID)
        vehDetails = getVehicleDetails(operation)
        lastInstallDetailID = getCurrentOperationLastInstalledDetail(operation)
        totalPoints, _ = self.__pmCache.getOperationPmPointsData(branchID, operation.getID())
        minMilestonePoints = MIN_PM_POINTS if lastInstallDetailID == 0 else vehDetails[lastInstallDetailID - 1][1]
        maxMilestonePoints = vehDetails[lastInstallDetailID][1]
        maxDetailPoints = maxMilestonePoints - minMilestonePoints
        nextDetailID = lastInstallDetailID + 1
        detailID = getDetailNameByToken(vehDetails[lastInstallDetailID][0])
        model.setStageNumber(nextDetailID)
        model.setDetailId(detailID)
        previousPMPointsProgress = getPersonalMissionData(branchID).get(checkedPMPointsKey, 0)
        model.setPreviousProgress(previousPMPointsProgress - minMilestonePoints)
        currentDetailPoints = totalPoints - minMilestonePoints if totalPoints < maxMilestonePoints else maxDetailPoints
        model.setCurrentProgress(currentDetailPoints)
        model.setTotalProgress(maxDetailPoints)
        if checkedPMPointsKey:
            setPersonalMissionData(branchID, {checkedPMPointsKey: totalPoints})
