# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/SettingBonus.py
from itertools import imap
from operator import mul
from typing import List, Dict, Tuple
from ny_common.settings import SettingBonusConsts

class SettingBonusDefaults(object):
    DEFAULT_ATMOSPHERE_MULTIPLIER = 1.0
    DEFAULT_COLLECTION_BONUS = 0.0
    DEFAULT_MEGA_TOY_BONUS = 0.0


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

    def getMegaToyBonus(self, bonusType):
        return self._getBonusesByType(bonusType).get(SettingBonusConsts.MEGA_TOY_BONUS, SettingBonusDefaults.DEFAULT_MEGA_TOY_BONUS)

    def getCollectionLevelsRating(self):
        return self._config.get(SettingBonusConsts.COLLECTION_LEVELS_RATING, ())

    def getCollectionLevel(self, collectionDistribution):
        levelsRating = self.getCollectionLevelsRating()
        collectionRating = self._calculateCollectionRating(collectionDistribution)
        return self._calculateLevelByRating(levelsRating, collectionRating)

    def getCollectionLevelSettingBonus(self, bonusType, collectionName, collectionLevel):
        collectionBonuses = self.getCollectionBonuses(bonusType, collectionName)
        return collectionBonuses[collectionLevel]

    def getAtmosphereMultiplierForLevel(self, level):
        atmosphereMultipliers = self.getAtmosphereMultipliers()
        return atmosphereMultipliers[level - 1]

    def _getBonusesByType(self, bonusType):
        return self._config.get(SettingBonusConsts.BATTLE_BONUSES, {}).get(bonusType, {})

    def _calculateCollectionRating(self, collectionDistribution):
        toyRatingByRank = self.getToyRatingsByRank()
        return sum(imap(mul, toyRatingByRank, collectionDistribution))

    @staticmethod
    def _calculateLevelByRating(levelsRating, collectionRating):
        for level, bound in enumerate(levelsRating):
            if collectionRating < bound:
                return level - 1

        return len(levelsRating) - 1


class SettingBonus(object):
    PRECISION = 3

    @staticmethod
    def getFormulasInfo(atmosphereLevel, collectionDistributions, megaToysCount, config):
        bonusTypes = config.getBonusTypes()
        collectionLevels = SettingBonus.calculateCollectionLevels(collectionDistributions, config)
        formulas = {}
        for bonusType in bonusTypes:
            formulas[bonusType] = SettingBonus.getFormulaParams(bonusType, atmosphereLevel, collectionLevels, megaToysCount, config)

        return formulas

    @staticmethod
    def calculateBonusByFormulaInfo(formulaInfo):
        atmosphereMultiplier, collectionsBonus, megaToysBonus = formulaInfo
        return round(atmosphereMultiplier * collectionsBonus + megaToysBonus, SettingBonus.PRECISION)

    @staticmethod
    def getFormulaParams(bonusType, atmosphereLevel, collectionLevels, megaToysCount, config):
        atmosphereMultiplier = SettingBonus.getAtmosphereMultiplier(atmosphereLevel, config)
        collectionsBonus = SettingBonus.getCollectionsBonus(bonusType, collectionLevels, config)
        megaToysBonus = SettingBonus.calculateMegaToysBonus(bonusType, megaToysCount, config)
        return (atmosphereMultiplier, collectionsBonus, megaToysBonus)

    @staticmethod
    def calculateBonusForType(bonusType, atmosphereLevel, collectionLevels, megaToysCount, config):
        bonus = 0.0
        multiplier = SettingBonus.getAtmosphereMultiplier(atmosphereLevel, config)
        for collectionName, collectionLevel in collectionLevels.iteritems():
            collectionFactor = SettingBonus.getCollectionFactor(bonusType, collectionName, collectionLevel, config)
            bonus += multiplier * collectionFactor

        bonus += SettingBonus.calculateMegaToysBonus(bonusType, megaToysCount, config)
        return bonus

    @staticmethod
    def getCollectionsBonus(bonusType, collectionLevels, config):
        bonus = 0
        for collectionName, collectionLevel in collectionLevels.iteritems():
            collectionFactor = SettingBonus.getCollectionFactor(bonusType, collectionName, collectionLevel, config)
            bonus += collectionFactor

        return bonus

    @staticmethod
    def getAtmosphereMultiplier(atmosphereLevel, config):
        return config.getAtmosphereMultiplierForLevel(atmosphereLevel)

    @staticmethod
    def getCollectionFactor(bonusType, collectionName, collectionLevel, config):
        return config.getCollectionLevelSettingBonus(bonusType, collectionName, collectionLevel)

    @staticmethod
    def calculateMegaToysBonus(bonusType, toysCount, config):
        megaToyBonus = config.getMegaToyBonus(bonusType)
        return toysCount * megaToyBonus

    @staticmethod
    def calculateCollectionLevels(collectionDistributions, config):
        levels = {}
        for collName, collDistr in collectionDistributions.iteritems():
            collLevel = config.getCollectionLevel(collDistr)
            levels[collName] = collLevel

        return levels
