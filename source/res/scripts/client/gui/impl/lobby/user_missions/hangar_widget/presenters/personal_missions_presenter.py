# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/presenters/personal_missions_presenter.py
from __future__ import absolute_import
from functools import partial
from future.utils import itervalues, viewvalues
from typing import TYPE_CHECKING
from constants import ROLE_TYPE_TO_COMMON_ROLE
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.personal_missions_list_model import PersonalMissionsListModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.personal_mission_model import PersonalMissionModel
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.presenters.constants import UserMissionGroups
from gui.impl.lobby.user_missions.hangar_widget.presenters.base_child_presenter import UserMissionChildPresenter
from gui.impl.lobby.user_missions.hangar_widget.services import IPersonalMissionsService
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.lobby.personal_missions_30.tooltips.umg_tooltip import UmgPersonalMissionsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.PERSONAL_MISSIONS_30 import PERSONAL_MISSIONS_30
from gui.server_events.events_dispatcher import showPersonalMission, showPersonalMissionOperationsPage
from gui.shared.event_dispatcher import showPersonalMissionCampaignSelectorWindow, showPersonalMissionMainWindow
from helpers import dependency
from helpers.i18n import makeString
import nations
from personal_missions import PM_BRANCH
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
if TYPE_CHECKING:
    from typing import Optional
    from items.vehicles import VehicleType
    from gui.server_events.event_items import PersonalMission
    from gui.shared.gui_items.Vehicle import Vehicle

