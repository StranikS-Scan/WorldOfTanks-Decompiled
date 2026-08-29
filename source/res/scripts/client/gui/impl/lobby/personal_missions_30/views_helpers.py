# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/views_helpers.py
from __future__ import absolute_import
from future.utils import listvalues
import itertools
import typing
from collections import OrderedDict, namedtuple
import SoundGroups
from account_helpers.AccountSettings import PERSONAL_MISSION_3, PERSONAL_MISSION_4, AccountSettings
from account_helpers.settings_core.settings_constants import PersonalMission4, PersonalMission3
from adisp import adisp_process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import isBranchesStarted, getSuitableVehicles
from gui.game_control.links import URLMacros
from gui.impl.gen.view_models.views.lobby.personal_missions_30.additional_mission_model import AdditionalMissionType
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import OperationState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_reward_model import RewardsType
from gui.impl.gen.view_models.views.lobby.personal_missions_30.new_operation_banner import BannerState
from gui.impl.gen.view_models.views.lobby.personal_missions_30.operation_status_model import OperationStatus
from gui.impl.lobby.personal_missions_30.personal_mission_constants import MAX_DAILY_QUESTS_PM_POINTS, MAX_DETAIL_ID, MAX_NEWBIE_DAILY_QUESTS_PM_POINTS, MISSIONS_ROLES_TO_CATEGORIES, STAGES_CONFIG, AssemblingType
from gui.server_events.bonuses import PersonalMissionsPointsTokensBonus
from gui.server_events.event_items import NEWBIES_QUESTS_PASS_TOKEN
from gui.server_events.finders import getBranchByOperationId, PM_POINTS_TOKEN
from gui.server_events.personal_progress.formatters import PMCardConditionsFormatter
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showBrowserOverlayView, showPM30OperationAssemblingVideoWindow
from gui.sounds.filters import States, StatesGroup
from helpers import dependency
from personal_missions import PM_BRANCH
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Tuple, Optional
    from gui.impl.lobby.personal_missions_30.personal_mission_constants import StageInfo
    from gui.server_events.event_items import PMOperation
ConditionsConfig = namedtuple('ConditionsConfig', 'maxProgressValue, allQuestsRequired, questsDetails')

def isIntroShown(intro, branchID):
    return getPersonalMissionData(branchID).get(intro, False)


def markIntroShown(introKey, branchID):
    settings = getPersonalMissionData(branchID, withDefaults=True)
    if not settings.get(introKey):
        settings[introKey] = True
        setPersonalMissionData(branchID, settings)


def isVehDetailInstalled(lastInstalledDetail, detail):
    return int(detail.rsplit(':')[-1]) <= lastInstalledDetail


def _vehDetailsSortKey(vehDetail):
    return int(vehDetail[0].rsplit(':')[-1])


def getVehicleDetails(operation):
    return sorted(operation.getVehDetails().items(), key=_vehDetailsSortKey)


def firstUnclaimedOperation(operations):
    unclaimedOperation = findFirst(lambda o: not o.isAwardAchieved(), operations)
    return unclaimedOperation


def getMissionConfigData(mission):
    maxProgressValue = 0
    allQuestsRequired = False
    missionQuests = OrderedDict()
    conditionConfig = PMCardConditionsFormatter(mission)
    for conditionsCfg in conditionConfig.bodyFormat():
        maxProgressValue = conditionsCfg.get('progressData', {}).get('uniqueVehicles', 1)
        initData = conditionsCfg.get('initData')
        if not allQuestsRequired:
            allQuestsRequired = not initData.get('isInOrGroup')
        questID = '{}_{}'.format(mission.getGeneralQuestID(), conditionsCfg.get('progressID'))
        missionQuests[questID] = {'title': initData.get('title'),
         'description': initData.get('description'),
         'icon': initData.get('iconID')}

    return ConditionsConfig(maxProgressValue, allQuestsRequired, missionQuests)


