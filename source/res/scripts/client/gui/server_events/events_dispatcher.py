# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/events_dispatcher.py
import constants
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.marathon.marathon_constants import DEFAULT_MARATHON_PREFIX
from gui.server_events import awards, events_helpers, recruit_helper, anniversary_helper
from gui.server_events.events_helpers import getLootboxesFromBonuses
from gui.shared import g_eventBus, events, event_dispatcher as shared_events, EVENT_BUS_SCOPE
from gui.shared.events import PersonalMissionsEvent
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.reward_window import TwitchRewardWindow, GiveAwayRewardWindow, PiggyBankRewardWindow
from shared_utils import first
OPERATIONS = {PERSONAL_MISSIONS_ALIASES.PERONAL_MISSIONS_OPERATIONS_SEASON_1_ID: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS_PAGE_ALIAS,
 PERSONAL_MISSIONS_ALIASES.PERONAL_MISSIONS_OPERATIONS_SEASON_2_ID: PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS2_OPERATIONS_PAGE_ALIAS}
_EVENTS_REWARD_WINDOW = {recruit_helper.RecruitSourceID.TWITCH_0: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_1: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_2: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_3: TwitchRewardWindow,
 recruit_helper.RecruitSourceID.TWITCH_4: TwitchRewardWindow,
 anniversary_helper.ANNIVERSARY_EVENT_PREFIX: GiveAwayRewardWindow}
_PIGGY_BANK_EVENT_NAME = 'piggyBank'

def showPQSeasonAwardsWindow(questsType):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, ctx={'questsType': questsType}), EVENT_BUS_SCOPE.LOBBY)


def showMissions(tab=None, missionID=None, groupID=None, marathonPrefix=None, anchor=None, showDetails=True):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSIONS, ctx={'tab': tab,
     'eventID': missionID,
     'groupID': groupID,
     'marathonPrefix': marathonPrefix,
     'anchor': anchor,
     'showMissionDetails': showDetails}), scope=EVENT_BUS_SCOPE.LOBBY)


def canOpenPMPage(branchID=None, operationID=None, missionID=None):
    serverSettings = dependency.instance(ILobbyContext).getServerSettings()
    eventsCache = dependency.instance(IEventsCache)
    disabledOperationsIds = serverSettings.getDisabledPMOperations()
    disabledMissionsIds = serverSettings.getDisabledPersonalMissions()

    def checkBranch(idx):
        return serverSettings.isPersonalMissionsEnabled(int(idx))

    def checkOperation(idx):
        return int(idx) not in disabledOperationsIds

    def checkMission(idx):
        return int(idx) not in disabledMissionsIds

    if missionID is not None:
        mission = eventsCache.getPersonalMissions().getAllQuests()[int(missionID)]
        operationID = mission.getOperationID()
        branchID = mission.getPMType().branch
        return checkBranch(branchID) and checkOperation(operationID) and checkMission(missionID)
    elif operationID is not None:
        operation = eventsCache.getPersonalMissions().getAllOperations()[int(operationID)]
        return checkBranch(operation.getBranch()) and checkOperation(operationID)
    else:
        return checkBranch(branchID) if branchID is not None else False


def showPersonalMission(missionID=None):
    if not canOpenPMPage(missionID=missionID):
        return
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'eventID': missionID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsChain(operationID, chainID):
    if not canOpenPMPage(operationID=operationID):
        return
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'operationID': operationID,
     'chainID': chainID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionOperationsPage(branchID, operationID):
    if not canOpenPMPage(branchID, operationID):
        showPersonalMissionsOperationsMap()
        return
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'branch': branchID,
     'operationID': operationID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsOperationsMap():
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS), EVENT_BUS_SCOPE.LOBBY)


def showMissionsGrouped(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsMarathon(marathonPrefix=DEFAULT_MARATHON_PREFIX):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, marathonPrefix=marathonPrefix)


