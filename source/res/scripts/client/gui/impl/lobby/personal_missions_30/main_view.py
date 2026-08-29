# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/main_view.py
from __future__ import absolute_import
import SoundGroups
import typing
from functools import partial
from future.utils import listvalues
from account_helpers.settings_core.settings_constants import PersonalMission3, PersonalMission4
from constants import DAILY_QUESTS_CONFIG, Configs
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.additional_mission_model import AdditionalMissionModel, AdditionalMissionType
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory, OperationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.detail_model import DetailModel, DetailStatus
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_model import AnimationState, MainScreenState, MainViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_reward_model import MainViewRewardModel, RewardsType
from gui.impl.gen.view_models.views.lobby.personal_missions_30.mission_model import MissionModel, MissionStatus
from gui.impl.gen.view_models.views.lobby.personal_missions_30.missions_model import MissionsModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_model import OperationModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatus
from gui.impl.gen.view_models.views.lobby.personal_missions_30.quest_model import QuestModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.personal_missions_30.bonus_packers import getBonusPacker, packMissionsBonusModelAndTooltipData
from gui.impl.lobby.personal_missions_30.hangar_helpers import AssemblingManager
from gui.impl.lobby.personal_missions_30.personal_mission_constants import MAX_DETAIL_ID, MISSIONS_ROLES_TO_CATEGORIES, PERSONAL_MISSIONS_CAMPAIGN_3_SPACE, REWARDS_VIEW_TYPES, IntroKeys, SoundsKeys
from gui.impl.lobby.personal_missions_30.state import AssemblingState, MissionsState, ProgressionState
from gui.impl.lobby.personal_missions_30.tooltips.mission_progress_tooltip import MissionProgressTooltip
from gui.impl.lobby.personal_missions_30.tooltips.missions_category_tooltip import MissionsCategoryTooltip
from gui.impl.lobby.personal_missions_30.views_helpers import getDetailedOperationStatus, getDetailNameByToken, getMainRewardInfo, getMissionConfigData, getOperationStatus, getQuestsByOperationsChains, getRegularQuestsPMPoints, getBranchSortedPmOperations, getStageNumberByDetailId, getVehicleDetails, hasAssemblingVideo, isIntroShown, isVehDetailInstalled, showRewardVehicleInHangar, showStageAssemblingVideo, getOperationBannerState, setPMInstalledVehDetails, getPMInstalledVehDetails, getPersonalMissionData, getCheckedPMPointsKey, setPersonalMissionData, getCurrentOperationLastInstalledDetail, getBranchesSortedPmOperations, checkPM4FirstEntrance
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.events_dispatcher import showMissions
from gui.server_events.events_helpers import isDailyQuestsEnable, isWeeklyQuestsEnable
from gui.server_events.finders import PM_OPERATION_POINTS_TOKEN
from gui.shared.event_dispatcher import showHangar, showPMAdvancedRewardsWindow, showVehicleHubOverview, showWithoutAwardListOperationIntroWindow, showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import quests as quests_proc
from gui.shared.gui_items.processors.quests import PMActivateSeason, PMGetQuestRewards
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from personal_missions import PM_BRANCH, PM_SWITCHES
from personal_missions import g_cache as pm_cache
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IAchievements20EarningController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Tuple, Set
    from gui.server_events.event_items import PMOperation, PersonalMission
    from gui.shared.missions.packers.bonus import BonusUIPacker

