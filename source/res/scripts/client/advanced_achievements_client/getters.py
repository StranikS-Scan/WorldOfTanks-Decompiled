# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/advanced_achievements_client/getters.py
from collections import namedtuple
import typing
import sys
from achievements20.cache import ROOT_ACHIEVEMENT_IDS, ALLOWED_ACHIEVEMENT_TYPES, getCache
from advanced_achievements_client import items
from advanced_achievements_client.constants import AchievementType, NEAREST_REQUIRED_COUNT, BONUS_PRIORITY_MAP
from gui.server_events.bonuses import DogTagComponentBonus
if typing.TYPE_CHECKING:
    from typing import List

class _NearestCollector(object):
    __MATCHING_TYPES = (AchievementType.CUMULATIVE, AchievementType.REGULAR)
    __DESIRED_COUNT_BY_TYPE = {AchievementType.REGULAR: 2,
     AchievementType.CUMULATIVE: 1}

    def __init__(self):
        self.__rootSpecificAchievements = []
        self.__collectAll()

    def extract(self):
        chosen, leftovers = [], []
        for aType in self.__MATCHING_TYPES:
            desCount = self.__DESIRED_COUNT_BY_TYPE.get(aType, 0)
            topAchievements, leftoverAchievements = self.__getTopAchievementsForType(aType)
            topAchievements = self.__sortAchievements(topAchievements)
            chosen.extend(topAchievements[:desCount])
            if len(chosen) >= NEAREST_REQUIRED_COUNT:
                chosen = chosen[:NEAREST_REQUIRED_COUNT]
                break
            leftovers.extend(topAchievements[desCount:])
            leftovers.extend(leftoverAchievements)

        countToAdd = NEAREST_REQUIRED_COUNT - len(chosen)
        if countToAdd:
            chosen.extend(self.__sortAchievements(leftovers)[:countToAdd])
        return self.__sortAchievements(chosen)

    def __collectAll(self):
        for rootAchievement in _iterateRootAchievements():
            self.__rootSpecificAchievements.append(self.__collectForTree(rootAchievement))

    def __collectForTree(self, rootAchievement):
        achievementsByType = {}
        for achievement in rootAchievement.getInheritorsIterator(depth=2):
            aType = achievement.getType()
            if aType == AchievementType.STEPPED:
                aType = AchievementType.REGULAR
            if aType not in self.__MATCHING_TYPES or isinstance(achievement, items.VirtualStepAchievement):
                continue
            if not achievement.getProgress().isCompleted():
                achievementsByType.setdefault(aType, []).append(achievement)

        return achievementsByType

    def __getTopAchievementsForType(self, aType):
        topAchievements = []
        leftoverAchievements = []
        for achievementsByType in self.__rootSpecificAchievements:
            achievements = achievementsByType.get(aType)
            if achievements:
                topAchievementIndex = self.__getIndexOfTopAchievement(achievements)
                topAchievements.append(achievements[topAchievementIndex])
                achievements.pop(topAchievementIndex)
                leftoverAchievements.extend(achievements)

        return (topAchievements, leftoverAchievements)

    def __getIndexOfTopAchievement(self, achievements):
        topIndex = 0
        topAchievement = achievements[0]
        for index, achievement in enumerate(achievements):
            if self.__compareAchievements(topAchievement, achievement) > 0:
                topIndex = index
                topAchievement = achievement

        return topIndex

    def __sortAchievements(self, achievements):
        return sorted(achievements, cmp=self.__compareAchievements)

    @staticmethod
    def __compareAchievements(a, b):
        percentCmp = int(b.getProgress().getAsPercent() * 100) - int(a.getProgress().getAsPercent() * 100)
        return percentCmp or a.getID() - b.getID()


BonusTuple = namedtuple('BonusTuple', ('achievement', 'bonus'))

