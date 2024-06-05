# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/achievements_controller.py
from Event import Event, EventManager
from achievements20.cache import ALLOWED_ACHIEVEMENT_TYPES, ROOT_ACHIEVEMENT_IDS
from advanced_achievements_client.items import SteppedAchievement
from chat_shared import SYS_MESSAGE_TYPE
from account_helpers import AccountSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from account_helpers.AccountSettings import ADVANCED_ACHIEVEMENTS, PREV_ACHIEVEMENT_SCORE, PREV_CATEGORY_LIST_DATA, PREV_PLAYER_COLLECTION_PROGRESS, PREV_TROPHY_COUNT, UNSEEN_ADVANCED_ACHIEVEMENTS, SEEN_TROPHIES_ADVANCED_ACHIEVEMENTS, MAIN_ADVANCED_ACHIEVEMENTS_PAGE_VISITED, IS_NEEDED_SHOW_HINT_ACHIEVEMENT_CATALOG
from helpers.events_handler import EventsHandler
from advanced_achievements_client import getters
from messenger.proto.events import g_messengerEvents
from helpers.dependency import replace_none_kwargs
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IAchievementsController

class AchievementsController(IAchievementsController, EventsHandler):

    def __init__(self):
        super(AchievementsController, self).__init__()
        self.__cachedScore = None
        self.__cachedProgress = None
        self.__cachedTrophiesAchievements = None
        self.__newAchievementsData = []
        self.__eventsManager = em = EventManager()
        self.__accSettings = AdvancedAchievementsSettingsManager()
        self.onUpdate = Event(em)
        self.onUnseenAchievementsUpdate = Event(em)
        self.onNewAchievementsEarned = Event(em)
        return

    def onLobbyInited(self, _):
        self._subscribe()
        g_clientUpdateManager.addCallbacks({'stats.dossier': self.__dossierUpdateCallBack})
        self.__newAchievementsData = []

    def onAccountBecomePlayer(self):
        self.__accSettings.start()
        self.__invalidateCache()

    def onAccountBecomeNonPlayer(self):
        self.__accSettings.stop()
        self.__invalidateCache()
        self._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__newAchievementsData = []

    def fini(self):
        self.__eventsManager.clear()
        super(AchievementsController, self).fini()

    def _getEvents(self):
        return ((g_messengerEvents.serviceChannel.onChatMessageReceived, self.__onChatMessageReceived),)

    def getCurrentScore(self, userId=None):
        trophiesAchievementScore = self.getTrophiesAchievementsScore(userId)
        if userId:
            dossierDescr = self.__getDossierDescr(userId)
            return getters.getTotalScore(dossierDescr).current + trophiesAchievementScore
        if not self.__cachedScore:
            self.__updateCachedScore()
        return self.__cachedScore.current + trophiesAchievementScore

    def getTotalScore(self):
        if not self.__cachedScore:
            self.__updateCachedScore()
        return self.__cachedScore.total

    def getProgress(self, userId=None):
        if userId:
            return getters.getTotalProgress(self.__getDossierDescr(userId))
        if not self.__cachedProgress:
            self.__updateCachedProgress()
        return self.__cachedProgress

    def getTrophiesAchievementsScore(self, userId=None):
        score = 0
        if userId:
            for achievement in getters.getTrophiesAchievements(self.__getDossierDescr(userId)):
                score += achievement.getScore().current

        else:
            if not self.__cachedTrophiesAchievements:
                self.__updateCachedTrophiesAchievements()
            for achievement in self.__cachedTrophiesAchievements:
                score += achievement.getScore().current

        return score

    def getTrophiesAchievements(self, userId=None):
        if userId:
            return getters.getTrophiesAchievements(self.__getDossierDescr(userId))
        if not self.__cachedTrophiesAchievements:
            self.__updateCachedTrophiesAchievements()
        return self.__cachedTrophiesAchievements

    def getTotalAchievementsCount(self, userId=None):
        totalCount = 0
        dossierDescr = self.__getDossierDescr(userId)
        for achievementCategory in ALLOWED_ACHIEVEMENT_TYPES:
            if achievementCategory in dossierDescr:
                for _, stage, __ in dossierDescr[achievementCategory].itervalues():
                    if stage:
                        totalCount += stage

        return totalCount

    def getAchievementByID(self, achievementID, achievementCategory):
        return getters.getAchievementByID(achievementID, achievementCategory)

    def getPrevAchievementsScore(self):
        return self.__accSettings.getPrevAchievementsScore()

    def setPrevAchievementsScore(self, value):
        self.__accSettings.setPrevAchievementsScore(value)

    def getPrevPlayerCollectionProgress(self):
        return self.__accSettings.getPrevPlayerCollectionProgress()

    def setPrevPlayerCollectionProgress(self, value):
        self.__accSettings.setPrevPlayerCollectionProgress(value)

    def getPrevCategoryData(self):
        return self.__accSettings.getPrevCategoryData()

    def setPrevCategoryData(self, value):
        self.__accSettings.setPrevCategoryData(value)

    def getPrevTrophy(self):
        return self.__accSettings.getPrevTrophy()

    def setPrevTrophy(self, value):
        self.__accSettings.setPrevTrophy(value)

    def getUnseenAdvancedAchievementsCount(self, achievementCategory, achievementID, userId=None):
        count = 0
        if userId:
            return count
        unseenList = self.getUnseenAdvancedAchievements(achievementCategory)
        dependenciesInTree = getters.getAllDependenciesInTree(achievementCategory, achievementID)
        unseenList &= dependenciesInTree
        count += len(unseenList)
        return count

    def getUnseenAdvancedAchievements(self, achievementCategory):
        return self.__accSettings.getUnseenAdvancedAchievements(achievementCategory)

    def getSeenTrophiesAdvancedAchievements(self, achievementCategory):
        return self.__accSettings.getSeenTrophiesAdvancedAchievements(achievementCategory)

    def getUnseenTrophiesAdvancedAchievementsCount(self, userId=None):
        count = 0
        if userId:
            return count
        else:
            achievementsData = {}
            achievements = self.getTrophiesAchievements(userId)
            for achievement in achievements:
                if achievementsData.get(achievement.getCategory()) is None:
                    achievementsData[achievement.getCategory()] = []
                achievementsData[achievement.getCategory()].append(achievement.getID())

            for category in achievementsData:
                seenAchievements = self.getSeenTrophiesAdvancedAchievements(category)
                count += len(set(achievementsData[category]) - seenAchievements)

            return count

    def getTotalUnseenAdvancedAchievementsCount(self, userId=None):
        total = 0
        if userId:
            return total
        for achievementCategory, achievementID in ROOT_ACHIEVEMENT_IDS:
            total += self.getUnseenAdvancedAchievementsCount(achievementCategory, achievementID, userId)

        total += self.getUnseenTrophiesAdvancedAchievementsCount(userId)
        return total

    def seeUnseenAdvancedAchievement(self, achievementCategory, achievementID):
        self.__accSettings.seeUnseenAdvancedAchievement(achievementCategory, achievementID)
        self.onUnseenAchievementsUpdate()

    def seeUnseenTrophiesAdvancedAchievement(self, achievementCategory, achievementID):
        self.__accSettings.addSeenTrophiesAdvancedAchievements(achievementCategory, achievementID)
        self.onUnseenAchievementsUpdate()

    def initUnseenAdvancedAchievements(self, achievementsData):
        unseenAchievements = {}
        for id, category, _ in achievementsData:
            if unseenAchievements.get(category) is None:
                unseenAchievements[category] = []
            unseenAchievements[category].append(id)

        for category in unseenAchievements:
            self.__accSettings.addUnseenAdvancedAchievements(category, set(unseenAchievements[category]))

        self.onUnseenAchievementsUpdate()
        return

    def getMainAdvancedAchievementsPageVisited(self):
        return self.__accSettings.getMainAdvancedAchievementsPageVisited()

    def setMainAdvancedAchievementsPageVisited(self, value):
        self.__accSettings.setMainAdvancedAchievementsPageVisited(value)

    def getShowHint(self):
        return self.__accSettings.getShowHint()

    def setShowHint(self, value):
        self.__accSettings.setShowHint(value)

    @replace_none_kwargs(itemsCache=IItemsCache)
    def __getDossierDescr(self, userId=None, itemsCache=None):
        return itemsCache.items.getAccountDossier(userId).getDossierDescr()

    def __dossierUpdateCallBack(self, *_):
        if self.__newAchievementsData:
            self.__updateCachedScore()
            self.__updateCachedProgress()
            self.__updateCachedTrophiesAchievements()
            self.__addUnseenAdvancedAchievements(self.__newAchievementsData)
            self.onNewAchievementsEarned(self.__newAchievementsData)
            self.__newAchievementsData = []

    def __onChatMessageReceived(self, *ctx):
        _, message = ctx
        if message is not None and message.type == SYS_MESSAGE_TYPE.achievementReceived.index() and message.data:
            self.__newAchievementsData.extend(self.__getAdvancedAchievementsData(message))
        return

    def __getAdvancedAchievementsData(self, message):
        achievementIDs = []
        popUpRecords = message.data.get('popUpRecords', {})
        for key, value in popUpRecords.iteritems():
            category, id = key
            if category in ALLOWED_ACHIEVEMENT_TYPES:
                achievedValue, stage, timestapm = value
                if stage > 0:
                    currentAchievement = self.getAchievementByID(id, category)
                    if isinstance(currentAchievement, SteppedAchievement):
                        if achievedValue == currentAchievement.getFakeAchievementForStage(stage).getProgress().total:
                            achievementIDs.append((id, category, timestapm))
                    else:
                        achievementIDs.append((id, category, timestapm))

        return achievementIDs

    def __updateCachedScore(self):
        self.__cachedScore = getters.getTotalScore(self.__getDossierDescr())

    def __updateCachedProgress(self):
        self.__cachedProgress = getters.getTotalProgress(self.__getDossierDescr())

    def __updateCachedTrophiesAchievements(self):
        self.__cachedTrophiesAchievements = getters.getTrophiesAchievements(self.__getDossierDescr())

    def __invalidateCache(self):
        self.__cachedScore = None
        self.__cachedProgress = None
        self.__cachedTrophiesAchievements = None
        return

    def __addUnseenAdvancedAchievements(self, achievementsData):
        unseenAchievements = {}
        for id, category, _ in achievementsData:
            if unseenAchievements.get(category) is None:
                unseenAchievements[category] = []
            unseenAchievements[category].append(id)

        for category in unseenAchievements:
            self.__accSettings.addUnseenAdvancedAchievements(category, set(unseenAchievements[category]))

        self.onUnseenAchievementsUpdate()
        return


