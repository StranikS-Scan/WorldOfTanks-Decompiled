# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/SnowGirlConfig.py
from typing import Tuple, Optional
from CraftProbabilities import CraftProbabilitiesConfig
from items.components.ny_constants import MAX_TALISMAN_STAGE
from ny_common.settings import SnowGirlConsts

class SnowGirlConfig(CraftProbabilitiesConfig):

    def __init__(self, snowGirlConfig, craftProbabilitiesConfig=None):
        super(SnowGirlConfig, self).__init__(craftProbabilitiesConfig)
        self._snowGirlConfig = snowGirlConfig
        self._sequenceStage = 0

    @property
    def sequenceStage(self):
        return self._sequenceStage

    @sequenceStage.setter
    def sequenceStage(self, stage):
        self._sequenceStage = stage

    def getProbabilitiesForRanks(self):
        additionalProbabilities = self._snowGirlConfig.get(SnowGirlConsts.ADDITIONAL_PROBABILITIES, {})
        rankProbabilities = additionalProbabilities.get(SnowGirlConsts.RANK_PROBABILITIES, {})
        defaultProbabilities = super(SnowGirlConfig, self).getProbabilitiesForRanks()
        return rankProbabilities.get(self._sequenceStage, defaultProbabilities)

    def getValue(self, valueName):
        return self._snowGirlConfig.get(valueName, [])

    def getCostForMovingToNextStage(self, currentStage=None):
        return self._getValueForStageByName(SnowGirlConsts.SEQUENCE_STAGE_COST, currentStage)

    def getToyLimitForCurrentStage(self, currentStage=None):
        return self._getValueForStageByName(SnowGirlConsts.TOY_LIMITS_PER_STAGE, currentStage)

    def validateAndGetLevelUp(self, currentStage, receivedToys, nextStage):
        if nextStage <= currentStage:
            return (False, None, 'Next stage should be larger than current stage')
        elif nextStage > MAX_TALISMAN_STAGE:
            return (False, None, 'Next stage more than MAX_TALISMAN_STAGE')
        else:
            result, cost, reason = self._getLevelUpToNextStage(currentStage, receivedToys)
            if not result:
                return (result, cost, reason)
            sequenceStageCost = self.getValue(SnowGirlConsts.SEQUENCE_STAGE_COST)
            if nextStage > len(sequenceStageCost):
                return (False, None, 'Next stage more than length of SEQUENCE_STAGE_COST')
            resultCost = cost + sum(sequenceStageCost[currentStage + 1:nextStage])
            return (True, resultCost, '')

    def getTotalReceivedToys(self, currentStage, receivedToys):
        return sum(self.getValue(SnowGirlConsts.TOY_LIMITS_PER_STAGE)[:currentStage]) + receivedToys

    def getReceivedToysForMaxLevel(self):
        return self.getTotalReceivedToys(MAX_TALISMAN_STAGE, 0)

    def _getLevelUpToNextStage(self, currentStage, receivedToys=0):
        toyFragments = self.getCostForMovingToNextStage(currentStage)
        toyLimit = self.getToyLimitForCurrentStage(currentStage)
        if toyFragments is None:
            return (False, None, 'No cost for changing to next stage')
        else:
            return (False, None, 'No toy limit for current stage') if toyLimit is None else (True, toyFragments * (toyLimit - receivedToys) / toyLimit, '')

    def _getValueForStageByName(self, valueName, currentStage=None):
        sequenceStage = self._sequenceStage if currentStage is None else currentStage
        values = self._snowGirlConfig.get(valueName, [])
        return values[sequenceStage] if sequenceStage < len(values) else None