class PersonalMissionsPresenter(UserMissionChildPresenter, TooltipPositionerMixin, OverlapCtrlMixin, ViewComponent[PersonalMissionsListModel]):
    GROUP = UserMissionGroups.PERSONAL_MISSIONS
    eventsCache = dependency.descriptor(IEventsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)
    lobbyContext = dependency.descriptor(ILobbyContext)
    personalMissionsService = dependency.descriptor(IPersonalMissionsService)

    def __init__(self):
        super(PersonalMissionsPresenter, self).__init__(model=PersonalMissionsListModel)
        self._onClicks = {}
        self._showTierMismatch = None
        self._showNoMissions = None
        self._showUnavailable = None
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return UmgPersonalMissionsTooltip(int(event.getArgument('campaignId')), int(event.getArgument('missionId'))) if contentID == R.views.mono.personal_missions_30.tooltips.umg_tooltip() else super(PersonalMissionsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _getEvents(self):
        return super(PersonalMissionsPresenter, self)._getEvents() + ((self.viewModel.onClick, self._onClick),
         (self.viewModel.onMarkAsViewed, self._onMarkAsViewed),
         (self.hangarSpace.onVehicleChanged, self._update),
         (self.hangarSpace.onSpaceCreate, self._update),
         (self.personalMissionsService.onServicePMSyncCompleted, self._update),
         (self.personalMissionsService.onWidgetQuestIDMarkedAsNew, self._update),
         (self.personalMissionsService.onPersonalMissionsChanged, self._updateVisibility))

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(PersonalMissionsPresenter, self)._onLoading(*args, **kwargs)
        self.queueUpdate()

    def _onEventsUpdated(self):
        self.queueUpdate()

    def _onClick(self, args):
        function = self._onClicks.get(args['campaignId'])
        if function:
            function()

    def _onMarkAsViewed(self, _):
        self.personalMissionsService.clearWidgetQuestIDMarkedAsNew()

    def _rawUpdate(self):
        super(PersonalMissionsPresenter, self)._rawUpdate()
        with self.viewModel.transaction() as vm:
            vm.setReadyForAnimations(self.hangarSpace.spaceInited)
            self._updateMissions(vm)

    def _updateMissions(self, vm):
        missionsListVM = vm.getMissions()
        missionsListVM.clear()
        self._onClicks.clear()
        self._showTierMismatch = None
        self._showNoMissions = None
        campaigns = self.eventsCache.getPersonalMissions().getActiveCampaigns()
        for campaign in campaigns:
            missionVM = self._getCard(campaign)
            if missionVM:
                missionsListVM.addViewModel(missionVM)

        if not missionsListVM:
            if self._showTierMismatch is not None:
                missionsListVM.addViewModel(self._getCardTierMismatch())
            elif self._showNoMissions is not None:
                missionsListVM.addViewModel(self._getCardNoMissions())
            elif self._showUnavailable is not None:
                missionsListVM.addViewModel(self._getCardUnavailable())
        missionsListVM.invalidate()
        return

    def _getCardTierMismatch(self):
        missionVM = PersonalMissionModel()
        missionVM.setCampaignId(self._showTierMismatch)
        missionVM.setMissionState(PersonalMissionModel.STATE_WARNING)
        missionVM.setWarningMessage(backport.text(R.strings.user_missions.pm.tier()))
        missionVM.setIcon(self._icons().warning.c_36x36.circleBw())
        missionVM.setWarningTooltipHeader(backport.text(R.strings.user_missions.pm.warning.tooltip.header.tier()))
        missionVM.setWarningTooltipBody(backport.text(R.strings.user_missions.pm.warning.tooltip.body.tier()))
        self._addWarningClick(self._showTierMismatch)
        return missionVM

    def _getCardNoMissions(self):
        missionVM = PersonalMissionModel()
        missionVM.setCampaignId(self._showNoMissions)
        missionVM.setMissionState(PersonalMissionModel.STATE_WARNING)
        missionVM.setWarningMessage(backport.text(R.strings.user_missions.pm.no_missions()))
        missionVM.setIcon(self._icons().warning.c_36x36.circleBw())
        missionVM.setWarningTooltipHeader(backport.text(R.strings.user_missions.pm.warning.tooltip.header.no_missions_available()))
        missionVM.setWarningTooltipBody(backport.text(R.strings.user_missions.pm.warning.tooltip.body.no_missions_available()))
        self._addWarningClick(self._showNoMissions)
        return missionVM

    def _addWarningClick(self, branchID):
        branchName = PM_BRANCH.TYPE_TO_NAME[branchID]
        if branchName in PM_BRANCH.WITH_AWARD_LIST_BRANCHES:
            self._onClicks[branchID] = showPersonalMissionCampaignSelectorWindow
        elif branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
            pmc = self.eventsCache.getPersonalMissions()
            activeOperations = pmc.getActiveOperations(branches=(branchName,))
            if activeOperations:
                operationID = activeOperations[0].getID()
            else:
                operations = pmc.getOperationsForBranch(branchID)
                operationIDs = PM_BRANCH.BRANCH_TO_OPERATION_IDS[branchID]
                operationID = operationIDs[0]
                for opID in operationIDs:
                    if not operations[opID].isCompleted():
                        operationID = opID
                        break

            self._onClicks[branchID] = partial(showPersonalMissionMainWindow, operationID=operationID)

    def _getCardUnavailable(self):
        missionVM = PersonalMissionModel()
        missionVM.setMissionState(PersonalMissionModel.STATE_WARNING)
        missionVM.setWarningMessage(backport.text(R.strings.user_missions.pm.unavailable()))
        missionVM.setIcon(self._icons().warning.c_36x36.alert())
        missionVM.setWarningTooltipHeader(backport.text(R.strings.user_missions.pm.warning.tooltip.header.temporarily_unavailable()))
        missionVM.setWarningTooltipBody(backport.text(R.strings.user_missions.pm.warning.tooltip.body.temporarily_unavailable()))
        return missionVM

    def _getCard(self, campaignName):
        branchID = PM_BRANCH.NAME_TO_TYPE[campaignName]
        campaignId = PM_BRANCH.PM_CAMPAIGNS_IDS[branchID]
        personalMissionsCache = self.eventsCache.getPersonalMissions()
        campaign = personalMissionsCache.getCampaignsForBranch(branchID)[campaignId]
        if not campaign.isStarted():
            return
        elif not self.lobbyContext.getServerSettings().isPersonalMissionsEnabled(branch=branchID):
            self._showUnavailable = branchID
            return
        else:
            quests = personalMissionsCache.getSelectedQuestsForBranch(branchID)
            if not quests:
                if campaign.isFullCompleted():
                    return
                self._showNoMissions = branchID
                return
            randomQuest = next(itervalues(quests))
            operationId = randomQuest.getOperationID()
            disabledOps = self.lobbyContext.getServerSettings().getDisabledPMOperations()
            if operationId in disabledOps:
                self._showUnavailable = branchID
                return
            elif not self._hasProperVehicleTier(operationId):
                self._showTierMismatch = branchID
                return
            vehicle = g_currentVehicle.item
            if self._isUnsuitableForPM(vehicle):
                self._showNoMissions = branchID
                return
            vehType = vehicle.descriptor.type
            quest = None
            for q in viewvalues(quests):
                if q.getQuestClassifier().matchVehicle(vehType):
                    quest = q
                    break

            missionVM = PersonalMissionModel()
            missionVM.setCampaignId(branchID)
            missionVM.setVehicleIcon(self._icons().vehicles.num(operationId)())
            if quest is not None:
                if quest.isDisabled():
                    self._showUnavailable = branchID
                    return
                self._fillCardInProgress(missionVM, quest, vehType)
            else:
                self._fillCardCompleted(missionVM, branchID, operationId, vehType)
            return missionVM

    def _fillCardInProgress(self, missionVM, quest, vehType):
        questID = int(quest.getID())
        markedAsNewQuestID = self.personalMissionsService.getWidgetQuestIDMarkedAsNew()
        if markedAsNewQuestID and questID in markedAsNewQuestID:
            missionVM.setAnimationType(PersonalMissionModel.ANIMATION_NEW_MISSION)
        missionVM.setMissionId(questID)
        missionVM.setMissionState(self._pickMissionState(quest, vehType))
        missionVM.setTitle(quest.getShortUserName())
        classifier = self._getClassifier(quest.getQuestBranch(), vehType)
        missionVM.setIcon(self._icons().classifiers.c_36x36.dyn(classifier.replace('-', '_'))())
        branchID = quest.getQuestBranch()
        branchName = quest.getQuestBranchName()
        if branchName in PM_BRANCH.WITH_AWARD_LIST_BRANCHES:
            self._onClicks[branchID] = partial(showPersonalMission, missionID=questID)
        elif branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
            self._onClicks[branchID] = partial(showPersonalMissionMainWindow, operationID=quest.getOperationID())

    def _fillCardCompleted(self, missionVM, branchID, operationId, vehType):
        classifier = self._getClassifier(branchID, vehType)
        missionVM.setIcon(self._icons().classifiers.c_36x36.dyn(classifier.replace('-', '_'))())
        if branchID == PM_BRANCH.REGULAR:
            title = makeString(PERSONAL_MISSIONS.chainNameByVehicleType(vehType.classTag))
        elif branchID == PM_BRANCH.PERSONAL_MISSION_2:
            allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[vehType.id[0]]
            title = makeString(PERSONAL_MISSIONS.getAllianceName(allianceId))
        else:
            title = makeString(PERSONAL_MISSIONS_30.chainNameByRole(classifier))
        missionVM.setTitle(title)
        missionVM.setMissionState(PersonalMissionModel.STATE_COMPLETE)
        chainId = None
        if PM_BRANCH.TYPE_TO_NAME[branchID] in PM_BRANCH.WITH_AWARD_LIST_BRANCHES:
            operation = self.eventsCache.getPersonalMissions().getOperationsForBranch(branchID)[operationId]
            chainId = operation.getChainByClassifierAttr(classifier)[0]
        self._onClicks[branchID] = partial(showPersonalMissionOperationsPage, branchID, operationId, chainID=chainId)
        return

    def _updateVisibility(self):
        self._notifyVisibilityChanged()

    def isVisible(self):
        return self.personalMissionsService.isVisible()

    @staticmethod
    def _icons():
        return R.images.gui.maps.icons.userMissions.personal_missions.widget_card

    @classmethod
    def _getClassifier(cls, branchID, vehType):
        if branchID == PM_BRANCH.REGULAR:
            return vehType.classTag
        if branchID == PM_BRANCH.PERSONAL_MISSION_2:
            allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[vehType.id[0]]
            return nations.ALLIANCES_TAGS_ORDER[allianceId]
        return ROLE_TYPE_TO_COMMON_ROLE[vehType.role]

    def _update(self, *_):
        self.queueUpdate()

    @classmethod
    def _isUnsuitableForPM(cls, vehicle):
        return vehicle.getCustomState() == vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE or vehicle.rentalIsOver

    @classmethod
    def _hasProperVehicleTier(cls, operationID):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return False
        else:
            vehType = vehicle.descriptor.type
            minLevel, maxLevel = cls.eventsCache.getPersonalMissions().getVehicleLevelRestrictions(operationID)
            return minLevel <= vehType.level <= maxLevel

    @classmethod
    def _pickMissionState(cls, quest, vehType):
        branchName = quest.getQuestBranchName()
        if branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
            if quest.isAmongUsedQuestVehicle(vehType.compactDescr):
                return PersonalMissionModel.STATE_WRONG_VEHICLE
            return PersonalMissionModel.STATE_ACTIVE
        return PersonalMissionModel.STATE_IMPROVE if quest.isMainCompleted() else PersonalMissionModel.STATE_ACTIVE
