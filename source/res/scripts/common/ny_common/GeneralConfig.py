# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GeneralConfig.py
from items.new_year import g_cache
from ny_common.settings import NYGeneralConsts

class GeneralConfig(object):

    def __init__(self, config):
        self._config = config

    def getAtmosphereLevelLimits(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_LEVEL_LIMITS)

    def getAtmPointsForFillingRankToy(self, toyID):
        toyDescr = g_cache.toys[toyID]
        config = self._getPointsConfigForFillingRankToy()
        return config[toyDescr.rank - 1]

    def _getPointsConfigForFillingRankToy(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_POINTS_PER_RANK, ())

    def calculateAtmosphereLevel(self, atmPoints):
        return self.calculateLevelByPoints(atmPoints)

    def getAtmosphereProgress(self, totalPoints):
        atmosphereLimits = self.getAtmosphereLevelLimits()
        for level, bound in enumerate(atmosphereLimits):
            if totalPoints < bound:
                prevBound = atmosphereLimits[level - 1]
                return (totalPoints - prevBound, bound - prevBound)

        finalDelta = atmosphereLimits[-1] - atmosphereLimits[-2]
        return (finalDelta, finalDelta)

    def calculateLevelByPoints(self, totalPoints):
        levelLimits = self.getAtmosphereLevelLimits()
        for level, bound in enumerate(levelLimits):
            if totalPoints < bound:
                return level

        return len(levelLimits)

    def getMaxLevelLimit(self):
        levelLimits = self.getAtmosphereLevelLimits()
        return levelLimits[-1] if levelLimits else 0

    def getMaxLevel(self):
        return len(self.getAtmosphereLevelLimits())
