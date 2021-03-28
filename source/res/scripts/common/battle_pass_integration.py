# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_integration.py
from copy import copy
from functools import partial
from constants import ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_NAMES
from items import vehicles
from soft_exception import SoftException
from debug_utils import LOG_WARNING, LOG_DEBUG_DEV
CHECK_POINTS_LIMIT = True

def _makePointsPerLevel(progression):
    result = copy(progression)
    for i in xrange(1, len(progression)):
        result[i] -= progression[i - 1]

    return result


def validatePoints(season, bonusTypeName='regular'):
    TEAM_SIZE_REGULAR = 15
    capBonuses = season['capBonuses']
    bonusType = ARENA_BONUS_TYPE_NAMES.get(bonusTypeName.upper())
    points = season['points'][bonusType]
    pointsLimit = min(_makePointsPerLevel(season['base']))
    maxCapBonus = max(capBonuses)
    winPoints = points['win']
    losePoints = points['lose']

    def checkPointsList(pointsList, pointsLimit, capBonusPoints, path):
        if len(pointsList) != TEAM_SIZE_REGULAR:
            raise SoftException('BattlePass len(season/points/{}) {} != {}'.format(path, len(pointsList), TEAM_SIZE_REGULAR))
        if max(pointsList) + capBonusPoints > pointsLimit:
            msg = 'BattlePass season/points/{} max valid points + capBonus={} is {}'.format(path, maxCapBonus, pointsLimit)
            if CHECK_POINTS_LIMIT:
                raise SoftException(msg)
            else:
                LOG_WARNING(msg)

    checkPointsList(winPoints, pointsLimit, maxCapBonus, '{}/win'.format(bonusTypeName))
    checkPointsList(losePoints, pointsLimit, maxCapBonus, '{}/lose'.format(bonusTypeName))
    for key, value in points.iteritems():
        if key != 'win' and key != 'lose' and key != 'enabled':
            vehCD = key
            if not vehicles.g_list.isVehicleExistingByCD(vehCD):
                raise SoftException('BattlePass wrong vehCD={}'.format(vehCD))
            vehLevel = vehicles.getVehicleType(vehCD).level
            winPoints = points[vehCD]['win']
            losePoints = points[vehCD]['lose']
            capBonusAtLevel = capBonuses[vehLevel - 1]
            checkPointsList(winPoints, pointsLimit, capBonusAtLevel, '{}/{}/win'.format(bonusTypeName, str(vehCD)))
            checkPointsList(losePoints, pointsLimit, capBonusAtLevel, '{}/{}/lose'.format(bonusTypeName, str(vehCD)))


def calculatePointsSettingsRegular(storage):
    vehTypeCompDescr, results = storage['tempResults'].items()[0]
    rank = storage['avatarResults'].get('fareTeamXPPosition', 0)
    isWinner = 'winnerTeam' in results and 'team' in results and results['team'] == results['winnerTeam']
    return (vehTypeCompDescr, isWinner, rank)


def calculatePointsSettingsBattleRoyale(storage):
    vehTypeCompDescr, results = storage['tempResults'].items()[0]
    place = storage['avatarResults']['brPosInBattle']
    isWinner = place == 1
    LOG_DEBUG_DEV('calculatePointsSettingsBattleRoyale', vehTypeCompDescr, isWinner, place)
    return (vehTypeCompDescr, isWinner, place)


def checkBattleRoyalePointsSequence(points, thresholdTargetCount):
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


def validatePointsBattleRoyale(bonusType, placesCount, season):
    if bonusType == ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO:
        twinBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD
    else:
        twinBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
    if twinBonusType not in season['points']:
        raise SoftException('BattlePass bonus type {} must be present with {}'.format(twinBonusType, bonusType))
    points = season['points'][bonusType]
    if points['enabled'] != season['points'][twinBonusType]['enabled']:
        raise SoftException('BattlePass bonus type {} must has same enabled flag as {}'.format(twinBonusType, bonusType))

    def checkPointsList(path):
        if len(points[path]) != placesCount:
            raise SoftException('BattlePass len(season/points/{}/{}) {} != {}'.format(bonusType, path, points[path], placesCount))

    checkPointsList('win')
    checkPointsList('lose')
    if not checkBattleRoyalePointsSequence(points, 3):
        raise SoftException('BattlePass royale points are wrong.Example: win: 10 0 0 0..., lose: 0 7 7 5 5 5 0 0 ..3 thresholds. Should decrease')


def validatePointsRanked(season):
    validatePoints(season, bonusTypeName='ranked')


BattlePassByGameMode = {ARENA_BONUS_TYPE.REGULAR: {'validatePoints': validatePoints,
                            'calculatePointsSettings': calculatePointsSettingsRegular,
                            'maxRanks': 15},
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO: {'validatePoints': partial(validatePointsBattleRoyale, ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, 20),
                                       'calculatePointsSettings': calculatePointsSettingsBattleRoyale,
                                       'maxRanks': 20},
 ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD: {'validatePoints': partial(validatePointsBattleRoyale, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD, 10),
                                        'calculatePointsSettings': calculatePointsSettingsBattleRoyale,
                                        'maxRanks': 10},
 ARENA_BONUS_TYPE.RANKED: {'validatePoints': validatePointsRanked,
                           'calculatePointsSettings': calculatePointsSettingsRegular,
                           'maxRanks': 15}}
