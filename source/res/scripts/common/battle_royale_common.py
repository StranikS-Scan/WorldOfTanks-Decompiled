# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_royale_common.py
from typing import Tuple, List, Dict
from debug_utils import LOG_DEBUG_DEV
AccBRTitleAndPointsType = Tuple[int, int]
BR_BATTLE_QUEST_BASE = 'br_battle_result'
BR_SOLO_QUEST_FOR_POSITION_TEMPLATE = BR_BATTLE_QUEST_BASE + '_solo_{position}'
BR_SQUAD_QUEST_FOR_POSITION_TEMPLATE = BR_BATTLE_QUEST_BASE + '_squad_{position}'
BR_TOKEN_FOR_TITLE = 'token:br:title:{title}'

class BattleRoyaleEventProgressionConfig(object):

    def __init__(self, gameParams):
        progression_config = gameParams['battle_royale_config']['eventProgression']
        LOG_DEBUG_DEV('Battle Royale progression config', progression_config)
        self._pointsForTitle = progression_config['brPointsByTitle']
        self._unburnableTitles = progression_config.get('unburnableTitles', [0])

    @property
    def unburnableTitles(self):
        return self._unburnableTitles

    @property
    def pointsForTitle(self):
        return self._pointsForTitle

    @property
    def maxAccTitle(self):
        return len(self.pointsForTitle)


class BattleRoyaleTitlesCalculationLogic(object):

    def __init__(self, currentTitleAndPoints, logID):
        self._titleAndPoints = currentTitleAndPoints
        self._logID = logID

    def calculateNewAccTitle(self, pointsDelta, gameParams, ignoreUnburnableTitles=False):
        config = BattleRoyaleEventProgressionConfig(gameParams)
        if pointsDelta > 0:
            result = self._increaseTitle(pointsDelta, config)
        elif pointsDelta < 0:
            result = self._decreaseTitle(pointsDelta, config, not ignoreUnburnableTitles)
        else:
            result = self._titleAndPoints
        return result

    def _increaseTitle(self, pointsDelta, config):
        accTitle, accPoints = self._titleAndPoints
        maxAccTitle = config.maxAccTitle
        while pointsDelta > 0:
            if accTitle < maxAccTitle:
                titlePoints = config.pointsForTitle[accTitle]
                points = min(pointsDelta, titlePoints - accPoints)
                accPoints += points
                if accPoints == titlePoints:
                    accTitle += 1
                    accPoints = 0
            else:
                LOG_DEBUG_DEV('BattleRoyale. Player has achieved last title, progression has stopped.')
                points = pointsDelta
            pointsDelta -= points

        return (accTitle, accPoints)

    def _decreaseTitle(self, pointsDelta, config, checkUnburnableTitles):
        accBRTitle, accPoints = self._titleAndPoints
        pointsDelta = abs(pointsDelta)
        while pointsDelta > 0:
            if accPoints > 0:
                points = min(pointsDelta, accPoints)
                accPoints -= points
            elif accBRTitle > 0:
                if checkUnburnableTitles and accBRTitle in config.unburnableTitles:
                    break
                points = 1
                accBRTitle -= 1
                accPoints = config.pointsForTitle[accBRTitle] - 1
            else:
                break
            pointsDelta -= points

        return (accBRTitle, accPoints)