def getDetailNameByToken(token):
    return '_'.join(token.split(':')[2:])


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getBranchSortedPmOperations(branchID, eventsCache=None):
    return OrderedDict(sorted(eventsCache.getPersonalMissions().getOperationsForBranch(branchID).items()))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getBranchesSortedPmOperations(branches, eventsCache=None):
    return OrderedDict(sorted(eventsCache.getPersonalMissions().getAllOperations(branches).items()))


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getOperationStatus(operation, branchOperations=None, eventsCache=None):
    personalMissions = eventsCache.getPersonalMissions()
    if not branchOperations:
        branchOperations = getBranchSortedPmOperations(operation.getBranch())
    unclaimedOperation = firstUnclaimedOperation(listvalues(branchOperations))
    lastActiveOperationID = personalMissions.getLastActiveOperationID()
    state = OperationState.UNAVAILABLE
    if operation.isDisabled():
        state = OperationState.LOCKED
    elif operation.isFullCompleted():
        state = OperationState.COMPLETED_WITH_HONORS
    elif operation.isAwardAchieved():
        state = OperationState.COMPLETED
    elif operation.isWithAwardListBranch() and operation.isInProgress() or personalMissions.isBranchWithAwardListActive() and lastActiveOperationID == operation.getID() or operation.isWithoutAwardListBranch() and (operation.isActive() or operation.isFullCompleted(isFinalRewardReceived=False)):
        state = OperationState.ACTIVE
    elif not operation.isDisabled() and isOperationAvailableByVehicles(operation) and operation.isUnlocked() and (unclaimedOperation is None or unclaimedOperation.getID() == operation.getID()):
        state = OperationState.AVAILABLE
    return state


def getQuestsByOperationsChains(branchNames):
    operations = getBranchesSortedPmOperations(branchNames)
    allMissions = OrderedDict()
    for operationID, operation in operations.items():
        allMissions[operationID] = OrderedDict()
        for missionsType in operation.getIterationChain():
            missionsForChain = sorted(operation.getChainByClassifierAttr(missionsType)[1].values(), key=lambda q: q.getID())
            allMissions[operationID][MISSIONS_ROLES_TO_CATEGORIES[missionsType].value] = OrderedDict([ (missionData.getID(), missionData) for missionData in missionsForChain ])

    return allMissions


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getDetailedOperationStatus(operation, sortedOps=None, eventsCache=None):
    if not sortedOps:
        sortedOps = getBranchSortedPmOperations(operation.getBranch())
    isAdditionalOperation = operation.getBranch() == PM_BRANCH.PERSONAL_MISSION_4
    operations = listvalues(sortedOps)
    notCurrentOperations = [ pmOperation for pmOperation in operations if pmOperation.getID() != operation.getID() ]
    isAnotherOperationInProgress = any((operation.isInProgress() for operation in notCurrentOperations))
    nextNotStartedOperation = getNextNotStartedOperation(operation, isAdditionalOperation, notCurrentOperations)
    unclaimedOperation = firstUnclaimedOperation(operations)
    state = OperationStatus.AVAILABLE
    nextOperation = operation
    operationIsFullCompleted = operation.isFullCompleted()
    operationIsCompleted = operation.isCompleted()
    operationIsActive = operation.isActive()
    operationWasStarted = wasOperationActivatedBefore(operation, unclaimedOperation)
    operationIsPaused = operation.isPaused()
    operationIsInProgress = operation.isInProgress()
    anotherActiveOperation = first((operation for operation in notCurrentOperations if operation.isActive()))
    isCurrentOpAndAnotherEqual = anotherActiveOperation and anotherActiveOperation.getBranch() == operation.getBranch()
    isAllOpQuestsCompleted = isAllOperationQuestsCompleted(operation)
    selectedQuests = eventsCache.getPersonalMissions().getSelectedQuestsForBranch(operation.getBranch()).values()
    if all((operation.isFullCompleted() for operation in operations)):
        state = OperationStatus.CAMPAIGN_FINISHED
    elif not isAdditionalOperation and unclaimedOperation is not None and unclaimedOperation.getID() < operation.getID():
        state = OperationStatus.PRECEDING_OPERATION_NOT_COMPLETED
        nextOperation = unclaimedOperation
    elif operationIsFullCompleted:
        nextNotCompletedWithHonor = findFirst(lambda o: o.isCompleted and not o.isFullCompleted(), operations)
        if nextNotStartedOperation:
            state = OperationStatus.NOT_ALL_COMPLETED
            nextOperation = nextNotStartedOperation
        elif isAnotherOperationInProgress:
            state = OperationStatus.NOT_ALL_COMPLETED
            inProgressOperation = findFirst(lambda o: o.isInProgress(), operations)
            nextOperation = inProgressOperation
        elif nextNotCompletedWithHonor and all((o.isCompleted() for o in operations)):
            state = OperationStatus.NOT_ALL_COMPLETED_WITH_HONOR
            nextOperation = nextNotCompletedWithHonor
    elif not isOperationAvailableByVehicles(operation):
        state = OperationStatus.REQUIRES_VEHICLE
    elif eventsCache.getLockedPersonalMissions() and (operationIsPaused or not operationIsActive):
        state = OperationStatus.VEHICLE_IS_IN_BATTLE
    elif operationIsCompleted:
        if operationIsPaused or not operationIsActive:
            state = OperationStatus.COMPLETED
        elif nextNotStartedOperation and getPMInstalledVehDetails(operation.getBranch()) == MAX_DETAIL_ID:
            state = OperationStatus.NEXT_OPERATION_AVAILABLE
            nextOperation = nextNotStartedOperation
        elif operationIsInProgress:
            state = OperationStatus.ACTIVE
    elif operation.isFullCompleted(isFinalRewardReceived=False):
        state = OperationStatus.ACTIVE
    elif operationIsPaused or operationWasStarted and (isCurrentOpAndAnotherEqual or not selectedQuests and not isAllOpQuestsCompleted):
        state = OperationStatus.PAUSED
    elif operationIsInProgress:
        state = OperationStatus.ACTIVE
    return (state, nextOperation)


