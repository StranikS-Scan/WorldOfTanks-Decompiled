# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/personal_mission_flags.py
import nations
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.base_flags import IQuestsFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_helpers import headerQuestFormatterVo, wrapQuestGroup, LabelState
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import finders
from gui.server_events.events_dispatcher import showPersonalMission, showPersonalMissionOperationsPage, showPersonalMissionsOperationsMap
from gui.shared.formatters import icons
from helpers import dependency
from helpers.i18n import makeString as _ms
from personal_missions import PM_BRANCH
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
QUEST_TYPE_BY_PM_BRANCH = {PM_BRANCH.REGULAR: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR,
 PM_BRANCH.PERSONAL_MISSION_2: HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2}
HANGAR_HEADER_QUESTS_TO_PM_BRANCH = {value:key for key, value in QUEST_TYPE_BY_PM_BRANCH.iteritems()}

class WIDGET_PM_STATE(object):
    DISABLED = 0
    BRANCH_DISABLED = 2
    OPERATION_DISABLED = 4
    MISSION_DISABLED = 8
    UNAVAILABLE = 16
    LOW_LEVEL = 32
    NO_VEHICLE = 64
    DONE = 128
    DONE_LOCKED_NEXT = DONE | UNAVAILABLE
    DONE_LOW_NEXT = DONE | NO_VEHICLE
    COMPLETED = 256
    COMPLETED_LOCKED_NEXT = COMPLETED | UNAVAILABLE
    COMPLETED_LOW_NEXT = COMPLETED | NO_VEHICLE
    AVAILABLE = 512
    IN_PROGRESS = 1024
    ON_PAUSE = 2048


TOOLTIPS_HANGAR_HEADER_PM = {WIDGET_PM_STATE.BRANCH_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.LOW_LEVEL: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_LOWLEVEL,
 WIDGET_PM_STATE.MISSION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_MISSION_DISABLED,
 WIDGET_PM_STATE.AVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_AVAILABLE,
 WIDGET_PM_STATE.COMPLETED_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETEDLOCKEDNEXT,
 WIDGET_PM_STATE.COMPLETED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.DONE_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.DONE_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONELOCKEDNEXT,
 WIDGET_PM_STATE.DONE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.NO_VEHICLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_NOVEHICLE,
 WIDGET_PM_STATE.UNAVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.OPERATION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_OPERATION_DISABLED,
 WIDGET_PM_STATE.DISABLED: None}
TOOLTIPS_HANGAR_HEADER_PM2 = {WIDGET_PM_STATE.BRANCH_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_BRANCH_DISABLED,
 WIDGET_PM_STATE.LOW_LEVEL: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_LOWLEVEL,
 WIDGET_PM_STATE.MISSION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_MISSION_DISABLED,
 WIDGET_PM_STATE.AVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_AVAILABLE,
 WIDGET_PM_STATE.COMPLETED_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_COMPLETEDLOCKEDNEXT,
 WIDGET_PM_STATE.COMPLETED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_COMPLETED,
 WIDGET_PM_STATE.DONE_LOW_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.DONE_LOCKED_NEXT: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_DONELOCKEDNEXT,
 WIDGET_PM_STATE.DONE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DONE,
 WIDGET_PM_STATE.NO_VEHICLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_NOVEHICLE,
 WIDGET_PM_STATE.UNAVAILABLE: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS2_UNAVAILABLEFULL,
 WIDGET_PM_STATE.OPERATION_DISABLED: TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_OPERATION_DISABLED,
 WIDGET_PM_STATE.DISABLED: None}

