# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_integration.py
from copy import copy
from collections import namedtuple
from constants import ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_NAMES
from items import vehicles
from soft_exception import SoftException
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, Union
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
        points = season['points'][self.bonusType]
        winPoints = points['win']
        losePoints = points['lose']

        def checkPointsList(pointsList, path):
            if len(pointsList) != self.getTeamSize():
                raise SoftException('[BattlePass] len(season/points/{}) {} != {}'.format(path, len(pointsList), self.getTeamSize()))

        checkPointsList(winPoints, '{}/win'.format(self.bonusTypeName))
        checkPointsList(losePoints, '{}/lose'.format(self.bonusTypeName))
        for key, value in points.iteritems():
            if key not in ('win', 'lose', 'enabled', 'visible'):
                vehCD = key
                if not vehicles.g_list.isVehicleExistingByCD(vehCD):
                    raise SoftException('[BattlePass] wrong vehCD={}'.format(vehCD))
                winPoints = points[vehCD]['win']
                losePoints = points[vehCD]['lose']
                checkPointsList(winPoints, '{}/{}/win'.format(self.bonusTypeName, str(vehCD)))
                checkPointsList(losePoints, '{}/{}/lose'.format(self.bonusTypeName, str(vehCD)))

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
                raise SoftException('[BattlePass] len(season/points/{}/{}) {} != {}'.format(bonusTypeName, path, points[path], placesCount))

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
            raise SoftException('[BattlePass] bonus type {} must be present with {}'.format(self.twinBonusType, self.bonusType))
        points = season['points'][self.bonusType]
        if points['enabled'] != season['points'][self.twinBonusType]['enabled']:
            raise SoftException('[BattlePass] bonus type {} must has same enabled flag as {}'.format(self.twinBonusType, self.bonusType))

        def checkPointsList(path):
            if len(points[path]) != self.getTeamSize():
                raise SoftException('[BattlePass] len(season/points/{}/{}) {} != {}'.format(self.bonusType, path, points[path], self.getTeamSize()))

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
        mergedPoints = list(points['lose'])
        mergedPoints[0] = points['win'][0]
        sortedMergedPoints = copy(mergedPoints)
        sortedMergedPoints.sort(reverse=True)
        if sortedMergedPoints != mergedPoints:
            return False
        pointsValues = set(sortedMergedPoints)
        pointsValues.discard(0)
        return False if len(pointsValues) != thresholdTargetCount else True


class BattlePassIntegrationComp7(BattlePassIntegrationRandom):

    def calculatePointsSettings(self, storage):
        vehTypeCompDescr, results = storage['tempResults'].items()[0]
        rank = storage['avatarResults'].get('fareTeamPrestigePointsPosition', 0)
        isWinner = 'winnerTeam' in results and 'team' in results and results['team'] == results['winnerTeam']
        return BpPointsSettings(vehTypeCompDescr, isWinner, rank)


_BATTLEPASS_BY_GAMEMODE = {ARENA_BONUS_TYPE.REGULAR: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='REGULAR'),
 ARENA_BONUS_TYPE.RANKED: BattlePassIntegrationRandom(teamSize=10, bonusTypeName='RANKED'),
 ARENA_BONUS_TYPE.MAPBOX: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='MAPBOX'),
 ARENA_BONUS_TYPE.COMP7: BattlePassIntegrationComp7(teamSize=7, bonusTypeName='COMP7'),
 ARENA_BONUS_TYPE.WINBACK: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='WINBACK'),
 ARENA_BONUS_TYPE.RANDOM_NP2: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='RANDOM_NP2'),
 ARENA_BONUS_TYPE.EPIC_BATTLE: BattlePassIntegrationEpicBattle(teamSize=30, bonusTypeName='EPIC_BATTLE'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: BattlePassIntegrationBattleRoyale(teamSize=15, bonusTypeName='BATTLE_ROYALE_SOLO'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: BattlePassIntegrationBattleRoyale(teamSize=10, bonusTypeName='BATTLE_ROYALE_SQUAD')}

def getBattlePassByGameMode(arenaBonusType):
    return _BATTLEPASS_BY_GAMEMODE.get(arenaBonusType)


def getAllIntergatedGameModes():
    return _BATTLEPASS_BY_GAMEMODE.keys()
