# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/rewards_view.py
from __future__ import absolute_import
from itertools import chain
from typing import TYPE_CHECKING
import SoundGroups
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.rewards_view_model import RewardsViewModel, RewardsViewType
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.personal_missions_30.bonus_packers import packMissionsBonusModelAndTooltipData, getBonusPacker
from gui.impl.lobby.personal_missions_30.state import PersonalMissions3EntryState
from gui.impl.lobby.personal_missions_30.views_helpers import getDetailNameByToken, showRewardVehicleInHangar, setForceLeavePM3State, setVideoOverlayOn, setVideoOverlayOff, canOpenOperationPage
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses
from gui.server_events.finders import NO_AWARD_LIST_FINISHED_QUEST, NO_AWARD_LIST_VEHICLE_DETAIL_TOKEN
from gui.shared.event_dispatcher import showPersonalMissionMainWindow
from helpers import dependency
from personal_missions import PM_BRANCH, PM_SWITCHES
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Callable, Dict, Optional

class RewardsView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx):
        settings = ViewSettings(layoutID=R.views.mono.personal_missions_30.rewards(), model=RewardsViewModel())
        self.ctx = ctx
        self.questID = self.ctx['questID']
        self.rewardType = self.ctx['type']
        self.rewards = self.ctx['rewards']
        self.closingCallback = self.ctx.get('closingCallback')
        self.nextOperationID = None
        self.currentOperation = None
        self.__tooltipData = {}
        self.__doStateChange = True
        super(RewardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltipData.get(event.getArgument('tooltipId'))

    def _getEvents(self):
        return ((self.viewModel.close, self.__onClose),
         (self.viewModel.goToOperation, self.__onShowOperation),
         (self.viewModel.goToVehicle, self.__onShowVehicle),
         (self.viewModel.disableVideoOverlaySound, self.__onDisableVideoOverlaySound),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _onLoading(self, *args, **kwargs):
        super(RewardsView, self)._onLoading(*args, **kwargs)
        self.currentOperation = self.__defineCurrentOperation()
        if self.rewardType == RewardsViewType.OPERATION:
            setVideoOverlayOn()
        operationID = self.currentOperation.getID()
        branchID = self.currentOperation.getBranch()
        isCompleted = self.currentOperation.isCompleted()
        lsm = getLobbyStateMachine()
        with self.viewModel.transaction() as tx:
            tx.setType(self.rewardType)
            tx.setOperationId(operationID)
            tx.setButtonDisabled(not canOpenOperationPage(operationID))
            tx.setButtonVisible(not lsm.getStateByCls(PersonalMissions3EntryState).isEntered())
            tx.setOperationName(self.__getOperationName(operationID))
            tx.setCampaignName(self.__getCampaignName(branchID))
            if self.rewardType == RewardsViewType.VEHICLE_PART:
                vehDetail = self.__getVehDetail(branchID, operationID)
                if vehDetail:
                    tx.setVehicleDetailName(vehDetail)
            self.__fillRewards(tx.getRewards(), getBonusPacker(isRewardScreen=True, isOperationCompleted=isCompleted))
            if self.rewardType == RewardsViewType.OPERATION_WITH_HONORS:
                self.nextOperationID = self.__defineNextOperationID(branchID)
                if self.nextOperationID:
                    tx.setNextOperationName(self.__getOperationName(self.nextOperationID))
            if self.rewardType == RewardsViewType.OPERATION:
                fillVehicleInfo(tx.vehicle, self.currentOperation.getPMAwardListVehicleBonus())

    def _finalize(self):
        self.__onViewClosed()
        SoundGroups.g_instance.playSound2D('vid_pm_stop')
        super(RewardsView, self)._finalize()

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        campaignSwitcher = PM_SWITCHES.MAP_BRANCH_NAME_TO_SWITCH_NAME.get(self.currentOperation.getBranchName())
        operationID = self.currentOperation.getID()
        if not diff.get(campaignSwitcher, True) or operationID in diff.get(PM_SWITCHES.DISABLED_PM_OPERATIONS, {}):
            self.__onClose()

    def __onClose(self):
        self.__onViewClosed()
        self.destroyWindow()

    def __onViewClosed(self):
        if self.closingCallback is not None:
            self.closingCallback(self.__doStateChange)
            self.closingCallback = None
        self.__doStateChange = True
        return

    def __onShowOperation(self):
        self.destroyWindow()
        operationID = self.currentOperation.getID() if self.rewardType == RewardsViewType.VEHICLE_PART else self.nextOperationID
        if operationID:
            showPersonalMissionMainWindow(operationID)

    def __onDisableVideoOverlaySound(self):
        setVideoOverlayOff()

    def __onShowVehicle(self):
        self.__doStateChange = False
        setForceLeavePM3State()
        self.destroyWindow()
        showRewardVehicleInHangar(self.currentOperation)

    def __getVehDetail(self, branchID, operationID):
        detailName = None
        detailToken = findFirst(lambda reward: reward.startswith(NO_AWARD_LIST_VEHICLE_DETAIL_TOKEN % (PM_BRANCH.PM_CAMPAIGNS_IDS[branchID], operationID)), self.rewards[self.questID].get('tokens', []))
        if detailToken:
            detailName = getDetailNameByToken(detailToken)
        return detailName

    def __isCampaignFinished(self):
        return all((operation.isFullCompleted() for operation in self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_2]).values()))

    def __defineCurrentOperation(self):
        currentOperationByType = {RewardsViewType.VEHICLE_PART: lambda q: int(q.split('_')[2]),
         RewardsViewType.OPERATION_WITH_HONORS: lambda q: int(q.split('_')[3].rsplit('t')[-1]),
         RewardsViewType.CAMPAIGN_WITH_HONORS: lambda q: int(q.split('_')[3].rsplit('t')[-1]),
         RewardsViewType.OPERATION: lambda q: int(q.split('_')[2])}
        operationID = currentOperationByType[self.rewardType](self.questID)
        return self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES).get(operationID)

    def __defineNextOperationID(self, branchID):
        allOperations = list(sorted(self.__eventsCache.getPersonalMissions().getAllOperations((PM_BRANCH.TYPE_TO_NAME[branchID],)).values(), key=lambda o: o.getID()))
        notFullCompletedOperations = [ operation for operation in allOperations if not operation.isFullCompleted() ]
        return notFullCompletedOperations[0].getID() if notFullCompletedOperations else None

    def __getOperationName(self, operationID):
        return self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES).get(operationID).getShortUserName()

    def __getCampaignName(self, branchID):
        return self.__eventsCache.getPersonalMissions().getCampaignsForBranch(branchID).get(PM_BRANCH.PM_CAMPAIGNS_IDS[branchID]).getUserName()

    def __getBonuses(self, rewards):
        if self.rewardType == RewardsViewType.OPERATION:
            return rewards
        bonuses = []
        for key, value in rewards.items():
            bonus = getNonQuestBonuses(key, value)
            if bonus:
                bonuses.extend(bonus)

        return bonuses

    def __fillRewards(self, rewardsModel, packer):
        if self.rewardType == RewardsViewType.CAMPAIGN_WITH_HONORS:
            bonuses = self.__getBonuses(self.rewards.get(self.questID, {}))
            bonuses.extend(chain(*(self.__getBonuses(self.rewards.get(NO_AWARD_LIST_FINISHED_QUEST % PM_BRANCH.PM_CAMPAIGNS_IDS[PM_BRANCH.NAME_TO_TYPE[branchName]], {})) for branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)))
        else:
            bonuses = self.__getBonuses(self.rewards[self.questID])
        rewardsModel.clear()
        packMissionsBonusModelAndTooltipData(bonuses, packer, rewardsModel, self.__tooltipData)
        rewardsModel.invalidate()


class RewardsViewWindow(LobbyNotificationWindow):

    def __init__(self, ctx, parent=None):
        super(RewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RewardsView(ctx=ctx), parent=parent)
