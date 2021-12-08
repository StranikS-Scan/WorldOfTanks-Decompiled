# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GeneralConfig.py
from items.collectibles import ToyDescriptor
from items.new_year import g_cache
from ny_common.settings import NYGeneralConsts

class GeneralConfig(object):

    def __init__(self, config):
        self._config = config

    def getAtmosphereLevelLimits(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_LEVEL_LIMITS)

    def getAtmPointsForNewToy(self, toyID=None, toyDescr=None):
        config = self._getPointsConfigForToy(toyID, toyDescr)
        return config.get('newToy', 0)

    def getAtmPointsForFilling(self, toyID, toyUsage, slotUsage):
        config = self._getPointsConfigForToy(toyID=toyID)
        return config.get(toyUsage, {}).get(slotUsage, 0)

    def getAtmPointsConfigValue(self, isMega, toyUsage, slotUsage):
        isMegaStr = 'megaToys' if isMega else 'toys'
        config = self._config.get(NYGeneralConsts.ATMOSPHERE_POINTS, {}).get(isMegaStr, {})
        return config.get(toyUsage, {}).get(slotUsage, 0)

    def _getPointsConfigForToy(self, toyID=None, toyDescr=None):
        if toyDescr is None:
            toyDescr = g_cache.toys.get(toyID, None)
        key = 'megaToys' if toyDescr.isMegaToy() else 'toys'
        return self._config.get(NYGeneralConsts.ATMOSPHERE_POINTS, {}).get(key)

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