class MainView(ViewImpl):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_CAMPAIGN_3_SPACE
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __customization = dependency.descriptor(ICustomizationService)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __achievementsController = dependency.descriptor(IAchievements20EarningController)

    def __init__(self, layoutID, operationID, state, assemblingManager):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = MainViewModel()
        super(MainView, self).__init__(settings)
        self.__blur = CachedBlur()
        self.__initState = MainScreenState.PROGRESSION if state is None else (MainScreenState(state) if isinstance(state, str) else state)
        self.__assemblingManager = assemblingManager
        self.__tooltipData = {}
        self.__quests = {}
        self.__needQuestsUpdate = True
        branchID = PM_BRANCH.OPERATION_ID_TO_BRANCH[operationID]
        self.__campaign = self.__eventsCache.getPersonalMissions().getCampaignsForBranch(branchID).get(PM_BRANCH.PM_CAMPAIGNS_IDS[branchID])
        self.__campaignOperations = getBranchSortedPmOperations(branchID)
        self.__operation = self.__campaignOperations.get(operationID)
        self.__operationsToUpdate = {operationID:False for operationID in self.__campaignOperations}
        self.__lastInstalledDetail = getPMInstalledVehDetails(self.getBranchID())
        self.__operationStatus = getOperationStatus(self.__operation, self.__campaignOperations)
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MainView, self).createToolTip(event)

    def getTooltipData(self, event):
        return self.__tooltipData.get(event.getArgument('tooltipId'))

    def getOperationID(self):
        return self.__operation.getID()

    def getBranchID(self):
        return self.__operation.getBranch()

    def getBranchName(self):
        return self.__operation.getBranchName()

    def isCurrentOperationFullCompleted(self):
        return self.__operation.isFullCompleted()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.personal_missions_30.tooltips.mission_progress_tooltip():
            if self.viewModel.getMainScreenState() == MainScreenState.PROGRESSION:
                missions = self.__eventsCache.getPersonalMissions().getActualQuests(self.getBranchID(), self.__operation.getID())
            else:
                category = self.viewModel.missionsModel.getMissionsCategory()
                missions = self.__quests.get(self.__operation.getID(), {}).get(category.value, {}).values()
            missionIndex = int(event.getArgument('missionIndex'))
            if 0 <= missionIndex < len(missions):
                mission = missions[missionIndex]
                return MissionProgressTooltip(mission=mission, isCompleted=mission.isCompleted())
        elif contentID == R.views.mono.personal_missions_30.tooltips.missions_category_tooltip():
            return MissionsCategoryTooltip(category=MissionCategory(event.getArgument('category')), operation=self.__operation)
        return super(MainView, self).createToolTipContent(event, contentID)

    def setProgressionState(self):
        if self.__operationsToUpdate[self.__operation.getID()]:
            self.__updateViewModel(operationToUpdate=self.__operation)
        if self.viewModel.getMainScreenState() == MainScreenState.MISSIONS:
            self.__blur.disable()
        self.viewModel.setMainScreenState(MainScreenState.PROGRESSION)

    def setMissionsState(self):
        self.viewModel.setMainScreenState(MainScreenState.MISSIONS)
        self.__blur.enable()
        if self.__needQuestsUpdate:
            self.__updateAllMissions()
            self.__needQuestsUpdate = False

    def setAssemblingState(self):
        self.viewModel.setMainScreenState(MainScreenState.ASSEMBLING)

    def setAnimationState(self, state):
        self.viewModel.setAnimationState(state)

    def setCameraFlightInProgress(self, isInProgress):
        self.viewModel.setCameraFlightInProgress(isInProgress)

    def getMainScreenState(self):
        return self.viewModel.getMainScreenState()

    def _onFocus(self, focused):
        super(MainView, self)._onFocus(focused)
        self.__assemblingManager.onFocus(focused)

    def _getEvents(self):
        cameraEvents = self.__assemblingManager.getCameraEvents(self.viewModel)
        hangarManager = self.__assemblingManager.getHangarOperationsManager()
        hangarManagerEvents = [(hangarManager.onVehicleClick, self.__onGoToAssembling)] if hangarManager is not None else []
        viewEvents = [(self.viewModel.onBack, self.__onBack),
         (self.viewModel.onSwitchOperation, self.__onSelectOperation),
         (self.viewModel.showOperationVehicleVideo, self.__showOperationVehicleVideo),
         (self.viewModel.showDetailVideo, self.__showDetailVideo),
         (self.viewModel.onOperationStatusButtonClick, self.__onOperationStatusButtonClick),
         (self.viewModel.onDetailInfo, self.__onDetailInfo),
         (self.viewModel.onClaimDetail, self.__onClaimDetail),
         (self.viewModel.onMission, self.__onMissionShow),
         (self.viewModel.onAdditionalMission, self.__onAdditionalMissionShow),
         (self.viewModel.onVehiclePreview, self.__onVehiclePreview),
         (self.viewModel.setFreeCamera, self.__setFreeCamera),
         (self.viewModel.updateAnimationState, self.__updateAnimationState),
         (self.viewModel.showVehicleInHangar, self.__showVehicleInHangar),
         (self.viewModel.showStylePreview, self.__showStylePreview),
         (self.viewModel.missionsModel.changeCategory, self.__changeMissionsCategory),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged),
         (self.__eventsCache.onPMSyncCompleted, self.__onPmEventsSync),
         (self.__eventsCache.onSyncCompleted, self.__onCommonSync),
         (self.__itemsCache.onPMSyncCompleted, self.__onPmItemsSync),
         (self.__itemsCache.onSyncCompleted, self.__onItemsSyncCompleted)]
        return viewEvents + cameraEvents + hangarManagerEvents

    def _onLoading(self, *args, **kwargs):
        super(MainView, self)._onLoading(*args, **kwargs)
        self.viewModel.setMainScreenState(self.__initState)
        self.__updateViewModel()
        checkPM4FirstEntrance(self.__operation)

    def _onShown(self):
        super(MainView, self)._onShown()
        self.__setCheckedPMPointsData()

    def _finalize(self):
        self.__tooltipData = {}
        super(MainView, self)._finalize()
        self.__blur.fini()

    def __onCommonSync(self, *_):
        self.__fillRewardTankModel(self.viewModel)
        with self.viewModel.transaction() as tx:
            for operationModel in tx.getOperations():
                operation = self.__campaignOperations.get(operationModel.getOperationId())
                self.__fillAdditionalMissionsModel(operationModel, operation)
                self.__fillDetails(operationModel, operation)

    def __onPmEventsSync(self, diff=None):
        self.__setAllOperationsUpdateStatus(needUpdate=True)
        if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
            self.__updateViewModel(operationToUpdate=self.__operation)
            self.__needQuestsUpdate = True
        campaignID = self.__campaign.getID()
        campaignKey = 'pm{}'.format(campaignID)
        campaignProgressKey = '{}_progress'.format(campaignKey)
        diff = diff or {}
        pmQuests = diff.get('potapovQuests', {}).get(campaignKey, {}).get(('selected', '_r'), set())
        if diff.get(campaignProgressKey, {}):
            for questName in diff.get(campaignProgressKey, {}):
                questID = pm_cache.getPersonalMissionIDByName(questName)
                pmQuests.add(questID)

        if pmQuests:
            self.__updateMissions(pmQuests)
        tokens = diff.get('tokens', {})
        if tokens:
            for operation in self.__campaignOperations.values():
                if operation.isInProgress():
                    operationPmPointsToken = PM_OPERATION_POINTS_TOKEN % (campaignID, operation.getID())
                    if tokens.get(operationPmPointsToken) is not None:
                        self.__setCheckedPMPointsData()
                        break

        return

    def __onItemsSyncCompleted(self, _, diff):
        if diff is not None and not diff:
            return
        else:
            self.__updateViewModel(operationToUpdate=self.__operation)
            return

    def __onPmItemsSync(self, *_):
        self.__setAllOperationsUpdateStatus(needUpdate=True)
        if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
            self.__updateViewModel(operationToUpdate=self.__operation)

    def __onSelectOperation(self, data):
        operationID = int(data.get(self.viewModel.OPERATION_ID, self.__operation.getID()))
        isAnotherCampaign = operationID not in PM_BRANCH.BRANCH_TO_OPERATION_IDS[self.getBranchID()]
        if isAnotherCampaign:
            branchID = PM_BRANCH.OPERATION_ID_TO_BRANCH[operationID]
            self.__campaign = self.__eventsCache.getPersonalMissions().getCampaignsForBranch(branchID).get(PM_BRANCH.PM_CAMPAIGNS_IDS[branchID])
            self.__campaignOperations = getBranchSortedPmOperations(branchID)
            self.__operation = self.__campaignOperations.get(operationID)
            self.__operationStatus = getOperationStatus(self.__operation, self.__campaignOperations)
            self.__lastInstalledDetail = getPMInstalledVehDetails(self.getBranchID())
            self.__operationsToUpdate = {operationID:False for operationID in self.__campaignOperations}
            self.__needQuestsUpdate = True
            checkPM4FirstEntrance(self.__operation)
            self.__updateViewModel()
        else:
            self.__operation = self.__campaignOperations.get(operationID)
            self.__operationStatus = getOperationStatus(self.__operation, self.__campaignOperations)
        if self.__operationStatus != OperationState.UNAVAILABLE and not isIntroShown(IntroKeys.OPERATION_INTRO_VIEW.value % operationID, self.getBranchID()):
            showWithoutAwardListOperationIntroWindow(operationID)
        if self.__operationsToUpdate.get(self.__operation.getID()):
            self.__updateViewModel(operationToUpdate=self.__operation)
        else:
            with self.viewModel.transaction() as tx:
                operationModel = self.__getOperationFromModel(self.__operation.getID())
                tx.setActiveOperationId(self.__operation.getID())
                self.__fillOperationPoints(operationModel, self.__operation)
                self.__fillRewardTankModel(tx)
                self.__fillOperationStatusModel(tx)
        self.__setCheckedPMPointsData()
        self.__assemblingManager.changeVehicleGO(self.__operation.getID(), getCurrentOperationLastInstalledDetail(self.__operation))
        self.__assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=self.isCurrentOperationFullCompleted())
        ProgressionState.goTo(operationID=self.__operation.getID())

    def __onOperationStatusButtonClick(self):
        if self.viewModel.status.getStatus().value in (OperationStatus.COMPLETED.value, OperationStatus.PAUSED.value, OperationStatus.AVAILABLE.value):
            if self.getBranchName() not in self.__eventsCache.getPersonalMissions().getActiveCampaigns():
                self.__switchCampaign()
            self.__processOperation(self.__operation.getBranch(), self.__operation.getID())
            if not self.__operation.isStarted():
                setPMInstalledVehDetails(self.__operation.getBranch())

    @args2params(str)
    def __onDetailInfo(self, detailId):
        if not getLobbyStateMachine().isStateEntered(AssemblingState.STATE_ID):
            AssemblingState.goTo(operationID=self.__operation.getID(), state=self.viewModel.getMainScreenState().value)
        self.__assemblingManager.switchCameraToStagePosition(getStageNumberByDetailId(detailId), callback=partial(self.viewModel.setAnimationState, AnimationState.CONTINUE_DETAIL_INFO))

    def __onGoToAssembling(self):
        AssemblingState.goTo(operationID=self.__operation.getID(), state=self.viewModel.getMainScreenState().value)
        self.viewModel.setAnimationState(AnimationState.ASSEMBLING)
        SoundGroups.g_instance.playSound2D(SoundsKeys.VEHICLE_CLICK)

    def __setFreeCamera(self):
        self.__assemblingManager.switchCameraToFreePosition(callback=partial(self.viewModel.setAnimationState, AnimationState.IDLE))

    @args2params(str)
    def __onClaimDetail(self, detailId):
        detailName = backport.text(R.strings.personal_missions_30.detail.name.dyn(detailId)())
        stageNumber = getStageNumberByDetailId(detailId)
        if stageNumber == MAX_DETAIL_ID:
            self.__claimReward(detailName)
        else:
            self.__assemblingManager.assembleStage(stageNumber)
            setPMInstalledVehDetails(self.__operation.getBranch(), stageNumber)
            self.__pushDetailMessage(detailName=detailName)
        operationModel = self.__getOperationFromModel(self.__operation.getID())
        with operationModel.transaction() as tx:
            self.__fillDetails(tx, self.__operation)

    def __pushDetailMessage(self, detailName):
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.personalMissions.detailInstalled.body(), detailName=detailName), type=SystemMessages.SM_TYPE.PmActionCompleted, priority=NotificationPriorityLevel.LOW, messageData={'title': backport.text(R.strings.system_messages.personalMissions.detailInstalled.title(), operationName=self.__operation.getUserName())})

    @args2params(MissionCategory)
    def __onMissionShow(self, category):
        MissionsState.goTo(category=category, operationID=self.__operation.getID(), state=self.viewModel.getMainScreenState().value)

    def setMissionViewCategory(self, category):
        self.viewModel.missionsModel.setMissionsCategory(MissionCategory(category))

    @staticmethod
    def __onAdditionalMissionShow():
        showMissions()

    def __onVehiclePreview(self):
        vehicleBonus = self.__operation.getPMAwardListVehicleBonus()
        if vehicleBonus is not None:
            vehicle = self.__itemsCache.items.getItemByCD(vehicleBonus.compactDescr)
            if vehicle.isPreviewAllowed():
                showVehicleHubOverview(vehicle.intCD)
        return

    def __showVehicleInHangar(self):
        self.__showRewardVehicle()

    @args2params(int)
    def __showStylePreview(self, styleId):
        style = self.__customization.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
        showStylePreview(getVehicleCDForStyle(style), style)

    @args2params(AnimationState)
    def __updateAnimationState(self, animationState):
        self.viewModel.setAnimationState(animationState)

    def __showRewardVehicle(self):
        showRewardVehicleInHangar(self.__operation)

    def __setAllOperationsUpdateStatus(self, needUpdate=False):
        self.__operationsToUpdate = {operationID:needUpdate for operationID in self.__campaignOperations}

    @args2params(MissionCategory)
    def __changeMissionsCategory(self, category):
        self.viewModel.missionsModel.setMissionsCategory(category)

    def __onBack(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __showOperationVehicleVideo(self):
        showWithoutAwardListOperationIntroWindow(self.__operation.getID(), force=True)

    @args2params(str)
    def __showDetailVideo(self, detailId):
        showStageAssemblingVideo(self.getOperationID(), getStageNumberByDetailId(detailId))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        campaignSwitcher = PM_SWITCHES.MAP_BRANCH_NAME_TO_SWITCH_NAME.get(self.getBranchName())
        switchers = PM_SWITCHES.WITHOUT_AWARD_LIST_SWITCHERS
        if any((not diff.get(switcher, True) and campaignSwitcher == switcher for switcher in switchers)) or self.__operation.getID() in diff.get(PM_SWITCHES.DISABLED_PM_OPERATIONS, {}):
            showHangar()
            return
        if DAILY_QUESTS_CONFIG in diff or Configs.WEEKLY_QUESTS_CONFIG in diff:
            operationModel = self.__getOperationFromModel(self.__operation.getID())
            with operationModel.transaction() as tx:
                self.__fillAdditionalMissionsModel(tx, self.__operation)
        elif PM_SWITCHES.DISABLED_PM_MISSIONS in diff or PM_SWITCHES.DISABLED_PM_OPERATIONS in diff:
            self.__setAllOperationsUpdateStatus(True)
            if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
                self.__updateViewModel(operationToUpdate=self.__operation)
                self.__needQuestsUpdate = True
            else:
                self.__updateAllMissions()

    def __onSettingsChanged(self, diff):
        if PersonalMission3.PART_NO in diff:
            self.__lastInstalledDetail = getPMInstalledVehDetails(self.getBranchID())

    @decorators.adisp_process('updating')
    def __processOperation(self, branch, operation, questIDS=None):
        quests = []
        if questIDS is not None:
            allQuests = self.__eventsCache.getPersonalMissions().getQuestsForBranch(self.getBranchID())
            quests = [ allQuests.get(questID, None) for questID in questIDS ]
        res = yield quests_proc.PMOperationSelect(branch, operation, quests).request()
        if res and res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
        return

    @decorators.adisp_process('updating')
    def __switchCampaign(self):
        res = yield PMActivateSeason(self.getBranchID()).request()
        if res and res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)

    @decorators.adisp_process('updating')
    def __claimReward(self, detailName):
        self.__achievementsController.pause()
        quest = self.__operation.getRewardQuest()
        res = yield PMGetQuestRewards(quest, branchName=self.getBranchName()).request()
        if res and res.success:

            def onFinalRewardWindowClosed(doStateChange=True):
                if doStateChange:
                    self.__assemblingManager.setRewardAssemblingInProgress(False)
                    self.__assemblingManager.onAssemblingVideoFinished(MAX_DETAIL_ID)
                self.__achievementsController.resume()

            self.__assemblingManager.setRewardAssemblingInProgress(True)
            showPMAdvancedRewardsWindow(ctx={'questID': quest.getID(),
             'rewards': {quest.getID(): quest.getBonuses()},
             'type': REWARDS_VIEW_TYPES['operation'],
             'closingCallback': onFinalRewardWindowClosed})
            setPMInstalledVehDetails(self.getBranchID(), MAX_DETAIL_ID)
            self.__pushDetailMessage(detailName=detailName)
            self.__setAllOperationsUpdateStatus(needUpdate=True)
            self.__updateViewModel(operationToUpdate=self.__operation)
            self.__assemblingManager.assembleStage(MAX_DETAIL_ID, isFinalStage=True)
        else:
            self.__achievementsController.resume()
            if res and res.userMsg:
                SystemMessages.pushMessage(res.userMsg, priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.ErrorSimple)

    def __getOperationFromModel(self, operationID):
        return first([ operationModel for operationModel in self.viewModel.getOperations() if operationModel.getOperationId() == operationID ], None)

    def __updateViewModel(self, operationToUpdate=None):
        self.__operationStatus = getOperationStatus(self.__operation, self.__campaignOperations)
        with self.viewModel.transaction() as tx:
            tx.setActiveOperationId(self.getOperationID())
            tx.setCampaignName(self.__campaign.getUserName())
            self.__fillRewardTankModel(tx)
            self.__fillMenuItems(tx)
            self.__fillOperationStatusModel(tx)
            self.__fillBannerModel(tx.banner)
            operationsArray = tx.getOperations()
            if operationToUpdate is not None:
                for operationModel in self.viewModel.getOperations():
                    if operationModel.getOperationId() == operationToUpdate.getID():
                        self.__fillOperationModel(operationModel, operationToUpdate)
                        self.__operationsToUpdate[operationToUpdate.getID()] = False

            else:
                operationsArray.clear()
                for operation in self.__campaignOperations.values():
                    operationEmptyModel = tx.getOperationsType()()
                    operationModel = self.__fillOperationModel(operationEmptyModel, operation)
                    operationsArray.addViewModel(operationModel)
                    self.__setAllOperationsUpdateStatus(needUpdate=False)

            operationsArray.invalidate()
        return

    def __fillOperationModel(self, operationModel, operation):
        operationModel.setOperationState(getOperationStatus(operation, self.__campaignOperations))
        operationModel.setVehicleInHangar(operation.getPMAwardListVehicleBonus().isInInventory)
        self.__fillOperationPoints(operationModel, operation)
        self.__fillMainRewards(operationModel, operation)
        self.__fillDetails(operationModel, operation)
        self.__fillAdditionalMissionsModel(operationModel, operation)
        self.__fillActualMissionsModel(operationModel, operation)
        return operationModel

    def __fillOperationPoints(self, operationModel, operation):
        pmPointsTotal, pmPointsMax = self.__eventsCache.getPersonalMissions().getOperationPmPointsData(self.getBranchID(), operation.getID())
        operationModel.setOperationId(operation.getID())
        operationModel.setValue(pmPointsTotal)
        operationModel.setMaxValue(pmPointsMax)
        operationModel.setDeltaFrom(self.__getCheckedPmPointsData(pmPointsTotal, pmPointsMax))

    def __fillBannerModel(self, bannerModel):
        isFirstEntrance = not getPersonalMissionData(PM_BRANCH.PERSONAL_MISSION_4).get(PersonalMission4.OPERATION_SHOWN, True)
        operation = first(listvalues(getBranchesSortedPmOperations(PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_3])))
        bannerState = getOperationBannerState(operation)
        bannerModel.setEnabled(not operation.isDisabled())
        bannerModel.setFirstTimeEntrance(isFirstEntrance)
        bannerModel.setOperationId(operation.getID())
        bannerModel.setBannerState(bannerState)

    def __fillMainRewards(self, operationModel, operation):
        rewardsArray = operationModel.getRewards()
        rewardsArray.clear()
        rewards = ((RewardsType.MAIN, operation.getRewardQuest()), (RewardsType.OPERATION, operation.getAwardListRewardHonorQuest()), (RewardsType.CAMPAIGN, self.__campaign.getCampaignFinishedQuest()))
        bunusPacker = getBonusPacker()
        for rewardType, quest in rewards:
            if rewardType == RewardsType.CAMPAIGN and self.getBranchID() == PM_BRANCH.PERSONAL_MISSION_4:
                continue
            completedTasks, tasksNumber = getMainRewardInfo(operation, self.__campaignOperations, rewardType)
            if rewardType:
                rewardModel = operationModel.getRewardsType()()
                rewardModel.setRewardsType(rewardType)
                rewardModel.setCompletedTasks(completedTasks)
                rewardModel.setTasksNumber(tasksNumber)
                rawBonuses = quest.getRawBonuses()
                rawBonuses.pop('slots', None)
                self.__fillRewards(rewardModel.getItems(), quest.getBonuses(bonusData=rawBonuses), bunusPacker)
                rewardsArray.addViewModel(rewardModel)
            rewardsArray.invalidate()

        return

    def __fillDetails(self, operationModel, operation):
        detailsArray = operationModel.getDetails()
        detailsArray.clear()
        vehDetails = getVehicleDetails(operation)
        for detailIndex, detail in enumerate(vehDetails):
            if detailIndex == 0:
                minDetailPoints = 0
                maxDetailPoints = detail[1]
            else:
                minDetailPoints = vehDetails[detailIndex - 1][1]
                maxDetailPoints = detail[1] - minDetailPoints
            maxDetailPointRelativeProgression = detail[1]
            isInstalled = isVehDetailInstalled(self.__lastInstalledDetail, detail[0])
            detailModel = operationModel.getDetailsType()()
            totalPoints = operationModel.getValue()
            status, earnedPoints = self.__getDetailStatus(minDetailPoints, maxDetailPointRelativeProgression, totalPoints, isInstalled, operation, detailIndex)
            detailModel.setMaxPoint(maxDetailPoints)
            detailModel.setStatus(status)
            detailModel.setEarnedPoint(earnedPoints)
            detailModel.setId(getDetailNameByToken(detail[0]))
            detailModel.setHasAssemblingVideo(hasAssemblingVideo(operation.getID(), detailIndex + 1))
            detailsArray.addViewModel(detailModel)

        detailsArray.invalidate()

    def __fillRewardTankModel(self, mainViewModel):
        fillVehicleInfo(mainViewModel.vehicle, self.__operation.getPMAwardListVehicleBonus())

    def __fillMenuItems(self, mainViewModel):
        operationsArray = mainViewModel.getMenuItems()
        operationsArray.clear()
        for operation in self.__campaignOperations.values():
            operationModel = mainViewModel.getMenuItemsType()()
            operationModel.setOperationId(operation.getID())
            operationModel.setState(getOperationStatus(operation, self.__campaignOperations))
            operationModel.setOperationName(operation.getShortUserName())
            operationModel.setOperationIcon(operation.getIconID())
            operationsArray.addViewModel(operationModel)

        operationsArray.invalidate()

    def __fillAdditionalMissionsModel(self, operationModel, operation):
        additionalMissionsArray = operationModel.getAdditionalMissions()
        additionalMissionsArray.clear()
        pmPointsTotal, _ = self.__eventsCache.getPersonalMissions().getOperationPmPointsData(self.getBranchID(), operation.getID())
        for additionalMissionsType in AdditionalMissionType:
            additionalMissionModel = operationModel.getAdditionalMissionsType()()
            if operation.hasCollectedAllPoints() or operation.isCompleted():
                additionalMissionModel.setIsEnabled(False)
                additionalMissionModel.setType(additionalMissionsType)
                additionalMissionsArray.addViewModel(additionalMissionModel)
                continue
            earnedPoints, totalPoints = getRegularQuestsPMPoints(missionType=additionalMissionsType)
            isEnabled = isDailyQuestsEnable() if additionalMissionsType == AdditionalMissionType.DAILY else isWeeklyQuestsEnable()
            additionalMissionModel.setIsEnabled(isEnabled)
            additionalMissionModel.setType(additionalMissionsType)
            additionalMissionModel.setCurrentPoints(earnedPoints)
            additionalMissionModel.setMaxPoints(totalPoints)
            additionalMissionModel.setIsProgressHidden(pmPointsTotal < earnedPoints)
            additionalMissionsArray.addViewModel(additionalMissionModel)

        additionalMissionsArray.invalidate()

    def __fillActualMissionsModel(self, operationModel, operation):
        missionsArray = operationModel.getMissions()
        missionsArray.clear()
        actualMissions = self.__eventsCache.getPersonalMissions().getActualQuests(self.getBranchID(), operation.getID())
        bonusPacker = getBonusPacker(isOperationCompleted=operation.isCompleted() or operation.hasCollectedAllPoints())
        for mission in actualMissions:
            missionModel = operationModel.getMissionsType()()
            chain = sorted(operation.getChainByClassifierAttr(mission.getMajorTag())[1])
            missionIndex = chain.index(mission.getID())
            self.__fillMissionModel(missionModel, mission, missionIndex + 1, len(chain), bonusPacker)
            missionsArray.addViewModel(missionModel)

        missionsArray.invalidate()

    def __updateAllMissions(self):
        with self.viewModel.missionsModel.transaction() as tx:
            self.__quests = getQuestsByOperationsChains((self.getBranchName(),))
            allMissionsArray = tx.getAllMissions()
            allMissionsArray.clear()
            for operationID, chainTree in self.__quests.items():
                _, maxLevel = self.__eventsCache.getPersonalMissions().getVehicleLevelRestrictions(operationID)
                operation = self.__eventsCache.getPersonalMissions().getOperationsForBranch(self.getBranchID()).get(operationID)
                allMissionModel = tx.getAllMissionsType()()
                allMissionModel.setOperationId(operationID)
                allMissionModel.setOperationName(operation.getUserName())
                allMissionModel.setMinRequiredVehicle(self.__operation.getRequiredVehicleLevel())
                allMissionModel.setMaxRequiredVehicle(maxLevel)
                missionsCategorizationsArray = allMissionModel.getMissionsCategorizations()
                bonusPacker = getBonusPacker(isOperationCompleted=operation.isCompleted() or operation.hasCollectedAllPoints())
                for chainType, chain in chainTree.items():
                    missionCategorizationModel = allMissionModel.getMissionsCategorizationsType()()
                    missionCategorizationModel.setMissionsCategory(MissionCategory(chainType))
                    missionsArray = missionCategorizationModel.getMissions()
                    for missionIndex, missionData in enumerate(chain.values()):
                        missionModel = missionCategorizationModel.getMissionsType()()
                        self.__fillMissionModel(missionModel, missionData, missionIndex + 1, len(chain), bonusPacker)
                        missionsArray.addViewModel(missionModel)

                    missionsCategorizationsArray.addViewModel(missionCategorizationModel)

                allMissionsArray.addViewModel(allMissionModel)

            allMissionsArray.invalidate()
        self.__needQuestsUpdate = False

    def __updateMissions(self, missions):
        if not self.__quests:
            return
        for missionIDToUpdate in missions:
            newQuest = self.__eventsCache.getPersonalMissions().getQuestsForBranch(self.getBranchID()).get(missionIDToUpdate)
            questCategory = MISSIONS_ROLES_TO_CATEGORIES[newQuest.getQuestClassifier().classificationAttr].value
            self.__quests[newQuest.getOperationID()][questCategory][missionIDToUpdate] = newQuest
            missionsByOperationModel = first([ model for model in self.viewModel.missionsModel.getAllMissions() if model.getOperationId() == newQuest.getOperationID() ])
            missionsByChainModel = first([ model for model in missionsByOperationModel.getMissionsCategorizations() if model.getMissionsCategory().value == questCategory ])
            chainQuests = self.__quests[newQuest.getOperationID()][questCategory].values()
            operation = self.__eventsCache.getPersonalMissions().getOperationsForBranch(newQuest.getQuestBranch()).get(newQuest.getOperationID())
            chainQuestsModels = missionsByChainModel.getMissions()
            bonusPacker = getBonusPacker(isOperationCompleted=operation.isCompleted() or operation.hasCollectedAllPoints())
            with chainQuestsModels.transaction() as tx:
                for index, quest in enumerate(chainQuests):
                    if quest.getID() == missionIDToUpdate:
                        if not quest.isInitial():
                            self.__fillMissionModel(tx[index - 1], chainQuests[index - 1], index, len(chainQuestsModels), bonusPacker)
                        self.__fillMissionModel(tx[index], quest, index + 1, len(chainQuestsModels), bonusPacker)

    def __fillMissionModel(self, missionModel, mission, missionIndex, maxMissionNumber, bonusPacker):
        questConfig = getMissionConfigData(mission)
        maxProgressValue = questConfig.maxProgressValue
        battlesUniqueVehiclesCount = len(mission.getConditionsProgress().get('battlesUniqueVehicles', {}))
        currentProgressValue = maxProgressValue if mission.isCompleted() else battlesUniqueVehiclesCount
        if mission.isDisabled():
            status = MissionStatus.DISABLED
        elif mission.isCompleted():
            status = MissionStatus.COMPLETED
        elif mission.isInProgress():
            status = MissionStatus.ACTIVE
        else:
            status = MissionStatus.LOCKED
        missionModel.setOperationId(mission.getOperationID())
        missionModel.setCurrentMissionNumber(missionIndex)
        missionModel.setMaxMissions(maxMissionNumber)
        missionModel.setMissionStatus(status)
        missionModel.setMissionCategory(MISSIONS_ROLES_TO_CATEGORIES[mission.getMajorTag()])
        missionModel.setCurrentProgressValue(currentProgressValue)
        missionModel.setMaxProgressValue(maxProgressValue)
        missionModel.setAllQuestsRequired(questConfig.allQuestsRequired)
        self.__fillRewards(missionModel.getRewards(), mission.getBonuses(), bonusPacker)
        questsArray = missionModel.getQuests()
        questsArray.clear()
        for questID, questDetails in questConfig.questsDetails.items():
            questModel = missionModel.getQuestsType()()
            questModel.setId(questID)
            questModel.setQuestType(questDetails['icon'])
            questModel.setSummary(questDetails['title'])
            questModel.setQuestCondition(questDetails['description'])
            questsArray.addViewModel(questModel)

        questsArray.invalidate()

    def __fillRewards(self, rewardsModel, bonuses, packer):
        rewardsModel.clear()
        packMissionsBonusModelAndTooltipData(bonuses, packer, rewardsModel, self.__tooltipData)
        rewardsModel.invalidate()

    def __fillOperationStatusModel(self, mainModel):
        status, nextOperation = getDetailedOperationStatus(self.__operation, getBranchesSortedPmOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES))
        mainModel.status.setStatus(status)
        if nextOperation:
            mainModel.status.setNextOperationName(nextOperation.getUserName())
            mainModel.status.setOperationIdToPerform(nextOperation.getID())
        minLevel, _ = self.__eventsCache.getPersonalMissions().getVehicleLevelRestrictions(self.__operation.getID())
        mainModel.status.setRequiredVehicleLevel(minLevel)
        mainModel.status.setCurrentOperationId(self.__operation.getID())
        mainModel.status.setCurrentOperationName(self.__operation.getUserName())

    def __getDetailStatus(self, minDetailPoints, maxDetailPoints, totalPoints, isInstalled, operation, detailIndex):
        status = DetailStatus.DEFAULT
        earnedPoints = 0
        if totalPoints >= maxDetailPoints or operation.isCompleted():
            if detailIndex == MAX_DETAIL_ID - 1 and not operation.getRewardQuest().isCompleted():
                status = DetailStatus.IN_PROGRESS
            elif operation.isCompleted() or isInstalled and detailIndex != MAX_DETAIL_ID - 1:
                status = DetailStatus.DONE
            else:
                status = DetailStatus.NOT_RECEIVED
            earnedPoints = maxDetailPoints - minDetailPoints
        elif minDetailPoints <= totalPoints < maxDetailPoints:
            status = DetailStatus.IN_PROGRESS
            earnedPoints = totalPoints - minDetailPoints
        return (status, earnedPoints)

    def __getCheckedPmPointsData(self, pmPointsTotal, pmPointsMax):
        lastCheckedData = getPersonalMissionData(self.getBranchID()).get(getCheckedPMPointsKey(self.getBranchID()), 0)
        if self.__operationStatus == OperationState.UNAVAILABLE.value or lastCheckedData > pmPointsTotal:
            lastCheckedData = 0
        if self.__operationStatus in (OperationState.COMPLETED_WITH_HONORS.value, OperationState.COMPLETED.value):
            lastCheckedData = pmPointsMax
        return lastCheckedData

    def __setCheckedPMPointsData(self):
        if self.__operationStatus != OperationState.ACTIVE:
            return
        operationModel = self.__getOperationFromModel(self.__operation.getID())
        pmPointsTotal = operationModel.getValue()
        maxPoints = operationModel.getMaxValue()
        if pmPointsTotal == self.__getCheckedPmPointsData(pmPointsTotal, maxPoints):
            return
        setPersonalMissionData(self.getBranchID(), {getCheckedPMPointsKey(self.getBranchID()): pmPointsTotal})


class PersonalMissions3Window(WindowImpl):
    _TRANSPARENT_BACKGROUND_ALPHA = 0.0

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = self._TRANSPARENT_BACKGROUND_ALPHA
        super(PersonalMissions3Window, self).__init__(content=MainView(R.views.mono.personal_missions_30.main(), **kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