def _findPersonalMissionsState(eventsCache, vehicle, branch):
    branchState = WIDGET_PM_STATE.DISABLED
    vehicleLvl = vehicle.level
    vehicleType = vehicle.descriptor.type
    fullDone = True
    statesQueue = (WIDGET_PM_STATE.AVAILABLE,
     WIDGET_PM_STATE.COMPLETED_LOW_NEXT,
     WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT,
     WIDGET_PM_STATE.COMPLETED,
     WIDGET_PM_STATE.DONE_LOW_NEXT,
     WIDGET_PM_STATE.DONE_LOCKED_NEXT,
     WIDGET_PM_STATE.DONE,
     WIDGET_PM_STATE.NO_VEHICLE,
     WIDGET_PM_STATE.UNAVAILABLE,
     WIDGET_PM_STATE.OPERATION_DISABLED,
     WIDGET_PM_STATE.DISABLED)
    currentState = branchState
    for operation in eventsCache.getPersonalMissions().getOperationsForBranch(branch).itervalues():
        operationState = WIDGET_PM_STATE.DISABLED
        if not operation.isCompleted():
            fullDone = False
        if operation.isDisabled():
            operationState |= WIDGET_PM_STATE.OPERATION_DISABLED
        elif not operation.isUnlocked():
            operationState |= WIDGET_PM_STATE.UNAVAILABLE
            continue
        for chainID, chain in operation.getQuests().iteritems():
            if not operation.getChainClassifier(chainID).matchVehicle(vehicleType):
                continue
            firsQuest = chain.values()[0]
            if vehicleLvl < firsQuest.getVehMinLevel():
                operationState |= WIDGET_PM_STATE.NO_VEHICLE
            for quest in chain.itervalues():
                if quest.isInProgress():
                    if operation.isDisabled():
                        return (WIDGET_PM_STATE.OPERATION_DISABLED, None)
                    if quest.isDisabled():
                        return (WIDGET_PM_STATE.MISSION_DISABLED, None)
                    if vehicleLvl < quest.getVehMinLevel():
                        return (WIDGET_PM_STATE.LOW_LEVEL, None)
                    if quest.isOnPause:
                        return (WIDGET_PM_STATE.ON_PAUSE, quest)
                    return (WIDGET_PM_STATE.IN_PROGRESS, quest)
                if operation.isDisabled() or quest.isDisabled() or operationState & WIDGET_PM_STATE.NO_VEHICLE:
                    continue
                if quest.isFullCompleted():
                    operationState |= WIDGET_PM_STATE.DONE
                if quest.isMainCompleted():
                    operationState |= WIDGET_PM_STATE.COMPLETED
                operationState |= WIDGET_PM_STATE.AVAILABLE

        currentState |= operationState

    if fullDone:
        currentState |= WIDGET_PM_STATE.COMPLETED
    if currentState & WIDGET_PM_STATE.DONE and currentState & WIDGET_PM_STATE.COMPLETED:
        currentState &= ~WIDGET_PM_STATE.COMPLETED
    for priorState in statesQueue:
        if currentState & priorState == priorState:
            return (priorState, None)

    return None


def _getPersonalMissionsIcon(vehicle, branch, active):
    if branch == PM_BRANCH.REGULAR:
        if active:
            return RES_ICONS.vehicleTypeOutline(vehicle.type)
        return RES_ICONS.vehicleTypeInactiveOutline(vehicle.type)
    if branch == PM_BRANCH.PERSONAL_MISSION_2:
        allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[vehicle.nationID]
        alliance = nations.ALLIANCES_TAGS_ORDER[allianceId]
        if active:
            return RES_ICONS.getAlliance32x32Icon(alliance)
        return RES_ICONS.getAlliance32x32InactiveIcon(alliance)


def _getPersonalMissionsTooltip(branch, key):
    if branch == PM_BRANCH.REGULAR:
        return TOOLTIPS_HANGAR_HEADER_PM.get(key, '')
    return TOOLTIPS_HANGAR_HEADER_PM2.get(key, '') if branch == PM_BRANCH.PERSONAL_MISSION_2 else ''


