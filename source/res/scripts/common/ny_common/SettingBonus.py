# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/SettingBonus.py
from itertools import imap
from operator import mul
from functools import partial
from typing import List, Dict, Tuple
from ny_common.settings import SettingBonusConsts

class SettingBonusDefaults(object):
    DEFAULT_ATMOSPHERE_MULTIPLIER = 1.0
    DEFAULT_COLLECTION_BONUS = 0.0


class SettingBonusConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getToyRatingsByRank(self):
        return self._config.get(SettingBonusConsts.TOY_RATINGS, ())

    def getAtmosphereMultipliers(self):
        return self._config.get(SettingBonusConsts.ATMOSPHERE_MULTIPLIERS, ())

    def getBonusTypes(self):
        return self._config.get(SettingBonusConsts.BATTLE_BONUSES, {}).keys()

    def getCollectionBonuses(self, bonusType, collectionName):
        return self._getBonusesByType(bonusType).get(SettingBonusConsts.COLLECTION_BONUSES, {}).get(collectionName, ())

    def getUniqueToysBonuses(self, bonusType):
        return self._getBonusesByType(bonusType).get(SettingBonusConsts.UNIQUE_TOYS_BONUSES, ())

    def getCollectionLevelsRating(self):
        return self._config.get(SettingBonusConsts.COLLECTION_LEVELS_RATING, ())

    def getUniqueToysLevelsRating(self):
        return self._config.get(SettingBonusConsts.UNIQUE_TOY_LEVELS_RATING, ())

    def getCollectionLevel(self, collectionDistribution):
        levelsRating = self.getCollectionLevelsRating()
        collectionRating = self._calculateCollectionRating(collectionDistribution)
        return self._calculateLevelByRating(levelsRating, collectionRating)

    def getUniqueToysLevel(self, collectionDistributions):
        levelsRating = self.getUniqueToysLevelsRating()
        uniqueToysRating = self.calculateUniqueToysRating(collectionDistributions)
        return self._calculateLevelByRating(levelsRating, uniqueToysRating)

    def getCollectionLevelSettingBonus(self, bonusType, collectionName, collectionLevel):
        collectionBonuses = self.getCollectionBonuses(bonusType, collectionName)
        return collectionBonuses[collectionLevel]

    def getUniqueToysLevelSettingBonus(self, bonusType, uniqueToysLevel):
        return self.getUniqueToysBonuses(bonusType)[uniqueToysLevel]

    def getAtmosphereMultiplierForLevel(self, level):
        atmosphereMultipliers = self.getAtmosphereMultipliers()
        return atmosphereMultipliers[level - 1]

    def _getBonusesByType(self, bonusType):
        return self._config.get(SettingBonusConsts.BATTLE_BONUSES, {}).get(bonusType, {})

    def _calculateCollectionRating(self, collectionDistribution):
        toyRatingByRank = self.getToyRatingsByRank()
        return sum(imap(mul, toyRatingByRank, collectionDistribution))

    def calculateUniqueToysRating(self, collectionDistributions):
        toyRatingByRank = self.getToyRatingsByRank()
        return sum(imap(sum, imap(partial(imap, mul, toyRatingByRank), collectionDistributions)))

    @staticmethod
    def _calculateLevelByRating(levelsRating, collectionRating):
        for level, bound in enumerate(levelsRating):
            if collectionRating < bound:
                return level - 1

        return len(levelsRating) - 1


class SettingBonus(object):
    PRECISION = 3

    @classmethod
    def getFormulasInfo(cls, atmosphereLevel, collectionDistributions, config):
        bonusTypes = config.getBonusTypes()
        collectionLevels = cls.calculateCollectionLevels(collectionDistributions, config)
        uniqueToysLevel = cls.calculateUniqueToysLevel(collectionDistributions.values(), config)
        return {bonusType:cls.getFormulaParams(bonusType, atmosphereLevel, collectionLevels, uniqueToysLevel, config) for bonusType in bonusTypes}

    @staticmethod
    def calculateBonusByFormulaInfo(formulaInfo):
        atmosphereMultiplier, collectionsBonus, toysBonus = formulaInfo
        return round(atmosphereMultiplier * (collectionsBonus + toysBonus), SettingBonus.PRECISION)

    @classmethod
    def getFormulaParams(cls, bonusType, atmosphereLevel, collectionLevels, uniqueToysLevel, config):
        atmosphereMultiplier = cls.getAtmosphereMultiplier(atmosphereLevel, config)
        collectionsBonus = cls.getCollectionsBonus(bonusType, collectionLevels, config)
        uniqueToysBonus = cls.calculateUniqueToysBonus(bonusType, uniqueToysLevel, config)
        return (atmosphereMultiplier, collectionsBonus, uniqueToysBonus)

    @classmethod
    def calculateBonusForType(cls, bonusType, atmosphereLevel, collectionLevels, toysLevel, config):
        bonus = 0.0
        multiplier = cls.getAtmosphereMultiplier(atmosphereLevel, config)
        for collectionName, collectionLevel in collectionLevels.iteritems():
            collectionFactor = cls.getCollectionFactor(bonusType, collectionName, collectionLevel, config)
            bonus += multiplier * collectionFactor

        bonus += multiplier * cls.calculateUniqueToysBonus(bonusType, toysLevel, config)
        return bonus

    @classmethod
    def getCollectionsBonus(cls, bonusType, collectionLevels, config):
        bonus = 0
        for collectionName, collectionLevel in collectionLevels.iteritems():
            collectionFactor = cls.getCollectionFactor(bonusType, collectionName, collectionLevel, config)
            bonus += collectionFactor

        return bonus

    @staticmethod
    def getAtmosphereMultiplier(atmosphereLevel, config):
        return config.getAtmosphereMultiplierForLevel(atmosphereLevel)

    @staticmethod
    def getCollectionFactor(bonusType, collectionName, collectionLevel, config):
        return config.getCollectionLevelSettingBonus(bonusType, collectionName, collectionLevel)

    @staticmethod
    def calculateUniqueToysBonus(bonusType, uniqueToysLevel, config):
        return config.getUniqueToysLevelSettingBonus(bonusType, uniqueToysLevel)

    @staticmethod
    def calculateCollectionLevels(collectionDistributions, config):
        return {collName:config.getCollectionLevel(collDistr) for collName, collDistr in collectionDistributions.iteritems()}

    @staticmethod
    def calculateUniqueToysLevel(collectionDistributions, config):
        return config.getUniqueToysLevel(collectionDistributions)
