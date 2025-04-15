# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/unseen_events_manager.py
from Event import EventManager, Event
from constants import DailyQuestsLevels
from helpers import dependency
from gui.server_events import settings
from shared_utils import first
from skeletons.gui.game_control import IUnseenEventsCounter
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class UnseenEventManager(IUnseenEventsCounter):
    __slots__ = ('__seenQuests', '__unseenQuests', '__em', 'onUnseenEventUpdated', 'onSeenEvents')
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(UnseenEventManager, self).__init__()
        self.__seenQuests = {}
        self.__unseenQuests = {}
        self.__em = EventManager()
        self.onUnseenEventUpdated = Event(self.__em)
        self.onSeenEvents = Event(self.__em)

    def onAccountBecomeNonPlayer(self):
        self.__seenQuests.clear()
        self.__unseenQuests.clear()

    def addUnseenEvent(self, eventID, count):
        self.__unseenQuests[eventID] = self.__unseenQuests.setdefault(eventID, 0) + count
        self.onUnseenEventUpdated({eventID: self.__unseenQuests[eventID]})

    def updateUnseenEvents(self, data):
        self.__unseenQuests = data
        self.onUnseenEventUpdated(data)

    def getAllUnseenEventsCount(self):
        return sum((c for c in self.__unseenQuests.values()))

    def isUnseenEvent(self, eventID):
        return eventID in self.__unseenQuests

    def seenEvent(self, eventID, count):
        self.__seenQuests[eventID] = self.__seenQuests.setdefault(eventID, 0) + count
        if eventID in self.__unseenQuests:
            self.__unseenQuests[eventID] -= count
            if self.__unseenQuests[eventID] <= 0:
                self.__unseenQuests.pop(eventID)
        self.onSeenEvents({eventID: self.__seenQuests[eventID]})

    def seenEvents(self, eventsData):
        result = {}
        for eventID, count in eventsData.iteritems():
            self.__seenQuests[eventID] = self.__seenQuests.setdefault(eventID, 0) + count
            result[eventID] = self.__seenQuests[eventID]
            if eventID in self.__unseenQuests:
                self.__unseenQuests[eventID] -= count
                if self.__unseenQuests[eventID] <= 0:
                    self.__unseenQuests.pop(eventID)

        self.onSeenEvents(result)

    def commitToSettings(self):
        if self.__seenQuests:
            settings.visitEventsGUI({self.__eventsCache.getQuestByID(q) for q in self.__seenQuests})
            self.__seenQuests.clear()

    def getUnseenEventsCount(self, eventsID):
        return sum((c for event, c in self.__unseenQuests.iteritems() if event in eventsID))

    def cleanUpPremium(self):
        isPremium = self.__itemsCache.items.stats.isPremium
        if not isPremium:
            questSettings = settings.get()
            questSettings.update(visited=tuple(set(questSettings.visited).difference((q.getSeenSettingID() for q in self.__eventsCache.getDailyPremiumQuests().values()))))
            questSettings.save()

    def clearBonusDQ(self):
        questSettings = settings.get()
        lastBonusMissionVisited = questSettings.dailyQuests.lastBonusMissionVisited
        if lastBonusMissionVisited is None:
            return
        else:
            bonusQuest = first(self.__eventsCache.getDailyQuests(filterLevels=(DailyQuestsLevels.BONUS,)).values())
            if bonusQuest is None:
                return
            if lastBonusMissionVisited != bonusQuest.getID():
                questSettings.update(visited=tuple(set(questSettings.visited).difference({bonusQuest.getSeenSettingID()})))
                questSettings.save()
            return