def getOperationBannerState(operation):
    state = BannerState.DEFAULT
    if operation.isFullCompleted():
        state = BannerState.COMPLETED_WITH_HONOR
    elif operation.isCompleted():
        state = BannerState.COMPLETED
    return state


def getMainRewardInfo(operation, allOperations, rewardType):
    completedTasks = 0
    tasksNumber = 0
    if rewardType == RewardsType.MAIN:
        tasksNumber = 1
        completedTasks = int(operation.isCompleted())
    elif rewardType == RewardsType.CAMPAIGN:
        completedTasks = len([ op for op in allOperations.values() if op.isFullCompleted() ])
        tasksNumber = len(allOperations)
    elif rewardType == RewardsType.OPERATION:
        completedTasks = len(operation.getCompletedQuests())
        tasksNumber = len(list(itertools.chain.from_iterable(operation.getQuests().values())))
    return (completedTasks, tasksNumber)


def getNextNotStartedOperation(currentOperation, isAdditionalOperation, operations):
    notStartedOperation = None
    unclaimedOperation = firstUnclaimedOperation(operations)
    for operation in operations:
        if not operation.isStarted() and (isAdditionalOperation or operation.getID() > currentOperation.getID()) and unclaimedOperation is not None and unclaimedOperation.getID() == operation.getID():
            notStartedOperation = operation
            break

    return notStartedOperation


def isAllOperationQuestsCompleted(operation):
    return operation.getChainsCount() == len(operation.getCompletedFinalQuests())


def setForceLeavePM3State():
    from gui.Scaleform.lobby_entry import getLobbyStateMachine
    from gui.impl.lobby.personal_missions_30.state import PersonalMissions3State
    lsm = getLobbyStateMachine()
    lsm.getStateByCls(PersonalMissions3State).setForceLeave()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showRewardVehicleInHangar(operation, itemsCache=None):
    vehicleBonus = operation.getPMAwardListVehicleBonus()
    if vehicleBonus:
        itemCD = vehicleBonus.compactDescr
        vehicle = itemsCache.items.getItemByCD(itemCD)
        if vehicle.isInInventory:
            shared_events.selectVehicleInHangar(itemCD)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def isPMCampaignsStarted(branches, eventsCache=None):
    return any((operation for operation in eventsCache.getPersonalMissions().getAllOperations(branches=branches).values() if operation.isStarted()))