class PersonalMissionsFlag(IQuestsFlag):
    __slots__ = ()
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    @classmethod
    def isFlagSuitable(cls, questType):
        return questType in QUEST_TYPE_BY_PM_BRANCH.values()

    @classmethod
    def formatQuests(cls, vehicle, params):
        if vehicle is None:
            return
        else:
            isPersonalMissionsEnabled = cls.__lobbyContext.getServerSettings().isPersonalMissionsEnabled() and cls.__limitedUIController.isRuleCompleted(LuiRules.PERSONAL_MISSIONS)
            if not isPersonalMissionsEnabled:
                return []
            result = []
            states = []
            if vehicle.isOnlyForBattleRoyaleBattles:
                return []
            for branch in reversed(PM_BRANCH.ACTIVE_BRANCHES):
                questType = QUEST_TYPE_BY_PM_BRANCH[branch]
                if not cls.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(branch):
                    result.append(headerQuestFormatterVo(False, _getPersonalMissionsIcon(vehicle, branch, False), _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.EMPTY)), questType, tooltip=_getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.BRANCH_DISABLED)))
                    states.append(WIDGET_PM_STATE.BRANCH_DISABLED)
                pmState, quest = _findPersonalMissionsState(cls.__eventsCache, vehicle, branch)
                states.append(pmState)
                enable = True
                personalMissionID = ''
                if pmState == WIDGET_PM_STATE.IN_PROGRESS:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ACTIVE), current=quest.getInternalID())
                    personalMissionID = quest.getID()
                    tooltip = TOOLTIPS_CONSTANTS.PERSONAL_QUESTS_PREVIEW
                elif pmState == WIDGET_PM_STATE.ON_PAUSE:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ON_PAUSE))
                    personalMissionID = quest.getID()
                    tooltip = TOOLTIPS_CONSTANTS.PERSONAL_QUESTS_PREVIEW
                elif pmState == WIDGET_PM_STATE.AVAILABLE:
                    icon = RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_PLUS
                    label = MENU.hangarHeaderPersonalMissionsLabel(LabelState.EMPTY)
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.AVAILABLE)
                elif pmState == WIDGET_PM_STATE.COMPLETED:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED)
                elif pmState == WIDGET_PM_STATE.COMPLETED_LOW_NEXT:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED_LOW_NEXT)
                elif pmState == WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.COMPLETED_LOCKED_NEXT)
                elif pmState == WIDGET_PM_STATE.DONE:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE)
                elif pmState == WIDGET_PM_STATE.DONE_LOW_NEXT:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE_LOW_NEXT)
                elif pmState == WIDGET_PM_STATE.DONE_LOCKED_NEXT:
                    icon = _getPersonalMissionsIcon(vehicle, branch, True)
                    label = _ms(MENU.hangarHeaderPersonalMissionsLabel(LabelState.ALL_DONE), icon=icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_OUTLINE_QUESTS_ALL_DONE))
                    tooltip = _getPersonalMissionsTooltip(branch, WIDGET_PM_STATE.DONE_LOCKED_NEXT)
                    enable = False
                else:
                    icon = _getPersonalMissionsIcon(vehicle, branch, False)
                    label = MENU.hangarHeaderPersonalMissionsLabel(LabelState.INACTIVE)
                    tooltip = _getPersonalMissionsTooltip(branch, pmState)
                    enable = False
                result.append(headerQuestFormatterVo(enable, icon, label, questType, questID=personalMissionID, tooltip=tooltip, isTooltipSpecial=bool(pmState & WIDGET_PM_STATE.IN_PROGRESS or pmState & WIDGET_PM_STATE.ON_PAUSE)))

            if all([ st == WIDGET_PM_STATE.NO_VEHICLE for st in states ]):
                for vo in result:
                    vo['tooltip'] = TOOLTIPS.HANGAR_HEADER_PERSONALMISSIONS_DISABLEDALL

            result = sorted(result, key=lambda quest: quest['enable'], reverse=True)
            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_PERSONAL, RES_ICONS.MAPS_ICONS_QUESTS_HEADERFLAGICONS_PERSONAL, result, True)

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        if questID:
            showPersonalMission(missionID=int(questID))
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_REGULAR:
            cls.__showAvailablePMOperation(PM_BRANCH.REGULAR)
        elif questType == HANGAR_HEADER_QUESTS.QUEST_TYPE_PERSONAL_PM2:
            cls.__showAvailablePMOperation(PM_BRANCH.PERSONAL_MISSION_2)

    @classmethod
    def __showAvailablePMOperation(cls, branch):
        for operationID in finders.BRANCH_TO_OPERATION_IDS[branch]:
            operation = cls.__eventsCache.getPersonalMissions().getAllOperations()[operationID]
            result, _ = operation.isAvailable()
            if result:
                showPersonalMissionOperationsPage(branch, operationID)
                return

        showPersonalMissionsOperationsMap()