class AdvancedAchievementsSettingsManager(object):
    __slots__ = ('__settings',)

    def __init__(self):
        self.__settings = dict()

    def start(self):
        self.__settings = AccountSettings.getSettings(ADVANCED_ACHIEVEMENTS)

    def stop(self):
        if self.__settings:
            AccountSettings.setSettings(ADVANCED_ACHIEVEMENTS, self.__settings)
        self.__settings.clear()

    def getPrevAchievementsScore(self):
        return self.__settings.get(PREV_ACHIEVEMENT_SCORE, 0)

    def setPrevAchievementsScore(self, value):
        self.__settings[PREV_ACHIEVEMENT_SCORE] = value

    def getShowHint(self):
        return self.__settings.get(IS_NEEDED_SHOW_HINT_ACHIEVEMENT_CATALOG, True)

    def setShowHint(self, value):
        self.__settings[IS_NEEDED_SHOW_HINT_ACHIEVEMENT_CATALOG] = value

    def getPrevPlayerCollectionProgress(self):
        return self.__settings.get(PREV_PLAYER_COLLECTION_PROGRESS, 0)

    def setPrevPlayerCollectionProgress(self, value):
        self.__settings[PREV_PLAYER_COLLECTION_PROGRESS] = value

    def getPrevCategoryData(self):
        return self.__settings.get(PREV_CATEGORY_LIST_DATA, [(0, 0), (0, 0), (0, 0)])

    def setPrevCategoryData(self, value):
        self.__settings[PREV_CATEGORY_LIST_DATA] = value

    def getPrevTrophy(self):
        return self.__settings.get(PREV_TROPHY_COUNT, 0)

    def setPrevTrophy(self, value):
        self.__settings[PREV_TROPHY_COUNT] = value

    def getUnseenAdvancedAchievements(self, achievementCategory):
        return set(self.__settings.get(UNSEEN_ADVANCED_ACHIEVEMENTS, {}).get(achievementCategory, []))

    def seeUnseenAdvancedAchievement(self, achievementCategory, seen):
        currentSet = self.getUnseenAdvancedAchievements(achievementCategory)
        currentSet.discard(seen)
        self.__settings[UNSEEN_ADVANCED_ACHIEVEMENTS][achievementCategory] = list(currentSet)

    def addUnseenAdvancedAchievements(self, achievementCategory, unseenSet):
        currentSet = self.getUnseenAdvancedAchievements(achievementCategory)
        currentSet.update(unseenSet)
        self.__settings[UNSEEN_ADVANCED_ACHIEVEMENTS][achievementCategory] = list(currentSet)

    def getSeenTrophiesAdvancedAchievements(self, achievementCategory):
        return set(self.__settings.get(SEEN_TROPHIES_ADVANCED_ACHIEVEMENTS, {}).get(achievementCategory, []))

    def addSeenTrophiesAdvancedAchievements(self, achievementCategory, unseenSet):
        currentSet = self.getSeenTrophiesAdvancedAchievements(achievementCategory)
        currentSet.add(unseenSet)
        self.__settings[SEEN_TROPHIES_ADVANCED_ACHIEVEMENTS][achievementCategory] = list(currentSet)

    def getMainAdvancedAchievementsPageVisited(self):
        return self.__settings.get(MAIN_ADVANCED_ACHIEVEMENTS_PAGE_VISITED, False)

    def setMainAdvancedAchievementsPageVisited(self, value):
        self.__settings[MAIN_ADVANCED_ACHIEVEMENTS_PAGE_VISITED] = value
