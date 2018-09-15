# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/events_dispatcher.py
import constants
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.server_events import awards, formatters
from gui.shared import g_eventBus, events, event_dispatcher as shared_events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from halloween_shared import HALLOWEEN_QUEST_PREFIX, HALLOWEEN_REWARD_QUEST_PREFIX, HALLOWEEN_ACHIEVEMENT_PREFIX
import BigWorld
from HalloweenSupplyDrop import HalloweenSupplyDrop

def showPQSeasonAwardsWindow(questsType):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, ctx={'questsType': questsType}), EVENT_BUS_SCOPE.LOBBY)


def showMissions(tab=None, missionID=None, groupID=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSIONS, ctx={'tab': tab,
     'eventID': missionID,
     'groupID': groupID,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMission(missionID=None):
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'eventID': missionID}), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionsChain(operationID, chainID):
    g_eventBus.handleEvent(events.LoadViewEvent(PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_PAGE_ALIAS, ctx={'operationID': operationID,
     'chainID': chainID}), EVENT_BUS_SCOPE.LOBBY)


def showMissionsMarathons(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsCategories(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showMissionsForCurrentVehicle(missionID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, missionID=missionID, groupID=groupID, anchor=anchor)


def showDossier(eventID=None, groupID=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE), EVENT_BUS_SCOPE.LOBBY)


def goToHalloweenMissionRewardBox(eventID=None, groupID=None, anchor=None):
    g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.MISSION_AWARD_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
    g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.BATTLE_RESULTS), scope=EVENT_BUS_SCOPE.LOBBY)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), EVENT_BUS_SCOPE.LOBBY)
    for e in BigWorld.entities.values():
        if isinstance(e, HalloweenSupplyDrop):
            e.remote_requestUIStateValidation()
            e.delayClick()


def closeHalloweenMissionRewardBox(eventID=None, groupID=None, anchor=None):
    g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.MISSION_AWARD_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
    for e in BigWorld.entities.values():
        if isinstance(e, HalloweenSupplyDrop):
            e.receivedSupplyDrop(True)


def showMissionsElen():
    showMissions(tab=QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS)


def showMissionDetails(missionID, groupID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSION_DETAILS, ctx={'eventID': missionID,
     'groupID': groupID}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionDetails(missionID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSION_DETAILS, ctx={'eventID': missionID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showPersonalMissionOperationsPage():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PERSONAL_MISSIONS), scope=EVENT_BUS_SCOPE.LOBBY)


def hidePersonalMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_PERSONAL_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showMission(eventID, eventType=None):
    """ Open missions interface with given event's detailed view.
    
    Possible requests:
        eventID is marathon's quest: open marathon tab with quest details;
        eventID is main marathon quest: open marathon tab;
        eventID is some othe quest: open categories tab with quest details;
        eventID is personal mission: open old quest interface.
    """
    eventsCache = dependency.instance(IEventsCache)
    quests = eventsCache.getQuests()
    quest = quests.get(eventID)
    if eventType is not None and eventType == constants.EVENT_TYPE.PERSONAL_MISSION:
        showPersonalMission(eventID)
    elif quest is not None:
        if formatters.isMarathon(quest.getGroupID()):
            groups = eventsCache.getGroups()
            group = groups.get(quest.getGroupID())
            groupContent = group.getGroupContent(quests)
            mainQuest = group.getMainQuest(groupContent)
            if mainQuest and quest.getID() != mainQuest.getID():
                showMissionsMarathons(missionID=quest.getID(), groupID=group.getID(), anchor=group.getID())
            else:
                showMissionsMarathons(anchor=group.getID())
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


def showGiftAward():
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.GIFT_RECRUIT_WINDOW), EVENT_BUS_SCOPE.LOBBY)


def showMissionAward(quest, ctx, bonus_data):
    qID = quest.getID()
    if qID.startswith(HALLOWEEN_REWARD_QUEST_PREFIX):
        missionAward = awards.HalloweenMissionAward(quest, ctx, bonus_data, None)
        for e in BigWorld.entities.values():
            if isinstance(e, HalloweenSupplyDrop):
                e.shownAwardPopup()

    elif qID.startswith(HALLOWEEN_QUEST_PREFIX):
        missionAward = awards.HalloweenMissionAward(quest, ctx, bonus_data, goToHalloweenMissionRewardBox)
    elif qID.startswith(HALLOWEEN_ACHIEVEMENT_PREFIX):
        missionAward = awards.HalloweenAchievementMissionAward(quest, ctx, showDossier)
    else:
        missionAward = awards.MissionAward(quest, ctx, showMissionsForCurrentVehicle)
    if missionAward.getAwards() or qID.startswith(HALLOWEEN_REWARD_QUEST_PREFIX):
        shared_events.showMissionAwardWindow(missionAward)
    return


def showPersonalMissionAward(quest, ctx):
    shared_events.showMissionAwardWindow(awards.PersonalMissionAward(quest, ctx, showPersonalMission))


def showRankedBoobyAward(quest):
    shared_events.showMissionAwardWindow(awards.RankedBoobyAward(quest, showMission))


def showOperationUnlockedAward(quest, ctx):
    shared_events.showAwardWindow(awards.OperationUnlockedAward(quest, ctx, showPersonalMissionsChain))


def showPersonalMissionCongratulationAward(ctx):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSION_AWARD_CONGRATULATION_VIEW_ALIAS
    g_eventBus.handleEvent(events.LoadViewEvent(alias, name='%s%d' % (alias, ctx['operationID']), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showActions(tab=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'tab': tab,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)