class _RewardManager(object):

    @classmethod
    def composeBonusTuples(cls, achievements, hideInvisible, sort):
        bonusTuples = []
        for achievement in achievements:
            bonuses = achievement.getRewards().getBonuses(split=True)
            for bonus in bonuses:
                bonusTuples.append(BonusTuple(achievement, bonus))

        if hideInvisible:
            bonusTuples = cls.__hideInvisibleBonusTuples(bonusTuples)
        if sort:
            bonusTuples = cls.__sortBonusTuples(bonusTuples)
        return bonusTuples

    @classmethod
    def __sortBonusTuples(cls, bonusTuples):
        bonusTuples.sort(key=lambda bonusTuple: BONUS_PRIORITY_MAP.get(bonusTuple.bonus.getName(), sys.maxint))
        return bonusTuples

    @classmethod
    def __hideInvisibleBonusTuples(cls, bonusTuples):
        return list(filter(cls.__isVisibleBonusTuple, bonusTuples))

    @classmethod
    def __isVisibleBonusTuple(cls, bonusTuple):
        bonus = bonusTuple.bonus
        if isinstance(bonus, DogTagComponentBonus):
            if len(bonus.getValue()) == 2:
                return True
        return False


def _iterateRootAchievements(dossierDescr=None):
    for achievementCategory, achievementID in ROOT_ACHIEVEMENT_IDS:
        yield getAchievementByID(achievementID, achievementCategory, dossierDescr)


def getAchievementByID(achievementID, achievementCategory, dossierDescr=None):
    return items.createAchievement(achievementID, achievementCategory, dossierDescr)


def getTrophiesAchievements(dossierDescr):
    trophiesAchievements = []
    for achievementCategory in ALLOWED_ACHIEVEMENT_TYPES:
        if achievementCategory in dossierDescr:
            for achievementId in dossierDescr[achievementCategory]:
                achievement = getAchievementByID(achievementId, achievementCategory, dossierDescr)
                if achievement.isDeprecated:
                    trophiesAchievements.append(achievement)

    return trophiesAchievements


def getLastReceivedAchievements(dossierDescr):
    lastReceivedAchievements = []
    for achievementCategory in ALLOWED_ACHIEVEMENT_TYPES:
        for achievementId in dossierDescr[achievementCategory]:
            _, stage, timestamp = dossierDescr[achievementCategory].get(achievementId)
            achievement = getAchievementByID(achievementId, achievementCategory, dossierDescr)
            if timestamp != 0 and stage > 0 and not achievement.isDeprecated:
                lastReceivedAchievements.append((achievementId, achievementCategory, timestamp))

    sortedList = sorted(lastReceivedAchievements, key=lambda record: -record[-1])[:NEAREST_REQUIRED_COUNT]
    return [ getAchievementByID(achievementId, achievementCategory, dossierDescr) for achievementId, achievementCategory, _ in sortedList ]


def getNearest():
    return _NearestCollector().extract()


def getTotalProgress(dossierDescr=None):
    totalProgress = None
    for achievement in _iterateRootAchievements(dossierDescr):
        progress = achievement.getProgress()
        totalProgress = totalProgress + progress if totalProgress else progress

    return totalProgress


def getTotalScore(dossierDescr=None):
    totalScore = None
    for achievement in _iterateRootAchievements(dossierDescr):
        score = achievement.getScore()
        totalScore = totalScore + score if totalScore else score

    return totalScore


def getAchievementsEarnedBeforeTime(dossierDescr, requestedTimestamp):
    achievements = []
    for achievementCategory in ALLOWED_ACHIEVEMENT_TYPES:
        for achievementId in dossierDescr[achievementCategory]:
            _, stage, timestamp = dossierDescr[achievementCategory].get(achievementId)
            if timestamp != 0 and stage > 0 and timestamp > requestedTimestamp:
                achievements.append((achievementId, achievementCategory, timestamp))

    return achievements


def getAllDependenciesInTree(achievementCategory, achievementID, listOfDependecies=None):
    if listOfDependecies is None:
        listOfDependecies = set()
    listOfDependecies.update({achievementID})
    for childrenId in getAchievementDependencies(achievementCategory, achievementID):
        getAllDependenciesInTree(achievementCategory, childrenId, listOfDependecies)

    return listOfDependecies


def getAchievementDependencies(achievementCategory, achievementID):
    return getCache().getAchievementByID(achievementCategory, achievementID).conditions.get('requiredAchievementIDs', set())


def getBonusTuples(achievements, hideInvisible=True, sort=True):
    return _RewardManager.composeBonusTuples(achievements, hideInvisible, sort)
