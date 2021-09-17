# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_integration.py
from copy import copy
from collections import namedtuple
from constants import ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_NAMES
from items import vehicles
from soft_exception import SoftException
from debug_utils import LOG_WARNING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Union
CHECK_POINTS_LIMIT = False
NON_VEH_CD = 0
BpPointsSettings = namedtuple('BpPointsSettings', 'vehTypeCompDescr, isWinner, rank')

class BattlePassIntegrationInterface(object):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def getTeamSize(self):
        raise NotImplementedError()

    def validatePoints(self, season):
        raise NotImplementedError()

    def calculatePointsSettings(self, storage):
        raise NotImplementedError()


class BattlePassIntegrationRandom(BattlePassIntegrationInterface):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def __init__(self, teamSize, bonusTypeName):
        self.teamSize = teamSize
        self.bonusTypeName = bonusTypeName.upper()
        self.bonusType = ARENA_BONUS_TYPE_NAMES[self.bonusTypeName]

    def getTeamSize(self):
        return self.teamSize

    def validatePoints(self, season):
        capBonuses = season['capBonuses']
        points = season['points'][self.bonusType]
        pointsLimit = min(self._makePointsPerLevel(season['base']))
        maxCapBonus = max(capBonuses)
        winPoints = points['win']
        losePoints = points['lose']

        def checkPointsList(pointsList, pointsLimit, capBonusPoints, path):
            if len(pointsList) != self.getTeamSize():
                raise SoftException('BattlePass len(season/points/{}) {} != {}'.format(path, len(pointsList), self.getTeamSize()))
            if max(pointsList) + capBonusPoints > pointsLimit:
                msg = 'BattlePass season/points/{} max valid points + capBonus={} is {}'.format(path, maxCapBonus, pointsLimit)
                if CHECK_POINTS_LIMIT:
                    raise SoftException(msg)
                else:
                    LOG_WARNING(msg)

        checkPointsList(winPoints, pointsLimit, maxCapBonus, '{}/win'.format(self.bonusTypeName))
        checkPointsList(losePoints, pointsLimit, maxCapBonus, '{}/lose'.format(self.bonusTypeName))
        for key, value in points.iteritems():
            if key != 'win' and key != 'lose' and key != 'enabled':
                vehCD = key
                if not vehicles.g_list.isVehicleExistingByCD(vehCD):
                    raise SoftException('BattlePass wrong vehCD={}'.format(vehCD))
                vehLevel = vehicles.getVehicleType(vehCD).level
                winPoints = points[vehCD]['win']
                losePoints = points[vehCD]['lose']
                capBonusAtLevel = capBonuses[vehLevel - 1]
                checkPointsList(winPoints, pointsLimit, capBonusAtLevel, '{}/{}/win'.format(self.bonusTypeName, str(vehCD)))
                checkPointsList(losePoints, pointsLimit, capBonusAtLevel, '{}/{}/lose'.format(self.bonusTypeName, str(vehCD)))

    @staticmethod
    def _makePointsPerLevel(progression):
        result = copy(progression)
        for i in xrange(1, len(progression)):
            result[i] -= progression[i - 1]

        return result

    def calculatePointsSettings(self, storage):
        vehTypeCompDescr, results = storage['tempResults'].items()[0]
        rank = storage['avatarResults'].get('fareTeamXPPosition', 0)
        isWinner = 'winnerTeam' in results and 'team' in results and results['team'] == results['winnerTeam']
        return BpPointsSettings(vehTypeCompDescr, isWinner, rank)


class BattlePassIntegrationEpicBattle(BattlePassIntegrationRandom):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def calculatePointsSettings(self, storage):
        vehTypeCompDescr, isWinner, rank = super(BattlePassIntegrationEpicBattle, self).calculatePointsSettings(storage)
        return BpPointsSettings(NON_VEH_CD, isWinner, rank)

    def validatePoints(self, season):
        points = season['points'][self.bonusType]
        placesCount = self.teamSize
        bonusTypeName = self.bonusTypeName

        def checkPointsList(path):
            if len(points[path]) != placesCount:
                raise SoftException('BattlePass len(season/points/{}/{}) {} != {}'.format(bonusTypeName, path, points[path], placesCount))

        checkPointsList('win')
        checkPointsList('lose')


class BattlePassIntegrationBattleRoyale(BattlePassIntegrationRandom):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType', 'twinBonusType')

    def __init__(self, teamSize, bonusTypeName):
        super(BattlePassIntegrationBattleRoyale, self).__init__(teamSize, bonusTypeName)
        if self.bonusType == ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO:
            self.twinBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD
        else:
            self.twinBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO

    def validatePoints(self, season):
        if self.twinBonusType not in season['points']:
            raise SoftException('BattlePass bonus type {} must be present with {}'.format(self.twinBonusType, self.bonusType))
        points = season['points'][self.bonusType]
        if points['enabled'] != season['points'][self.twinBonusType]['enabled']:
            raise SoftException('BattlePass bonus type {} must has same enabled flag as {}'.format(self.twinBonusType, self.bonusType))

        def checkPointsList(path):
            if len(points[path]) != self.getTeamSize():
                raise SoftException('BattlePass len(season/points/{}/{}) {} != {}'.format(self.bonusType, path, points[path], self.getTeamSize()))

        checkPointsList('win')
        checkPointsList('lose')
        if not self._checkBattleRoyalePointsSequence(points, 3):
            raise SoftException('BattlePass royale points are wrong.Example: win: 10 0 0 0..., lose: 0 7 7 5 5 5 0 0 ..3 thresholds. Should decrease')

    def calculatePointsSettings(self, storage):
        vehTypeCompDescr, results = storage['tempResults'].items()[0]
        place = storage['avatarResults']['brPosInBattle']
        isWinner = place == 1
        return BpPointsSettings(vehTypeCompDescr, isWinner, place)

    @staticmethod
    def _checkBattleRoyalePointsSequence(points, thresholdTargetCount):
        if any((point != 0 for point in points['win'][1:])):
            return False
        mergedPoints = copy(points['lose'])
        mergedPoints[0] = points['win'][0]
        sortedMergedPoints = copy(mergedPoints)
        sortedMergedPoints.sort(reverse=True)
        if sortedMergedPoints != mergedPoints:
            return False
        pointsValues = set(sortedMergedPoints)
        pointsValues.discard(0)
        return False if len(pointsValues) != thresholdTargetCount else True


_BATTLEPASS_BY_GAMEMODE = {ARENA_BONUS_TYPE.REGULAR: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='REGULAR'),
 ARENA_BONUS_TYPE.RANKED: BattlePassIntegrationRandom(teamSize=10, bonusTypeName='RANKED'),
 ARENA_BONUS_TYPE.MAPBOX: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='MAPBOX'),
 ARENA_BONUS_TYPE.EPIC_BATTLE: BattlePassIntegrationEpicBattle(teamSize=30, bonusTypeName='EPIC_BATTLE'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: BattlePassIntegrationBattleRoyale(teamSize=20, bonusTypeName='BATTLE_ROYALE_SOLO'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: BattlePassIntegrationBattleRoyale(teamSize=10, bonusTypeName='BATTLE_ROYALE_SQUAD')}

def getBattlePassByGameMode(arenaBonusType):
    return _BATTLEPASS_BY_GAMEMODE.get(arenaBonusType)


def getAllIntergatedGameModes():
    return _BATTLEPASS_BY_GAMEMODE.keys()
