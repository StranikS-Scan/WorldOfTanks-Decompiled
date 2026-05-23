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
BpPointsSettings = namedtuple('BpPointsSettings', 'isWinner, rank')

class BattlePassIntegrationInterface(object):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def getTeamSize(self):
        raise NotImplementedError()

    def validatePoints(self, season):
        raise NotImplementedError()

    def calculatePointsSettings(self, avatarResults, battleResults):
        raise NotImplementedError()


class BattlePassIntegrationRandom(BattlePassIntegrationInterface):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def __init__(self, teamSize, bonusTypeName):
        self.teamSize = teamSize
        self.bonusTypeName = bonusTypeName.upper()
        self.bonusType = ARENA_BONUS_TYPE_NAMES[self.bonusTypeName]

    def getTeamSize(self):
        return self.teamSize

    @staticmethod
    def _isWinnerTeam(battleResults):
        return 'winnerTeam' in battleResults and 'team' in battleResults and battleResults['team'] == battleResults['winnerTeam']

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
            if key != 'win' and key != 'lose' and key != 'enabled':
                vehCD = key
                if not vehicles.g_list.isVehicleExistingByCD(vehCD):
                    raise SoftException('[BattlePass] wrong vehCD={}'.format(vehCD))
                winPoints = points[vehCD]['win']
                losePoints = points[vehCD]['lose']
                checkPointsList(winPoints, '{}/{}/win'.format(self.bonusTypeName, str(vehCD)))
                checkPointsList(losePoints, '{}/{}/lose'.format(self.bonusTypeName, str(vehCD)))

    def calculatePointsSettings(self, avatarResults, battleResults):
        rank = avatarResults.get('fareTeamXPPosition', 0)
        isWinner = self._isWinnerTeam(battleResults)
        return BpPointsSettings(isWinner, rank)


class BattlePassIntegrationEpicBattle(BattlePassIntegrationRandom):
    __slots__ = ('teamSize', 'bonusTypeName', 'bonusType')

    def calculatePointsSettings(self, avatarResults, battleResults):
        rank = avatarResults.get('fareTeamXPPosition', 0)
        isWinner = self._isWinnerTeam(battleResults)
        return BpPointsSettings(isWinner, rank)

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

    def calculatePointsSettings(self, avatarResults, battleResults):
        place = avatarResults['brPosInBattle']
        isWinner = place == 1
        return BpPointsSettings(isWinner, place)

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

    def calculatePointsSettings(self, avatarResults, battleResults):
        rank = avatarResults.get('fareTeamPrestigePointsPosition', 0)
        isWinner = self._isWinnerTeam(battleResults)
        return BpPointsSettings(isWinner, rank)


_GAMEMODE_WITH_NON_VEHICLE_DESC = {ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD}

def isGameModeWithNonVehicleDesc(arenaBonusType):
    return arenaBonusType in _GAMEMODE_WITH_NON_VEHICLE_DESC


_BATTLEPASS_BY_GAMEMODE = {ARENA_BONUS_TYPE.REGULAR: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='REGULAR'),
 ARENA_BONUS_TYPE.RANKED: BattlePassIntegrationRandom(teamSize=10, bonusTypeName='RANKED'),
 ARENA_BONUS_TYPE.COMP7: BattlePassIntegrationComp7(teamSize=7, bonusTypeName='COMP7'),
 ARENA_BONUS_TYPE.EPIC_BATTLE: BattlePassIntegrationEpicBattle(teamSize=30, bonusTypeName='EPIC_BATTLE'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: BattlePassIntegrationBattleRoyale(teamSize=15, bonusTypeName='BATTLE_ROYALE_SOLO'),
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: BattlePassIntegrationBattleRoyale(teamSize=10, bonusTypeName='BATTLE_ROYALE_SQUAD'),
 ARENA_BONUS_TYPE.SORTIE_2: BattlePassIntegrationRandom(teamSize=7, bonusTypeName='SORTIE_2'),
 ARENA_BONUS_TYPE.FORT_BATTLE_2: BattlePassIntegrationRandom(teamSize=15, bonusTypeName='FORT_BATTLE_2'),
 ARENA_BONUS_TYPE.VERSUS_AI: BattlePassIntegrationRandom(teamSize=12, bonusTypeName='VERSUS_AI')}

def getBattlePassByGameMode(arenaBonusType):
    return _BATTLEPASS_BY_GAMEMODE.get(arenaBonusType)


def getAllIntergatedGameModes():
    return _BATTLEPASS_BY_GAMEMODE.keys()