def setVideoOverlayOn():
    SoundGroups.g_instance.setState(StatesGroup.VIDEO_OVERLAY, States.VIDEO_OVERLAY_ON)


def setVideoOverlayOff():
    SoundGroups.g_instance.setState(StatesGroup.VIDEO_OVERLAY, States.VIDEO_OVERLAY_OFF)


def isOperationAvailableByVehicles(operation):
    return isPMCampaignsStarted(branches=PM_BRANCH.ALL_NAMES) or operation.hasRequiredVehicles() if operation.isWithoutAwardListBranch() else operation.hasRequiredVehicles()


def getStageNumberByDetailId(detailId):
    return int(detailId.split('_')[-1])


def hasAssemblingVideo(operationID, stageNumber):
    stageInfo = STAGES_CONFIG[operationID][stageNumber]
    return stageInfo.assemblingType == AssemblingType.VIDEO


def showStageAssemblingVideo(operationID, stageNumber):
    if hasAssemblingVideo(operationID, stageNumber):
        showPM30OperationAssemblingVideoWindow(operationID, stageNumber)


def getPersonalMissionsURL():
    return GUI_SETTINGS.personalMissions3.get('infoPage', {}).get('url')


@adisp_process
def openInfoPageScreen():
    urlParser = URLMacros()
    url = yield urlParser.parse(getPersonalMissionsURL())
    showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)


def wasOperationActivatedBefore(operation, unclaimedOperation=None):
    branchID = operation.getBranch()
    if unclaimedOperation is None:
        unclaimedOperation = firstUnclaimedOperation(listvalues(getBranchSortedPmOperations(branchID)))
    operationIDs = PM_BRANCH.BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_3][1:]
    wasBranchOperationActivated = operation.getID() in operationIDs and (unclaimedOperation is None or unclaimedOperation.getID() == operation.getID()) and getPMInstalledVehDetails(branchID) == 0
    return operation.isStarted() or wasBranchOperationActivated


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def getPMInstalledVehDetails(branchID, settingsCore=None):
    branchIDToFunction = {PM_BRANCH.PERSONAL_MISSION_3: settingsCore.serverSettings.getPM3InstalledVehDetails,
     PM_BRANCH.PERSONAL_MISSION_4: settingsCore.serverSettings.getPM4InstalledVehDetails}
    getInstalledVehDetails = branchIDToFunction.get(branchID)
    return getInstalledVehDetails() if getInstalledVehDetails is not None else 0


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setPMInstalledVehDetails(branchID, vehDetailNumber=0, settingsCore=None):
    branchIDToFunction = {PM_BRANCH.PERSONAL_MISSION_3: settingsCore.serverSettings.setPM3VehDetailInstalled,
     PM_BRANCH.PERSONAL_MISSION_4: settingsCore.serverSettings.setPM4VehDetailInstalled}
    setVehDetailInstalled = branchIDToFunction.get(branchID)
    if setVehDetailInstalled is not None:
        setVehDetailInstalled(vehDetailNumber)
    return


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def getPersonalMissionData(branchID, withDefaults=False, settingsCore=None):
    branchIDToFunction = {PM_BRANCH.PERSONAL_MISSION_3: settingsCore.serverSettings.getPersonalMission3Data,
     PM_BRANCH.PERSONAL_MISSION_4: settingsCore.serverSettings.getPersonalMission4Data}
    defaults = None
    if withDefaults:
        branchIDToDefaults = {PM_BRANCH.PERSONAL_MISSION_3: AccountSettings.getSettingsDefault(PERSONAL_MISSION_3),
         PM_BRANCH.PERSONAL_MISSION_4: AccountSettings.getSettingsDefault(PERSONAL_MISSION_4)}
        defaults = branchIDToDefaults.get(branchID)
    getPMData = branchIDToFunction.get(branchID)
    return getPMData(defaults) if getPMData is not None else {}


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setPersonalMissionData(branchID, data, settingsCore=None):
    branchIDToFunction = {PM_BRANCH.PERSONAL_MISSION_3: settingsCore.serverSettings.setPersonalMission3Data,
     PM_BRANCH.PERSONAL_MISSION_4: settingsCore.serverSettings.setPersonalMission4Data}
    setPMData = branchIDToFunction.get(branchID)
    if setPMData is not None:
        setPMData(data)
    return


