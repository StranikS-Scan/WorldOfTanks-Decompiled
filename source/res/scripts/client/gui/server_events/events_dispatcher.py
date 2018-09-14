# Embedded file name: scripts/client/gui/server_events/events_dispatcher.py
import constants
from gui.shared import g_eventBus, events, event_dispatcher as shared_events
from gui.shared.utils.functions import getViewName
from gui.server_events import awards
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

def showPQSeasonAwardsWindow(seasonID):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, getViewName(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, int(seasonID)), ctx={'seasonID': seasonID}))


def showTankwomanRecruitWindow(questID, isPremium, fnGroup, lnGroup, iGroup):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.QUESTS_RECRUIT_WINDOW, ctx={'questID': questID,
     'isPremium': isPremium,
     'fnGroup': fnGroup,
     'lnGroup': lnGroup,
     'iGroupID': iGroup}))


def showEventsWindow(eventID, eventType):
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.EVENTS_WINDOW, ctx={'eventID': eventID,
     'eventType': eventType}))


def showTutorialTabInEventsWindow():
    showEventsWindow('', constants.EVENT_TYPE.TUTORIAL)


def showAchievementsAward(achievements):
    shared_events.showAwardWindow(awards.AchievementsAward(achievements))


def showTokenAward(potapovQuest, tokenID, tokensCount):
    shared_events.showAwardWindow(awards.TokenAward(potapovQuest, tokenID, tokensCount))


def showVehicleAward(vehicle):
    shared_events.showAwardWindow(awards.VehicleAward(vehicle))


def showTankwomanAward(questID, tankmanData):
    shared_events.showAwardWindow(awards.TankwomanAward(questID, tankmanData), isUniqueName=False)


def showRegularAward(quest, isMainReward = True, isAddReward = False):
    shared_events.showAwardWindow(awards.RegularAward(quest, isMainReward, isAddReward))
