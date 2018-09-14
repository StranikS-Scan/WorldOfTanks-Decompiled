# Embedded file name: scripts/client/gui/server_events/PQController.py
import operator
import BigWorld
from gui.shared.utils.requesters.QuestsProgressRequester import FalloutQuestsProgressRequester, RandomQuestsProgressRequester
import potapov_quests
from items import tankmen
from gui.server_events import event_items
from potapov_quests import PQ_BRANCH

class _PotapovQuestsController(object):

    def __init__(self, pqType):
        self.questsProgress = None
        self.__clearCaches()
        self.__hasQuestsForSelect = False
        self.__hasQuestsForReward = False
        self._pqType = pqType
        return

    def init(self):
        for _, potapovQuestID in potapov_quests.g_cache:
            questBranch = potapov_quests.g_cache.branchByPotapovQuestID(potapovQuestID)
            if questBranch == self._pqType:
                quest = self.__makeQuest(potapovQuestID)
                tile = self.__makeTile(quest.getTileID())
                tile._addQuest(quest)
                season = self.__makeSeason(tile.getSeasonID())
                season._addTile(tile)
                quest.setSeasonID(season.getID())

    def fini(self):
        self.__clearCaches()

    def getNextTankwomanIDs(self, nationID, isPremium, fnGroup, lnGroup, iGroupID):
        lastFirstNameID, lastLastNameID, lastIconID = self.questsProgress.getTankmanLastIDs(nationID)
        return map(operator.itemgetter(1), tankmen.getNextUniqueIDs(BigWorld.player().databaseID, lastFirstNameID, lastLastNameID, lastIconID, nationID, isPremium, fnGroup, lnGroup, iGroupID))

    def getQuests(self):
        return self.__quests

    def getTiles(self):
        return self.__tiles

    def getSeasons(self):
        return self.__seasons

    def getSelectedQuests(self):
        result = {}
        for qID in self.questsProgress.getSelectedPotapovQuestsIDs():
            if qID in self.__quests:
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

    def update(self, eventsCache, diff = None):
        if diff is not None:
            potapovQuestsDiff = diff.get('potapovQuests', {})
            if 'selected' in potapovQuestsDiff:
                eventsCache.onSelectedQuestsChanged(potapovQuestsDiff['selected'], self._pqType)
            if 'slots' in potapovQuestsDiff:
                eventsCache.onSlotsCountChanged(potapovQuestsDiff['slots'], self._pqType)
            isNeedToUpdateProgress = len(potapovQuestsDiff)
        else:
            isNeedToUpdateProgress = True
        if isNeedToUpdateProgress:
            self.__hasQuestsForSelect = False
            self.__hasQuestsForReward = False
            freeSlotsCount = self.questsProgress.getPotapovQuestsFreeSlots()
            for qID, quest in self.__quests.iteritems():
                quest.updateProgress(self.questsProgress)

            selectedQuests = self.questsProgress.getSelectedPotapovQuestsIDs()
            selectedChains = set()
            for questID in selectedQuests:
                if questID in self.__quests:
                    selectedChains.add(self.__quests[questID].getChainID())

            for qID, quest in self.__quests.iteritems():
                if not self.__hasQuestsForSelect and freeSlotsCount and quest.canBeSelected() and quest.getChainID() not in selectedChains:
                    self.__hasQuestsForSelect = True
                if not self.__hasQuestsForReward and quest.needToGetReward():
                    self.__hasQuestsForReward = True
                if self.__hasQuestsForSelect and self.__hasQuestsForReward:
                    break

            for tile in self.__tiles.itervalues():
                tile.updateProgress(eventsCache)

            for season in self.__seasons.itervalues():
                season.updateProgress()

            eventsCache.onProgressUpdated(self._pqType)
        return

    def _getQuestsCache(self):
        raise NotImplemented

    def _getSeasonsCache(self):
        raise NotImplemented

    def _getTilesCache(self):
        raise NotImplemented

    def __clearCaches(self):
        self.__seasons = {}
        self.__tiles = {}
        self.__quests = {}

    def __makeSeason(self, seasonID):
        if seasonID not in self.__seasons:
            season = self.__seasons[seasonID] = event_items.PQSeason(seasonID, self._getSeasonsCache().getSeasonInfo(seasonID))
        else:
            season = self.__seasons[seasonID]
        return season

    def __makeTile(self, tileID):
        if tileID not in self.__tiles:
            tile = self.__tiles[tileID] = event_items.PQTile(tileID, self._getTilesCache().getTileInfo(tileID))
        else:
            tile = self.__tiles[tileID]
        return tile

    def __makeQuest(self, pqID, seasonID = None):
        if pqID not in self.__quests:
            pqType = self._getQuestsCache().questByPotapovQuestID(pqID)
            quest = self.__quests[pqID] = event_items.PotapovQuest(pqID, pqType, seasonID=seasonID)
        else:
            quest = self.__quests[pqID]
        return quest


class RandomPQController(_PotapovQuestsController):

    def __init__(self):
        pqType = PQ_BRANCH.TYPE_TO_NAME[PQ_BRANCH.REGULAR]
        super(RandomPQController, self).__init__(pqType)
        self.questsProgress = RandomQuestsProgressRequester()

    def _getQuestsCache(self):
        return potapov_quests.g_cache

    def _getTilesCache(self):
        return potapov_quests.g_tileCache

    def _getSeasonsCache(self):
        return potapov_quests.g_seasonCache


class FalloutPQController(_PotapovQuestsController):

    def __init__(self):
        pqType = PQ_BRANCH.TYPE_TO_NAME[PQ_BRANCH.FALLOUT]
        super(FalloutPQController, self).__init__(pqType)
        self.questsProgress = FalloutQuestsProgressRequester()

    def _getQuestsCache(self):
        return potapov_quests.g_cache

    def _getTilesCache(self):
        return potapov_quests.g_tileCache

    def _getSeasonsCache(self):
        return potapov_quests.g_seasonCache