def checkPM4FirstEntrance(operation):
    branchID = operation.getBranch()
    if operation.getID() in PM_BRANCH.BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_4] and not getPersonalMissionData(branchID).get(PersonalMission4.OPERATION_SHOWN, False):
        setPersonalMissionData(branchID, {PersonalMission4.OPERATION_SHOWN: True})


def getCheckedPMPointsKey(branchID):
    branchIDToConst = {PM_BRANCH.PERSONAL_MISSION_3: PersonalMission3.CHECKED_PM3_POINTS,
     PM_BRANCH.PERSONAL_MISSION_4: PersonalMission4.CHECKED_PM4_POINTS}
    return branchIDToConst.get(branchID)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getRegularQuestsPMPoints(missionType, eventsCache=None):
    earnedPoints = 0
    totalPoints = 0
    if missionType == AdditionalMissionType.DAILY:
        quests = eventsCache.getDailyQuests()
        totalPoints = MAX_NEWBIE_DAILY_QUESTS_PM_POINTS if eventsCache.questsProgress.getTokenCount(NEWBIES_QUESTS_PASS_TOKEN) else MAX_DAILY_QUESTS_PM_POINTS
    else:
        quests = eventsCache.getWeeklyQuests()
    for quest in quests.values():
        for bonus in quest.getBonuses():
            if isinstance(bonus, PersonalMissionsPointsTokensBonus):
                points = bonus.getValue().get(PM_POINTS_TOKEN).get('count')
                if missionType == AdditionalMissionType.WEEKLY:
                    totalPoints += points
                if quest.isCompleted():
                    earnedPoints += points

    return (earnedPoints, totalPoints)


@dependency.replace_none_kwargs(eventsCache=IEventsCache, hangarGuiCtrl=IHangarGuiController)
def isPM4BannerAvailable(eventsCache=None, hangarGuiCtrl=None):
    personalMissions = eventsCache.getPersonalMissions()
    helper = hangarGuiCtrl.currentGuiProvider.getMissionsHelper()
    if helper is None or not helper.isPM3MissionsSupported():
        return False
    else:
        pm4Operations = personalMissions.getOperationsForBranch(PM_BRANCH.PERSONAL_MISSION_4)
        if all((operation.isFullCompleted() for operation in pm4Operations.values())):
            return False
        isGroup12Started = isBranchesStarted(*(PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_1] + PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_2]))
        if not isGroup12Started and not bool(getSuitableVehicles()):
            return False
        disabledPMOperations = personalMissions.getDisabledPMOperations(PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_3])
        return False if any((operationID for operationID in pm4Operations if operationID in disabledPMOperations)) else True


def isPM4BannerAnimationShown():
    serverSettings = dependency.instance(ISettingsCore).serverSettings
    return serverSettings.getPersonalMission4Data().get(PersonalMission4.PM_BANNER_ANIMATION_KEY, False)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def markPM4BannerAnimationShown(reset=False, settingsCore=None):
    serverSettings = settingsCore.serverSettings
    defaults = AccountSettings.getSettingsDefault(PERSONAL_MISSION_4)
    settings = serverSettings.getPersonalMission4Data(defaults)
    settings[PersonalMission4.PM_BANNER_ANIMATION_KEY] = not reset
    serverSettings.setPersonalMission4Data(settings)


def getCurrentOperationLastInstalledDetail(operation):
    if operation.isCompleted():
        return MAX_DETAIL_ID
    return getPMInstalledVehDetails(operation.getBranch()) if operation.isStarted() else 0


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def canOpenOperationPage(operationID, eventsCache=None):
    branchName = PM_BRANCH.TYPE_TO_NAME[getBranchByOperationId(operationID)]
    return operationID not in eventsCache.getPersonalMissions().getDisabledPMOperations((branchName,))
