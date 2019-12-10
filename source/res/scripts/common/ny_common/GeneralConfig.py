# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GeneralConfig.py
from items.collectibles import ToyDescriptor
from items.new_year import g_cache
from ny_common.settings import NYGeneralConsts

class GeneralConfig(object):

    def __init__(self, config):
        self._config = config

    def getAtmospherePointsByToyRank(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_POINTS_BY_TOY_RANK)

    def getAtmosphereLevelLimits(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_LEVEL_LIMITS)

    def calculateTotalAtmospherePoints(self, toyIDs):
        sum = 0
        pointsByRank = self.getAtmospherePointsByToyRank()
        for toyID in toyIDs:
            toyDescr = g_cache.toys.get(toyID, None)
            if toyDescr is None or toyDescr.isMegaToy():
                continue
            sum += pointsByRank[toyDescr.rank - 1]

        return sum

    def calculateAtmospehereLevel(self, toyIDs):
        totalPoints = self.calculateTotalAtmospherePoints(toyIDs)
        return self.calculateLevelByPoints(totalPoints)

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
