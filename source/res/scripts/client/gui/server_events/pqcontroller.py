# Embedded file name: scripts/client/gui/server_events/PQController.py
import weakref
import operator
import BigWorld
import potapov_quests
from Event import Event, EventManager
from items import tankmen
from gui.server_events import event_items

class PQController(object):

    def __init__(self, eventsCache):
        self.__clearCaches()
        self.__eventsCache = weakref.proxy(eventsCache)
        self.__em = EventManager()
        self.__hasQuestsForSelect = False
        self.__hasQuestsForReward = False
        self.onSelectedQuestsChanged = Event(self.__em)
        self.onSlotsCountChanged = Event(self.__em)
        self.onProgressUpdated = Event(self.__em)

    def init(self):
        for _, potapovQuestID in potapov_quests.g_cache:
            quest = self.__makeQuest(potapovQuestID)
            tile = self.__makeTile(quest.getTileID())
            tile._addQuest(quest)
            season = self.__makeSeason(tile.getSeasonID())
            season._addTile(tile)

    def fini(self):
        self.__em.clear()
        self.__clearCaches()

    def update(self, diff = None):
        if diff is not None:
            potapovQuestsDiff = diff.get('potapovQuests', {})
            if 'selected' in potapovQuestsDiff:
                self.onSelectedQuestsChanged(potapovQuestsDiff['selected'])
            if 'slots' in potapovQuestsDiff:
                self.onSlotsCountChanged(potapovQuestsDiff['slots'])
            isNeedToUpdateProgress = len(potapovQuestsDiff)
        else:
            isNeedToUpdateProgress = True
        if isNeedToUpdateProgress:
            self.__hasQuestsForSelect = False
            self.__hasQuestsForReward = False
            freeSlotsCount = self.__eventsCache.questsProgress.getPotapovQuestsFreeSlots()
            selectedQuestsIDs = self.__eventsCache.questsProgress.getSelectedPotapovQuestsIDs()
            for qID, quest in self.__quests.iteritems():
                quest.updateProgress(self.__eventsCache)
                if freeSlotsCount and quest.isUnlocked() and quest.getID() not in selectedQuestsIDs:
                    self.__hasQuestsForSelect = True
                if quest.needToGetReward():
                    self.__hasQuestsForReward = True

            for tile in self.__tiles.itervalues():
                tile.updateProgress(self.__eventsCache)

            for season in self.__seasons.itervalues():
                season.updateProgress(self.__eventsCache)

            self.onProgressUpdated()
        return

    def getNextTankwomanIDs(self, nationID, isPremium, fnGroup, lnGroup, iGroupID):
        lastFirstNameID, lastLastNameID, lastIconID = self.__eventsCache.questsProgress.getTankmanLastIDs(nationID)
        return map(operator.itemgetter(1), tankmen.getNextUniqueIDs(BigWorld.player().databaseID, lastFirstNameID, lastLastNameID, lastIconID, nationID, isPremium, fnGroup, lnGroup, iGroupID))

    def getQuests(self):
        return self.__quests

    def getTiles(self):
        return self.__tiles

    def getSeasons(self):
        return self.__seasons

    def getSelectedQuests(self):
        result = {}
        for qID in self.__eventsCache.questsProgress.getSelectedPotapovQuestsIDs():
            result[qID] = self.__quests[qID]

        return result

    def getTokens(self):
        result = set()
        for tile in self.getTiles().itervalues():
            result |= tile.getTokens().keys()

        return result

    def hasQuestsForSelect(self):
        return self.__hasQuestsForSelect

    def hasQuestsForReward(self):
        return self.__hasQuestsForReward

    def __clearCaches(self):
        self.__seasons = {}
        self.__tiles = {}
        self.__quests = {}

    def __makeSeason(self, seasonID):
        if seasonID not in self.__seasons:
            season = self.__seasons[seasonID] = event_items.PQSeason(seasonID, potapov_quests.g_seasonCache.getSeasonInfo(seasonID))
        else:
            season = self.__seasons[seasonID]
        return season

    def __makeTile(self, tileID):
        if tileID not in self.__tiles:
            tile = self.__tiles[tileID] = event_items.PQTile(tileID, potapov_quests.g_tileCache.getTileInfo(tileID))
        else:
            tile = self.__tiles[tileID]
        return tile

    def __makeQuest(self, pqID):
        if pqID not in self.__quests:
            pqType = potapov_quests.g_cache.questByPotapovQuestID(pqID)
            quest = self.__quests[pqID] = event_items.PotapovQuest(pqID, pqType)
        else:
            quest = self.__quests[pqID]
        return quest