def showMissionsCategories(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsForCurrentVehicle(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsElen(eventQuestsID=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, missionID=eventQuestsID, groupID=eventQuestsID, showDetails=False)


def showMissionsLinkedSet():
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS)


def showMissionDetails(missionID, groupID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSION_DETAILS, ctx={'eventID': missionID,
     'groupID': groupID}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionDetails(missionID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS, ctx={'eventID': missionID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionAwards():
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_AWARDS_VIEW_ALIAS), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionStartPage():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)


def hidePersonalMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_PERSONAL_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionBrowserView(ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_MISSIONS_BROWSER_VIEW, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showMission(eventID, eventType=None):
    eventsCache = dependency.instance(IEventsCache)
    quests = eventsCache.getQuests()
    quest = quests.get(eventID)
    if quest is None:
        prefix = events_helpers.getMarathonPrefix(eventID)
        if prefix is not None:
            showMissionsMarathon(marathonPrefix=prefix)
    if eventType is not None and eventType == constants.EVENT_TYPE.PERSONAL_MISSION:
        showPersonalMission(eventID)
    elif quest is not None:
        if events_helpers.isMarathon(quest.getGroupID()):
            groups = eventsCache.getGroups()
            group = groups.get(quest.getGroupID())
            groupContent = group.getGroupContent(quests)
            mainQuest = group.getMainQuest(groupContent)
            if mainQuest and quest.getID() != mainQuest.getID():
                showMissionsGrouped(missionID=quest.getID(), groupID=group.getID(), anchor=group.getID())
            else:
                showMissionsGrouped(anchor=group.getID())
        elif events_helpers.isLinkedSet(quest.getGroupID()):
            showMissionsLinkedSet()
        else:
            showMissionsCategories(missionID=quest.getID(), groupID=quest.getGroupID(), anchor=quest.getGroupID())
    return


def showAchievementsAward(achievements):
    shared_events.showAwardWindow(awards.AchievementsAward(achievements))


def showMotiveAward(quest):
    shared_events.showAwardWindow(awards.MotiveQuestAward(quest, showMission))


def showTankwomanAward(questID, tankmanData):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, ctx={'questID': questID,
     'isPremium': tankmanData.isPremium,
     'fnGroup': tankmanData.fnGroupID,
     'lnGroup': tankmanData.lnGroupID,
     'iGroupID': tankmanData.iGroupID}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def showRecruitWindow(recruitID, eventsCache=None):
    recruitData = recruit_helper.getRecruitInfo(recruitID)
    if recruitData.getSourceID() == recruit_helper.RecruitSourceID.TANKWOMAN:
        quest = eventsCache.getPersonalMissions().getAllQuests()[int(recruitID)]
        bonus = quest.getTankmanBonus()
        needToGetTankman = quest.needToGetAddReward() and not bonus.isMain or quest.needToGetMainReward() and bonus.isMain
        if needToGetTankman and bonus.tankman is not None:
            showTankwomanAward(quest.getID(), first(bonus.tankman.getTankmenData()))
    else:
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.TOKEN_RECRUIT_WINDOW, ctx={'tokenName': recruitID,
         'tokenData': recruitData}), EVENT_BUS_SCOPE.LOBBY)
    return


def showMissionAward(quest, ctx):
    eventName = recruit_helper.getSourceIdFromQuest(quest.getID()) or anniversary_helper.getEventNameByQuest(quest)
    if eventName in _EVENTS_REWARD_WINDOW:
        ctx['quest'] = quest
        ctx['eventName'] = eventName
        rewardWindow = _EVENTS_REWARD_WINDOW[eventName](ctx)
        rewardWindow.load()
    else:
        bonuses = getMissionInfoData(quest).getSubstituteBonuses()
        if bonuses:
            lootboxes = getLootboxesFromBonuses(bonuses)
            if lootboxes:
                for lootboxId, lootboxInfo in lootboxes.iteritems():
                    showLootboxesAward(lootboxId=lootboxId, lootboxCount=lootboxInfo['count'], isFree=lootboxInfo['isFree'])

            else:
                missionAward = awards.MissionAward(quest, ctx, showMissionsForCurrentVehicle)
                if missionAward.getAwards():
                    shared_events.showMissionAwardWindow(missionAward)


def showLootboxesAward(lootboxId, lootboxCount, isFree):
    pass


def showPiggyBankRewardWindow(creditsValue, isPremActive):
    ctx = {'eventName': _PIGGY_BANK_EVENT_NAME,
     'credits': creditsValue,
     'isPremActive': isPremActive}
    rewardWindow = PiggyBankRewardWindow(ctx)
    rewardWindow.load()


def showPersonalMissionAward(quest, ctx):
    shared_events.showPersonalMissionsQuestAwardScreen(quest, ctx, showPersonalMission)


def showRankedBoobyAward(quest):
    shared_events.showMissionAwardWindow(awards.RankedBoobyAward(quest, showMission))


def showOperationUnlockedAward(quest, ctx):
    shared_events.showAwardWindow(awards.OperationUnlockedAward(quest, ctx, showPersonalMissionsChain))


def showPersonalMissionsOperationAwardsScreen(ctx):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATION_AWARDS_SCREEN_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def updatePersonalMissionAward(context):
    g_eventBus.handleEvent(events.PersonalMissionsEvent(PersonalMissionsEvent.UPDATE_AWARD_SCREEN, ctx=context), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionFirstEntryAwardView(ctx):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_FIRST_ENTRY_AWARD_VIEW_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(alias, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showActions(tab=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'tab': tab,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)
