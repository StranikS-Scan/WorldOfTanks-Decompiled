# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/main_view.py
from collections import OrderedDict
from functools import partial
import SoundGroups
from account_helpers.settings_core.settings_constants import PersonalMission3
from constants import DAILY_QUESTS_CONFIG, Configs
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui import SystemMessages
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.additional_mission_model import AdditionalMissionType, AdditionalMissionModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory, OperationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.detail_model import DetailStatus, DetailModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_model import MainViewModel, MainScreenState, AnimationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_reward_model import RewardsType, MainViewRewardModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.mission_model import MissionStatus, MissionModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.missions_model import MissionsModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_model import OperationModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatus
from gui.impl.gen.view_models.views.lobby.personal_missions_30.quest_model import QuestModel
from gui.impl.gen.view_models.views.lobby.personal_missions_30.select_operation_model import SelectOperationModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.personal_missions_30.bonus_sorter import getBonusPacker, packMissionsBonusModelAndTooltipData
from gui.impl.lobby.personal_missions_30.hangar_helpers import AssemblingManager
from gui.impl.lobby.personal_missions_30.personal_mission_constants import IntroKeys, REWARDS_VIEW_TYPES, MISSIONS_ROLES_TO_CATEGORIES, MAX_DETAIL_ID, PM3_CAMPAIGN_ID, SoundsKeys, PERSONAL_MISSIONS_CAMPAIGN_3_SPACE
from gui.impl.lobby.personal_missions_30.state import MissionsState, AssemblingState, ProgressionState
from gui.impl.lobby.personal_missions_30.tooltips.mission_progress_tooltip import MissionProgressTooltip
from gui.impl.lobby.personal_missions_30.tooltips.missions_category_tooltip import MissionsCategoryTooltip
from gui.impl.lobby.personal_missions_30.views_helpers import isIntroShown, getQuestsByOperationsChains, firstUnclaimedOperation, getMissionConfigData, getDetailNameByToken, isVehDetailInstalled, getMainRewardInfo, getNextNotStartedOperation, showRewardVehicleInHangar, getOperationStatus, getStageNumberByDetailId, hasAssemblingVideo, isOperationAvailableByVehicles, wasOperationActivatedBefore, getRegularQuestsPMPoints
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.events_dispatcher import showMissions
from gui.server_events.events_helpers import isDailyQuestsEnable, isWeeklyQuestsEnable
from gui.shared.event_dispatcher import showPM30OperationIntroWindow, showPM30RewardsWindow, showVehicleHubOverview, showHangar
from gui.shared.gui_items.processors import quests as quests_proc
from gui.shared.gui_items.processors.quests import PMActivateSeason, PM3GetQuestRewards
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from personal_missions import PM_BRANCH
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IAchievements20EarningController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class MainView(ViewImpl):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_CAMPAIGN_3_SPACE
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
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
        self.__viewWasShown = False
        self.__needQuestsUpdate = True
        self.__pm3Campaign = self.__eventsCache.getPersonalMissions().getCampaignsForBranch(PM_BRANCH.PERSONAL_MISSION_3).get(PM3_CAMPAIGN_ID)
        self.__pm3Operations = self.__getSortedPm3Operations()
        self.__operationsToUpdate = {operationID:False for operationID in self.__pm3Operations.keys()}
        self.__operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
        self.__lastInstalledDetail = self.__settingsCore.serverSettings.getPM3InstalledVehDetails()
        self.__operationStatus = getOperationStatus(self.__operation, self.__pm3Operations)
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

    def initCurrentOperation(self):
        self.__assemblingManager.init()
        self.__assemblingManager.setHangarProgressionStateOn()
        self.__assemblingManager.changeVehicleGO(self.__operation.getID(), self.__getOperationLastInstalledDetail(self.__operation))
        hangarManager = self.__assemblingManager.getHangarOperationsManager()
        if hangarManager:
            hangarManager.onVehicleClick += self.__onGoToAssembling

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.personal_missions_30.tooltips.mission_progress_tooltip():
            if self.viewModel.getMainScreenState() == MainScreenState.PROGRESSION:
                missions = self.__eventsCache.getPersonalMissions().getActualQuests(PM_BRANCH.PERSONAL_MISSION_3, self.__operation.getID())
            else:
                category = self.viewModel.missionsModel.getMissionsCategory()
                missions = self.__quests.get(self.__operation.getID(), {}).get(category.value, {}).values()
            missionIndex = int(event.getArgument('missionIndex'))
            if 0 <= missionIndex < len(missions):
                return MissionProgressTooltip(mission=missions[missionIndex])
        elif contentID == R.views.mono.personal_missions_30.tooltips.missions_category_tooltip():
            return MissionsCategoryTooltip(category=MissionCategory(event.getArgument('category')), operation=self.__operation)
        return super(MainView, self).createToolTipContent(event, contentID)

    def setProgressionState(self):
        if self.__operationsToUpdate[self.__operation.getID()]:
            self.__updateViewModel(operationToUpdate=self.__operation)
        if self.viewModel.getMainScreenState() == MainScreenState.MISSIONS:
            self.__blur.disable()
        elif self.viewModel.getMainScreenState() == MainScreenState.ASSEMBLING:
            self.__assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=self.__operation.isFullCompleted(), callback=partial(self.viewModel.setAnimationState, AnimationState.CONTINUE_BACK))
        self.viewModel.setMainScreenState(MainScreenState.PROGRESSION)

    def setMissionsState(self):
        self.viewModel.setMainScreenState(MainScreenState.MISSIONS)
        self.__blur.enable()
        self.__setCheckedPM3PointsData()
        if self.__needQuestsUpdate:
            self.__updateAllMissions()
            self.__needQuestsUpdate = False

    def setAssemblingState(self):
        self.viewModel.setMainScreenState(MainScreenState.ASSEMBLING)

    def _getEvents(self):
        cameraEvents = self.__assemblingManager.getCameraEvents(self.viewModel)
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
         (self.viewModel.missionsModel.changeCategory, self.__changeMissionsCategory),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__settingsCore.onSettingsChanged, self.__onSettingsChanged),
         (self.__eventsCache.onPMSyncCompleted, self.__onPmEventsSync),
         (self.__eventsCache.onSyncCompleted, self.__onCommonSync),
         (self.__itemsCache.onPMSyncCompleted, self.__onPmItemsSync),
         (self.__itemsCache.onSyncCompleted, self.__onItemsSyncCompleted),
         (self.__assemblingManager.onCameraFlightStarted, self.__onCameraFlightStarted),
         (self.__assemblingManager.onCameraFlightFinished, self.__onCameraFlightFinished),
         (self.__assemblingManager.onAssemblingVideoFinished, self.__onAssemblingVideoFinished),
         (self.__assemblingManager.onAssemblingAnimationStarted, self.__onAssemblingAnimationStarted),
         (self.__assemblingManager.onAssemblingAnimationFinished, self.__onAssemblingAnimationFinished)]
        return viewEvents + cameraEvents

    def _onLoading(self, *args, **kwargs):
        super(MainView, self)._onLoading(*args, **kwargs)
        self.viewModel.setMainScreenState(self.__initState)
        self.__updateViewModel()

    def _onShown(self):
        self.__viewWasShown = True

    def _finalize(self):
        self.__tooltipData = {}
        if self.__viewWasShown:
            self.__setCheckedPM3PointsData()
        super(MainView, self)._finalize()
        hangarManager = self.__assemblingManager.getHangarOperationsManager()
        if hangarManager:
            hangarManager.onVehicleClick -= self.__onGoToAssembling
        self.__blur.fini()

    def __onCommonSync(self, *_):
        self.__fillRewardTankModel(self.viewModel)
        with self.viewModel.transaction() as tx:
            for operationModel in tx.getOperations():
                operation = self.__pm3Operations.get(operationModel.getOperationId())
                self.__fillAdditionalMissionsModel(operationModel, operation)
                self.__fillDetails(operationModel, operation)

        if self.__operation.isFullCompleted() and self.__assemblingManager.isSwitchingToFreeCameraNeeded():
            self.__assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=True, callback=partial(self.viewModel.setAnimationState, AnimationState.CONTINUE_BACK))

    def __onPmEventsSync(self, diff):
        self.__setAllOperationsUpdateStatus(needUpdate=True)
        if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
            self.__updateViewModel(operationToUpdate=self.__operation)
            self.__needQuestsUpdate = True
        pm3Quests = {}
        if diff:
            pm3Quests = diff.get('potapovQuests', {}).get('pm3', {}).get(('selected', '_r'), set())
            if diff.get('pm3_progress', {}):
                for questsID in diff.get('pm3_progress', {}):
                    pm3Quests.add(questsID)

        if pm3Quests:
            self.__updateMissions(pm3Quests)

    def __onItemsSyncCompleted(self, _, __):
        self.__updateViewModel(operationToUpdate=self.__operation)

    def __onPmItemsSync(self, *_):
        self.__setAllOperationsUpdateStatus(needUpdate=True)
        if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
            self.__updateViewModel(operationToUpdate=self.__operation)

    def __onSelectOperation(self, data):
        self.__setCheckedPM3PointsData()
        operationID = int(data.get(self.viewModel.OPERATION_ID, self.__operation.getID()))
        self.__operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
        self.__operationStatus = getOperationStatus(self.__operation, self.__pm3Operations)
        if self.__operationStatus == OperationState.AVAILABLE and not isIntroShown(IntroKeys.OPERATION_INTRO_VIEW.value % operationID):
            showPM30OperationIntroWindow(operationID)
        if self.__operationsToUpdate[self.__operation.getID()]:
            self.__updateViewModel(operationToUpdate=self.__operation)
        else:
            with self.viewModel.transaction() as tx:
                tx.setActiveOperationId(self.__operation.getID())
                self.__fillRewardTankModel(tx)
                self.__fillOperationStatusModel(tx)
        self.__assemblingManager.changeVehicleGO(self.__operation.getID(), self.__getOperationLastInstalledDetail(self.__operation))
        self.__assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=self.__operation.isFullCompleted())
        ProgressionState.goTo(operationID=self.__operation.getID())

    def __onOperationStatusButtonClick(self):
        if self.viewModel.status.getStatus().value in (OperationStatus.COMPLETED.value, OperationStatus.PAUSED.value, OperationStatus.AVAILABLE.value):
            if PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_3] not in self.__eventsCache.getPersonalMissions().getActiveCampaigns():
                self.__switchCampaign()
            self.__processOperation(self.__operation.getBranch(), self.__operation.getID())
            if not self.__operation.isStarted():
                self.__settingsCore.serverSettings.setPM3VehDetailInstalled()

    @args2params(str)
    def __onDetailInfo(self, detailId):
        if not getLobbyStateMachine().isStateEntered(AssemblingState.STATE_ID):
            AssemblingState.goTo()
        self.__assemblingManager.switchCameraToStagePosition(getStageNumberByDetailId(detailId), callback=partial(self.viewModel.setAnimationState, AnimationState.CONTINUE_DETAIL_INFO))

    def __onGoToAssembling(self):
        AssemblingState.goTo()
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
            self.__settingsCore.serverSettings.setPM3VehDetailInstalled(stageNumber)
            self.__pushDetailMessage(detailName=detailName)
        operationModel = self.__getOperationFromModel(self.__operation.getID())
        with operationModel.transaction() as tx:
            self.__fillDetails(tx, self.__operation)

    def __pushDetailMessage(self, detailName):
        SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.personalMissions.detailInstalled.body(), detailName=detailName), type=SystemMessages.SM_TYPE.PmActionCompleted, priority=NotificationPriorityLevel.LOW, messageData={'title': backport.text(R.strings.system_messages.personalMissions.detailInstalled.title(), operationName=self.__operation.getUserName())})

    @args2params(MissionCategory)
    def __onMissionShow(self, category):
        MissionsState.goTo(category=category)

    def setMissionViewCategory(self, category):
        self.viewModel.missionsModel.setMissionsCategory(category)

    @staticmethod
    def __onAdditionalMissionShow():
        showMissions()

    def __onVehiclePreview(self):
        self.__showVehiclePreview()

    def __showVehicleInHangar(self):
        self.__showRewardVehicle()

    @args2params(AnimationState)
    def __updateAnimationState(self, animationState):
        self.viewModel.setAnimationState(animationState)

    def __onCameraFlightStarted(self):
        self.viewModel.setCameraFlightInProgress(True)

    def __onCameraFlightFinished(self):
        self.viewModel.setCameraFlightInProgress(False)

    def __showVehiclePreview(self):
        vehicleBonus = self.__operation.getPM3VehicleBonus()
        if vehicleBonus is not None:
            itemCD = vehicleBonus.compactDescr
            vehicle = self.__itemsCache.items.getItemByCD(itemCD)
            if vehicle.isPreviewAllowed():
                showVehicleHubOverview(itemCD)
        return

    def __showRewardVehicle(self):
        showRewardVehicleInHangar(self.__operation)

    def __setAllOperationsUpdateStatus(self, needUpdate=False):
        self.__operationsToUpdate = {operationID:needUpdate for operationID in self.__pm3Operations.keys()}

    @args2params(MissionCategory)
    def __changeMissionsCategory(self, category):
        self.viewModel.missionsModel.setMissionsCategory(category)

    def __onBack(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __onAssemblingVideoFinished(self, stageNumber):
        AssemblingState.goTo()
        self.__assemblingManager.switchCameraToStagePosition(stageNumber, callback=partial(self.viewModel.setAnimationState, AnimationState.CONTINUE_CLAIM_DETAIL))

    def __onAssemblingAnimationStarted(self):
        AssemblingState.goTo()

    def __onAssemblingAnimationFinished(self):
        self.viewModel.setAnimationState(AnimationState.CONTINUE_CLAIM_DETAIL)

    def __showOperationVehicleVideo(self):
        showPM30OperationIntroWindow(self.__operation.getID(), force=True)

    @args2params(str)
    def __showDetailVideo(self, detailId):
        self.__assemblingManager.showStageAssemblingVideo(getStageNumberByDetailId(detailId))

    def __onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff or Configs.WEEKLY_QUESTS_CONFIG in diff:
            operationModel = self.__getOperationFromModel(self.__operation.getID())
            with operationModel.transaction() as tx:
                self.__fillAdditionalMissionsModel(tx, self.__operation)
        if 'isPM3QuestEnabled' in diff and not diff['isPM3QuestEnabled'] or 'disabledPMOperations' in diff or 'disabledPersonalMissions' in diff:
            if not diff.get('isPM3QuestEnabled', True) or self.__operation.getID() in diff.get('disabledPMOperations', {}):
                showHangar()
                return
            self.__setAllOperationsUpdateStatus(True)
            if self.viewModel.getMainScreenState() != MainScreenState.MISSIONS:
                self.__updateViewModel(operationToUpdate=self.__operation)
                self.__needQuestsUpdate = True
            else:
                self.__updateAllMissions()

    def __onSettingsChanged(self, diff):
        if PersonalMission3.PART_NO in diff:
            self.__lastInstalledDetail = self.__settingsCore.serverSettings.getPM3InstalledVehDetails()

    @decorators.adisp_process('updating')
    def __processOperation(self, branch, operation, questIDS=None):
        quests = []
        pm3Operations = self.__eventsCache.getPersonalMissions().getAllQuests(PM_BRANCH.V2_BRANCHES)
        if questIDS is not None:
            quests = [ pm3Operations.get(questID, None) for questID in questIDS ]
        res = yield quests_proc.PM3OperationSelect(branch, operation, quests).request()
        if res and res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)
        return

    @decorators.adisp_process('updating')
    def __switchCampaign(self):
        res = yield PMActivateSeason(self.__eventsCache.getPersonalMissions(), PM_BRANCH.PERSONAL_MISSION_3).request()
        if res and res.userMsg:
            SystemMessages.pushMessage(res.userMsg, type=res.sysMsgType)

    @decorators.adisp_process('updating')
    def __claimReward(self, detailName):
        self.__achievementsController.pause()
        quest = self.__operation.getPM3RewardQuest()
        res = yield PM3GetQuestRewards(quest).request()
        if res and res.success:

            def onFinalRewardWindowClosed(doStateChange=True):
                if doStateChange:
                    self.__onAssemblingVideoFinished(MAX_DETAIL_ID)
                self.__achievementsController.resume()

            showPM30RewardsWindow(ctx={'questID': quest.getID(),
             'rewards': {quest.getID(): quest.getBonuses()},
             'type': REWARDS_VIEW_TYPES['operation'],
             'closingCallback': onFinalRewardWindowClosed})
            self.__settingsCore.serverSettings.setPM3VehDetailInstalled(MAX_DETAIL_ID)
            self.__pushDetailMessage(detailName=detailName)
            self.__setAllOperationsUpdateStatus(needUpdate=True)
            self.__updateViewModel(operationToUpdate=self.__operation)
            self.__assemblingManager.assembleStage(MAX_DETAIL_ID, isFinalStage=True)
        else:
            self.__achievementsController.resume()
            if res and res.userMsg:
                SystemMessages.pushMessage(res.userMsg, priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.ErrorSimple)

    def __getSortedPm3Operations(self):
        return OrderedDict(sorted(self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).items()))

    def __getOperationFromModel(self, operationID):
        return first([ operationModel for operationModel in self.viewModel.getOperations() if operationModel.getOperationId() == operationID ], None)

    def __getOperationLastInstalledDetail(self, operation):
        if operation.isCompleted():
            return MAX_DETAIL_ID
        return 0 if not operation.isStarted() else self.__lastInstalledDetail

    def __updateViewModel(self, operationToUpdate=None):
        self.__pm3Operations = self.__getSortedPm3Operations()
        self.__operation = self.__pm3Operations.get(self.__operation.getID())
        self.__operationStatus = getOperationStatus(self.__operation, self.__pm3Operations)
        with self.viewModel.transaction() as tx:
            tx.setActiveOperationId(self.__operation.getID())
            tx.setCampaignName(self.__pm3Campaign.getUserName())
            self.__fillRewardTankModel(tx)
            self.__fillMenuItems(tx)
            self.__fillOperationStatusModel(tx)
            operationsArray = tx.getOperations()
            if operationToUpdate is not None:
                for operationModel in self.viewModel.getOperations():
                    if operationModel.getOperationId() == operationToUpdate.getID():
                        self.__fillOperationModel(operationModel, operationToUpdate)
                        self.__operationsToUpdate[operationToUpdate.getID()] = False

            else:
                operationsArray.clear()
                for operation in self.__pm3Operations.values():
                    operationEmptyModel = tx.getOperationsType()()
                    operationModel = self.__fillOperationModel(operationEmptyModel, operation)
                    operationsArray.addViewModel(operationModel)
                    self.__setAllOperationsUpdateStatus(needUpdate=False)

            operationsArray.invalidate()
        return

    def __fillOperationModel(self, operationModel, operation):
        pmPointsTotal, pmPointsMax = self.__eventsCache.getPersonalMissions().getOperationPmPointsData(PM_BRANCH.PERSONAL_MISSION_3, operation.getID())
        operationModel.setOperationId(operation.getID())
        operationModel.setValue(pmPointsTotal)
        operationModel.setMaxValue(pmPointsMax)
        operationModel.setOperationState(getOperationStatus(operation, self.__pm3Operations))
        operationModel.setDeltaFrom(self.__getCheckedPm3PointsData(pmPointsTotal, pmPointsMax))
        operationModel.setVehicleInHangar(operation.getPM3VehicleBonus().isInInventory)
        self.__fillMainRewards(operationModel, operation)
        self.__fillDetails(operationModel, operation)
        self.__fillAdditionalMissionsModel(operationModel, operation)
        self.__fillActualMissionsModel(operationModel, operation)
        return operationModel

    def __fillMainRewards(self, operationModel, operation):
        rewardsArray = operationModel.getRewards()
        rewardsArray.clear()
        rewards = ((RewardsType.MAIN, operation.getPM3RewardQuest()), (RewardsType.OPERATION, operation.getPM3RewardHonorQuest()), (RewardsType.CAMPAIGN, self.__pm3Campaign.getPM3CampaignFinishedQuest()))
        for rewardType, quest in rewards:
            completedTasks, tasksNumber = getMainRewardInfo(operation, self.__pm3Operations, rewardType)
            if rewardType:
                rewardModel = operationModel.getRewardsType()()
                rewardModel.setRewardsType(rewardType)
                rewardModel.setCompletedTasks(completedTasks)
                rewardModel.setTasksNumber(tasksNumber)
                rawBonuses = quest.getRawBonuses()
                rawBonuses.pop('slots', None)
                self.__fillRewards(rewardModel.getItems(), quest.getBonuses(bonusData=rawBonuses), getBonusPacker())
                rewardsArray.addViewModel(rewardModel)
            rewardsArray.invalidate()

        return

    def __fillDetails(self, operationModel, operation):
        detailsArray = operationModel.getDetails()
        detailsArray.clear()
        vehDetails = sorted(tuple(operation.getVehDetails().items()), key=lambda vehDetail: int(vehDetail[0].rsplit(':')[-1]))
        for detailIndex in range(0, len(vehDetails)):
            if detailIndex == 0:
                minDetailPoints = 0
                maxDetailPoints = vehDetails[detailIndex][1]
            else:
                minDetailPoints = vehDetails[detailIndex - 1][1]
                maxDetailPoints = vehDetails[detailIndex][1] - vehDetails[detailIndex - 1][1]
            maxDetailPointRelativeProgression = vehDetails[detailIndex][1]
            isInstalled = isVehDetailInstalled(self.__lastInstalledDetail, vehDetails[detailIndex][0])
            detailModel = operationModel.getDetailsType()()
            totalPoints = operationModel.getValue()
            status, earnedPoints = self.__getDetailStatus(minDetailPoints, maxDetailPointRelativeProgression, totalPoints, isInstalled, operation)
            detailModel.setMaxPoint(maxDetailPoints)
            detailModel.setStatus(status)
            detailModel.setEarnedPoint(earnedPoints)
            detailModel.setId(getDetailNameByToken(vehDetails[detailIndex][0]))
            detailModel.setHasAssemblingVideo(hasAssemblingVideo(operation.getID(), detailIndex + 1))
            detailsArray.addViewModel(detailModel)

        detailsArray.invalidate()

    def __fillRewardTankModel(self, mainViewModel):
        fillVehicleInfo(mainViewModel.vehicle, self.__operation.getPM3VehicleBonus())

    def __fillMenuItems(self, mainViewModel):
        operationsArray = mainViewModel.getMenuItems()
        operationsArray.clear()
        for operation in self.__pm3Operations.values():
            operationModel = mainViewModel.getMenuItemsType()()
            operationModel.setOperationId(operation.getID())
            operationModel.setState(getOperationStatus(operation, self.__pm3Operations))
            operationModel.setOperationName(operation.getShortUserName())
            operationModel.setOperationIcon(operation.getIconID())
            operationsArray.addViewModel(operationModel)

        operationsArray.invalidate()

    def __fillAdditionalMissionsModel(self, operationModel, operation):
        additionalMissionsArray = operationModel.getAdditionalMissions()
        additionalMissionsArray.clear()
        pmPointsTotal, _ = self.__eventsCache.getPersonalMissions().getOperationPmPointsData(PM_BRANCH.PERSONAL_MISSION_3, operation.getID())
        for additionalMissionsType in AdditionalMissionType:
            earnedPoints, totalPoints = getRegularQuestsPMPoints(missionType=additionalMissionsType)
            additionalMissionModel = operationModel.getAdditionalMissionsType()()
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
        actualMissions = self.__eventsCache.getPersonalMissions().getActualQuests(PM_BRANCH.PERSONAL_MISSION_3, operation.getID())
        for mission in actualMissions:
            missionModel = operationModel.getMissionsType()()
            chain = sorted(operation.getChainByClassifierAttr(mission.getMajorTag())[1])
            missionIndex = chain.index(mission.getID())
            self.__fillMissionModel(missionModel, mission, missionIndex + 1, len(chain))
            missionsArray.addViewModel(missionModel)

        missionsArray.invalidate()

    def __updateAllMissions(self):
        with self.viewModel.missionsModel.transaction() as tx:
            self.__quests = getQuestsByOperationsChains()
            allMissionsArray = tx.getAllMissions()
            allMissionsArray.clear()
            for operation, chainTree in self.__quests.items():
                minLevel, maxLevel = self.__eventsCache.getPersonalMissions().getVehicleLevelRestrictions(operation)
                operationName = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operation).getUserName()
                allMissionModel = tx.getAllMissionsType()()
                allMissionModel.setOperationId(operation)
                allMissionModel.setOperationName(operationName)
                allMissionModel.setMinRequiredVehicle(minLevel)
                allMissionModel.setMaxRequiredVehicle(maxLevel)
                missionsCategorizationsArray = allMissionModel.getMissionsCategorizations()
                for chainType, chain in chainTree.items():
                    missionCategorizationModel = allMissionModel.getMissionsCategorizationsType()()
                    missionCategorizationModel.setMissionsCategory(MissionCategory(chainType))
                    missionsArray = missionCategorizationModel.getMissions()
                    for missionIndex, missionData in enumerate(chain.values()):
                        missionModel = missionCategorizationModel.getMissionsType()()
                        self.__fillMissionModel(missionModel, missionData, missionIndex + 1, len(chain))
                        missionsArray.addViewModel(missionModel)

                    missionsCategorizationsArray.addViewModel(missionCategorizationModel)

                allMissionsArray.addViewModel(allMissionModel)

            allMissionsArray.invalidate()
        self.__needQuestsUpdate = False

    def __updateMissions(self, missions):
        if not self.__quests:
            return
        for missionIDToUpdate in missions:
            newQuest = self.__eventsCache.getPersonalMissions().getQuestsForBranch(PM_BRANCH.PERSONAL_MISSION_3).get(missionIDToUpdate)
            questCategory = MISSIONS_ROLES_TO_CATEGORIES[newQuest.getQuestClassifier().classificationAttr].value
            self.__quests[newQuest.getOperationID()][questCategory][missionIDToUpdate] = newQuest
            missionsByOperationModel = first([ model for model in self.viewModel.missionsModel.getAllMissions() if model.getOperationId() == newQuest.getOperationID() ])
            missionsByChainModel = first([ model for model in missionsByOperationModel.getMissionsCategorizations() if model.getMissionsCategory().value == questCategory ])
            chainQuests = self.__quests[newQuest.getOperationID()][questCategory].values()
            chainQuestsModels = missionsByChainModel.getMissions()
            with chainQuestsModels.transaction() as tx:
                for index, quest in enumerate(chainQuests):
                    if quest.getID() == missionIDToUpdate:
                        if not quest.isInitial():
                            self.__fillMissionModel(tx[index - 1], chainQuests[index - 1], index, len(chainQuestsModels))
                        self.__fillMissionModel(tx[index], quest, index + 1, len(chainQuestsModels))

    def __fillMissionModel(self, missionModel, mission, missionIndex, maxMissionNumber):
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
        self.__fillRewards(missionModel.getRewards(), mission.getBonuses(), getBonusPacker())
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
        status, nextOperationID = self.__getDetailedOperationStatus()
        mainModel.status.setStatus(status)
        if nextOperationID:
            nextOperationName = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(nextOperationID).getUserName()
            mainModel.status.setNextOperationName(nextOperationName)
        mainModel.status.setRequiredVehicleLevel(self.__operation.getRequiredVehicleLevel())
        mainModel.status.setCurrentOperationId(self.__operation.getID())
        mainModel.status.setCurrentOperationName(self.__operation.getUserName())
        mainModel.status.setOperationIdToPerform(nextOperationID)

    def __getDetailStatus(self, minDetailPoints, maxDetailPoints, totalPoints, isInstalled, operation):
        status = DetailStatus.DEFAULT
        earnedPoints = 0
        if totalPoints >= maxDetailPoints or operation.isCompleted():
            status = DetailStatus.DONE if isInstalled or operation.isCompleted() else DetailStatus.NOT_RECEIVED
            earnedPoints = maxDetailPoints - minDetailPoints
        elif totalPoints in range(minDetailPoints, maxDetailPoints):
            status = DetailStatus.IN_PROGRESS
            earnedPoints = totalPoints - minDetailPoints
        return (status, earnedPoints)

    def __getDetailedOperationStatus(self):
        operations = self.__pm3Operations.values()
        notCurrentOperations = [ operation for operation in operations if operation.getID() != self.__operation.getID() ]
        isAnotherOperationInProgress = any((operation.isInProgress() for operation in notCurrentOperations))
        nextNotStartedOperation = getNextNotStartedOperation(self.__operation, notCurrentOperations)
        unclaimedOperation = firstUnclaimedOperation(self.__operation, operations)
        state = OperationStatus.AVAILABLE
        nextOperationID = self.__operation.getID()
        operationIsFullCompleted = self.__operation.isFullCompleted()
        operationIsCompleted = self.__operation.isCompleted()
        operationIsActive = self.__operation.isActive()
        operationWasStarted = wasOperationActivatedBefore(self.__operation, unclaimedOperation)
        operationIsPaused = self.__operation.isPaused()
        operationIsInProgress = self.__operation.isInProgress()
        isAnotherOperationActive = any((operation.isActive() for operation in notCurrentOperations))
        if all((operation.isFullCompleted() for operation in operations)):
            state = OperationStatus.CAMPAIGN_FINISHED
        elif unclaimedOperation is not None and unclaimedOperation.getID() < self.__operation.getID():
            state = OperationStatus.PRECEDING_OPERATION_NOT_COMPLETED
            nextOperationID = unclaimedOperation.getID()
        elif operationIsFullCompleted:
            nextNotCompletedWithHonor = findFirst(lambda o: o.isCompleted and not o.isFullCompleted(), operations)
            if nextNotCompletedWithHonor and all([ o.isCompleted() for o in operations ]):
                state = OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR
                nextOperationID = nextNotCompletedWithHonor.getID()
            elif isAnotherOperationInProgress:
                state = OperationStatus.NOT_ALL_COMPLETED
                inProgressOperation = findFirst(lambda o: o.isInProgress(), operations)
                nextOperationID = inProgressOperation.getID()
            elif nextNotStartedOperation:
                state = OperationStatus.NOT_ALL_COMPLETED
                nextOperationID = nextNotStartedOperation.getID()
        elif not isOperationAvailableByVehicles(self.__operation):
            state = OperationStatus.REQUIRES_VEHICLE
        elif self.__eventsCache.getLockedPersonalMissions() and (operationIsPaused or not operationIsActive):
            state = OperationStatus.VEHICLE_IS_IN_BATTLE
        elif operationIsCompleted:
            if operationIsPaused and operationIsActive:
                state = OperationStatus.PAUSED
            elif not operationIsActive:
                state = OperationStatus.COMPLETED
            elif nextNotStartedOperation:
                state = OperationStatus.NEXT_OPERATION_AVAILABLE
                nextOperationID = nextNotStartedOperation.getID()
            elif operationIsInProgress:
                state = OperationStatus.ACTIVE
        elif operationIsPaused or operationWasStarted and isAnotherOperationActive:
            state = OperationStatus.PAUSED
        elif operationIsInProgress:
            state = OperationStatus.ACTIVE
        return (state, nextOperationID)

    def __getCheckedPm3PointsData(self, pmPointsTotal, pmPointsMax):
        lastCheckedData = self.__settingsCore.serverSettings.getPersonalMission3Data().get(PersonalMission3.CHECKED_PM3_POINTS, 0)
        if self.__operationStatus == OperationState.UNAVAILABLE.value or lastCheckedData > pmPointsTotal:
            lastCheckedData = 0
        if self.__operationStatus in (OperationState.COMPLETED_WITH_HONORS.value, OperationState.COMPLETED.value):
            lastCheckedData = pmPointsMax
        return lastCheckedData

    def __setCheckedPM3PointsData(self):
        if self.__operationStatus != OperationState.ACTIVE:
            return
        operationModel = self.__getOperationFromModel(self.__operation.getID())
        pmPointsTotal = operationModel.getValue()
        maxPoints = operationModel.getMaxValue()
        if pmPointsTotal == self.__getCheckedPm3PointsData(pmPointsTotal, maxPoints):
            return
        self.__settingsCore.serverSettings.setPersonalMission3Data({PersonalMission3.CHECKED_PM3_POINTS: pmPointsTotal})
        operationModel.setDeltaFrom(pmPointsTotal)


class PersonalMissions3Window(WindowImpl):
    _TRANSPARENT_BACKGROUND_ALPHA = 0.0

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = self._TRANSPARENT_BACKGROUND_ALPHA
        super(PersonalMissions3Window, self).__init__(content=MainView(R.views.mono.personal_missions_30.main(), **kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
