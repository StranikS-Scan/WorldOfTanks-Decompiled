# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CelebrityConfig.py
from typing import Optional
from ny_common.settings import CelebrityConsts

class CelebrityConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getSimplificationCosts(self):
        return self._config.get(CelebrityConsts.SIMPLIFICATION_COSTS, {})

    def calculateSimplificationCost(self, fromLevel, toLevel):
        if toLevel > fromLevel:
            return None
        else:
            costs = self.getSimplificationCosts()
            resultCost = 0
            for level in xrange(fromLevel, toLevel, -1):
                resultCost += costs.get(level, 0)

            return resultCost

    def getQuestCount(self):
        return self._config.get(CelebrityConsts.QUEST_COUNT, 0)
