# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/events_dispatcher.py
import constants
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.server_events import awards, formatters
from gui.shared import g_eventBus, events, event_dispatcher as shared_events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

def showPQSeasonAwardsWindow(questsType):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, ctx={'questsType': questsType}), EVENT_BUS_SCOPE.LOBBY)


def showTankwomanRecruitWindow(questID, isPremium, fnGroup, lnGroup, iGroup):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, ctx={'questID': questID,
     'isPremium': isPremium,
     'fnGroup': fnGroup,
     'lnGroup': lnGroup,
     'iGroupID': iGroup}), EVENT_BUS_SCOPE.LOBBY)


def showEventsWindow(eventID=None, eventType=None, doResetNavInfo=False):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EVENTS_WINDOW, ctx={'eventID': eventID,
     'eventType': eventType,
     'doResetNavInfo': doResetNavInfo}), EVENT_BUS_SCOPE.LOBBY)


def showMissions(tab=None, eventID=None, groupID=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSIONS, ctx={'tab': tab,
     'eventID': eventID,
     'groupID': groupID,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)


def showMissionsMarathons(eventID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_MARATHONS_VIEW_PY_ALIAS, eventID=eventID, groupID=groupID, anchor=anchor)


def showMissionsCategories(eventID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, eventID=eventID, groupID=groupID, anchor=anchor)


def showMissionsForCurrentVehicle(eventID=None, groupID=None, anchor=None):
    showMissions(tab=QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, eventID=eventID, groupID=groupID, anchor=anchor)


def showMissionDetails(eventID, groupID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MISSION_DETAILS, ctx={'eventID': eventID,
     'groupID': groupID}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideMissionDetails():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_MISSION_DETAILS_VIEW), EVENT_BUS_SCOPE.LOBBY)


def showMission(eventID, eventType=None):
    """ Open missions interface with given event's detailed view.
    
    Possible requests:
        eventID is marathon's quest: open marathon tab with quest details;
        eventID is main marathon quest: open marathon tab;
        eventID is some othe quest: open categories tab with quest details;
        eventID is potapov quest: open old quest interface.
    """
    eventsCache = dependency.instance(IEventsCache)
    quests = eventsCache.getQuests()
    quest = quests.get(eventID)
    if eventType is not None and eventType == constants.EVENT_TYPE.POTAPOV_QUEST:
        showEventsWindow(eventID, eventType)
    elif quest is not None:
        if formatters.isMarathon(quest.getGroupID()):
            groups = eventsCache.getGroups()
            group = groups.get(quest.getGroupID())
            groupContent = group.getGroupContent(quests)
            mainQuest = group.getMainQuest(groupContent)
            if mainQuest and quest.getID() != mainQuest.getID():
                showMissionsMarathons(eventID=quest.getID(), groupID=group.getID(), anchor=group.getID())
            else:
                showMissionsMarathons(anchor=group.getID())
        else:
            showMissionsCategories(eventID=quest.getID(), groupID=quest.getGroupID(), anchor=quest.getGroupID())
    return


def showTutorialTabInEventsWindow(eventID=''):
    showEventsWindow(eventID, constants.EVENT_TYPE.TUTORIAL)


def showAchievementsAward(achievements):
    shared_events.showAwardWindow(awards.AchievementsAward(achievements))


def showTokenAward(potapovQuest, tokenID, tokensCount):
    shared_events.showAwardWindow(awards.TokenAward(potapovQuest, tokenID, tokensCount, showEventsWindow))


def showVehicleAward(vehicle):
    shared_events.showAwardWindow(awards.VehicleAward(vehicle))


def showMotiveAward(quest):
    shared_events.showAwardWindow(awards.MotiveQuestAward(quest, showMission))


def showTankwomanAward(questID, tankmanData):
    shared_events.showAwardWindow(awards.TankwomanAward(questID, tankmanData, showTankwomanRecruitWindow), isUniqueName=False)


def showMissionAward(quest, ctx):
    missionAward = awards.MissionAward(quest, ctx, showMissionsForCurrentVehicle)
    if missionAward.getAwards():
        shared_events.showMissionAwardWindow(missionAward)


def showPersonalMissionAward(quest, ctx):
    shared_events.showMissionAwardWindow(awards.PersonalMissionAward(quest, ctx, showEventsWindow))


def showRankedBoobyAward(quest):
    shared_events.showMissionAwardWindow(awards.RankedBoobyAward(quest, showMission))


def showActions(tab=None, anchor=None):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'tab': tab,
     'anchor': anchor}), scope=EVENT_BUS_SCOPE.LOBBY)
