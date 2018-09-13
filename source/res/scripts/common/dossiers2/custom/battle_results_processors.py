# Embedded file name: scripts/common/dossiers2/custom/battle_results_processors.py
import time
from constants import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS, DESTR_CODES_BY_TAGS
from dossiers2.custom import records
from dossiers2.custom.cache import getCache
from dossiers2.custom.utils import isVehicleSPG, getInBattleSeriesIndex
_divisionToRecordNames = {'MIDDLE': ('middleBattlesCount', 'fortResourceInMiddle'),
 'CHAMPION': ('championBattlesCount', 'fortResourceInChampion'),
 'ABSOLUTE': ('absoluteBattlesCount', 'fortResourceInAbsolute')}

def updateFortifiedRegionDossier(dossierDescr, divisionName, isWinner, fortResource, isCommander):
    if divisionName not in _divisionToRecordNames:
        raise Exception, 'Unknown sortie division'
    counterRecordName, resourceRecordName = _divisionToRecordNames[divisionName]
    sortieBlock = dossierDescr['fortSorties']
    sortieBlock[resourceRecordName] += fortResource
    if not isCommander:
        return
    sortieBlock['battlesCount'] += 1
    if isWinner:
        sortieBlock['wins'] += 1
    else:
        sortieBlock['losses'] += 1
    sortieBlock[counterRecordName] += 1


def updateVehicleDossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr):
    __updateDossierCommonPart(dossierDescr, battleResults, dossierXP)
    __updateVehicleDossierImpl(vehTypeCompDescr, dossierDescr, battleResults)


def updateAccountDossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr):
    maxValuesChanged, frags8p = __updateDossierCommonPart(dossierDescr, battleResults, dossierXP)
    __updateAccountDossierImpl(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr, maxValuesChanged, frags8p)


def updateTankmanDossier(dossierDescr, battleResults):
    __updateTankmanDossierImpl(dossierDescr, battleResults)


def __updateDossierCommonPart(dossierDescr, results, dossierXP):
    bonusCaps = BONUS_CAPS.get(results['bonusType'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_TOTAL):
        __updateTotalValues(dossierDescr, results)
    frags8p = 0
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_KILL_LIST):
        frags8p = __processKillList(dossierDescr, results['kill_list'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_15X15):
        __updateAggregatedValues(dossierDescr.expand('a15x15'), dossierDescr.expand('a15x15_2'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_7X7):
        __updateAggregatedValues(dossierDescr.expand('a7x7'), dossierDescr.expand('a7x7'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_COMPANY):
        __updateBaseStatistics(dossierDescr.expand('company'), dossierDescr.expand('company2'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_CLAN):
        __updateBaseStatistics(dossierDescr.expand('clan'), dossierDescr.expand('clan2'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_HISTORICAL):
        __updateAggregatedValues(dossierDescr.expand('historical'), dossierDescr.expand('historical'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_SORTIE):
        __updateAggregatedValues(dossierDescr.expand('fortSorties'), dossierDescr.expand('fortSorties'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS):
        for recordDBID in results['achievements'] + results['protoAchievements']:
            __processArenaAchievement(dossierDescr, recordDBID)

    maxValuesChanged = []
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX15X15):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max15x15'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX7X7):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max7x7'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXHISTORICAL):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxHistorical'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXSORTIE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFortSorties'), results, dossierXP)
    return (maxValuesChanged, frags8p)


def __updateTotalValues(dossierDescr, results):
    total = dossierDescr.expand('total')
    total['battleLifeTime'] += results['lifeTime']
    total['lastBattleTime'] = int(time.time())
    total['treesCut'] += results['destroyedObjects'].get(DESTR_CODES_BY_TAGS['tree'], 0)
    total['mileage'] += results['mileage']


def __processKillList(dossierDescr, killList):
    if not killList:
        return 0
    cache = getCache()
    vehicles8p = cache['vehicles8+']
    vehiclesByTag = cache['vehiclesByTag']
    frags8p = 0
    killsByTag = {}
    vehTypeFrags = dossierDescr['vehTypeFrags']
    for kill in killList:
        vehTypeCompDescr = kill[1]
        vehTypeFrags[vehTypeCompDescr] = min(vehTypeFrags.get(vehTypeCompDescr, 0) + 1, 60001)
        if vehTypeCompDescr in vehicles8p:
            frags8p += 1
        for tag, record in (('beast', 'fragsBeast'), ('sinai', 'fragsSinai'), ('patton', 'fragsPatton')):
            if vehTypeCompDescr in vehiclesByTag[tag]:
                killsByTag[record] = killsByTag.get(record, 0) + 1

    if killsByTag:
        achievements = dossierDescr['achievements']
        for record, frags in killsByTag.iteritems():
            achievements[record] += frags

    return frags8p


def __updateAggregatedValues(block, block2, results, dossierXP, frags8p):
    __updateBaseStatistics(block, block2, results, dossierXP)
    if results['killerID'] == 0 and results['winnerTeam'] == results['team']:
        block['winAndSurvived'] += 1
    if frags8p != 0:
        block['frags8p'] += frags8p


def __updateBaseStatistics(block, block2, results, dossierXP):
    block['battlesCount'] += 1
    if dossierXP != 0:
        block['xp'] += dossierXP
        block2['originalXP'] += results['originalXP']
    if results['winnerTeam'] == results['team']:
        block['wins'] += 1
    elif results['winnerTeam'] == 3 - results['team']:
        block['losses'] += 1
    if results['killerID'] == 0:
        block['survivedBattles'] += 1
    for record in ('shots', 'directHits', 'spotted', 'damageDealt', 'damageReceived', 'capturePoints'):
        if bool(results[record]):
            block[record] += results[record]

    droppedCapturePoints = min(results['droppedCapturePoints'], 100)
    if droppedCapturePoints != 0:
        block['droppedCapturePoints'] += droppedCapturePoints
    kills = results['kills']
    if kills:
        block['frags'] += kills
    for record in ('damageAssistedTrack', 'damageAssistedRadio', 'directHitsReceived', 'noDamageDirectHitsReceived', 'piercingsReceived', 'explosionHitsReceived', 'explosionHits', 'piercings', 'potentialDamageReceived', 'damageBlockedByArmor'):
        if bool(results[record]):
            block2[record] += results[record]


def __processArenaAchievement(dossierDescr, recordDBID):
    block, record = records.DB_ID_TO_RECORD[recordDBID]
    if not dossierDescr.isBlockInLayout(block):
        return
    blockDescr = dossierDescr[block]
    if record not in blockDescr:
        return
    blockDescr[record] += 1


def __updateMaxValues(block, results, dossierXP):
    maxValuesChanged = []
    if dossierXP != 0 and dossierXP >= block['maxXP']:
        block['maxXP'] = dossierXP
        maxValuesChanged.append('maxXPVehicle')
    kills = results['kills']
    if kills > 0 and kills >= block['maxFrags']:
        block['maxFrags'] = kills
        maxValuesChanged.append('maxFragsVehicle')
    damageDealt = results['damageDealt']
    if damageDealt > 0 and damageDealt >= block['maxDamage']:
        block['maxDamage'] = damageDealt
        maxValuesChanged.append('maxDamageVehicle')
    return maxValuesChanged


def __updateVehicleDossierImpl(vehTypeCompDescr, dossierDescr, results):
    if bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_7X7):
        _updatePerBattleSeries(dossierDescr['achievements7x7'], 'tacticalBreakthroughSeries', results['winnerTeam'] == results['team'])
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        return
    achievements = dossierDescr['achievements']
    if achievements['markOfMastery'] < results['markOfMastery']:
        achievements['markOfMastery'] = results['markOfMastery']
    damageRating = int(results['damageRating'] * 100)
    achievements['damageRating'] = damageRating
    achievements['movingAvgDamage'] = results['movingAvgDamage']
    if achievements['marksOnGun'] < results['marksOnGun']:
        achievements['marksOnGun'] = results['marksOnGun']
    isSPG = isVehicleSPG(vehTypeCompDescr)
    _updatePerBattleSeries(achievements, 'invincibleSeries', results['killerID'] == 0 and results['damageReceived'] == 0 and not isSPG)
    _updatePerBattleSeries(achievements, 'diehardSeries', results['killerID'] == 0 and not isSPG)
    _updateInBattleSeries(achievements, 'sniper', results)
    _updateInBattleSeries(achievements, 'killing', results)
    _updateInBattleSeries(achievements, 'piercing', results)


def _updatePerBattleSeries(achievements, achieveName, isNotInterrupted):
    if isNotInterrupted:
        achievements[achieveName] += 1
    else:
        achievements[achieveName] = 0


def _updateInBattleSeries(achievements, seriesName, results):
    seriesIdx = getInBattleSeriesIndex(seriesName)
    recordName = seriesName + 'Series'
    series = results['series'].get(seriesIdx, [])
    if series:
        achievements[recordName] = achievements[recordName] + series[0]
    for runLength in series[1:]:
        achievements[recordName] = runLength


def __updateAccountDossierImpl(dossierDescr, results, dossierXP, vehTypeCompDescr, vehDossierDescr, maxValuesChanged, frags8p):
    if not vehDossierDescr is not None:
        raise AssertionError
        bonusCaps = BONUS_CAPS.get(results['bonusType'])
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_15X15):
            a15x15Cut = dossierDescr['a15x15Cut']
            vehA15x15 = vehDossierDescr['a15x15']
            a15x15Cut[vehTypeCompDescr] = (vehA15x15['battlesCount'],
             vehA15x15['wins'],
             vehDossierDescr['achievements']['markOfMastery'],
             vehA15x15['xp'])
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_7X7):
            a7x7Cut = dossierDescr['a7x7Cut']
            vehA7x7 = vehDossierDescr['a7x7']
            a7x7Cut[vehTypeCompDescr] = (vehA7x7['battlesCount'],
             vehA7x7['wins'],
             vehA7x7['xp'],
             vehA7x7['originalXP'],
             vehA7x7['damageDealt'],
             vehA7x7['damageAssistedRadio'],
             vehA7x7['damageAssistedTrack'])
            __updateCapturePointsWithBaseCapture(dossierDescr, results)
            __updateDefencePoints(dossierDescr, results)
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_HISTORICAL):
            historicalCut = dossierDescr['historicalCut']
            vehHistorical = vehDossierDescr['historical']
            historicalCut[vehTypeCompDescr] = (vehHistorical['battlesCount'], vehHistorical['wins'], vehHistorical['xp'])
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_SORTIE):
            sortieCut = dossierDescr['fortSortiesCut']
            vehSortie = vehDossierDescr['fortSorties']
            sortieCut[vehTypeCompDescr] = (vehSortie['battlesCount'], vehSortie['wins'], vehSortie['xp'])
            fortResource = results['fortResource']
            for blockName in ('fortMisc', 'fortMiscInClan'):
                miscBlock = dossierDescr[blockName]
                miscBlock['fortResourceInSorties'] += fortResource
                if fortResource > miscBlock['maxFortResourceInSorties']:
                    miscBlock['maxFortResourceInSorties'] = fortResource

        if bool(bonusCaps & BONUS_CAPS.DOSSIER_SORTIE):
            __updateAggregatedValues(dossierDescr.expand('fortSortiesInClan'), dossierDescr.expand('fortSortiesInClan'), results, dossierXP, frags8p)
        bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS) and __updateAccountRecords(bonusCaps, dossierDescr, vehDossierDescr)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX15X15):
        for record in maxValuesChanged:
            dossierDescr['max15x15'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX7X7):
        for record in maxValuesChanged:
            dossierDescr['max7x7'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXHISTORICAL):
        for record in maxValuesChanged:
            dossierDescr['maxHistorical'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXSORTIE):
        for record in __updateMaxValues(dossierDescr.expand('maxFortSortiesInClan'), results, dossierXP):
            dossierDescr['maxFortSortiesInClan'][record] = vehTypeCompDescr

        for record in maxValuesChanged:
            dossierDescr['maxFortSorties'][record] = vehTypeCompDescr

    return


def __updateTankmanDossierImpl(dossierDescr, results):
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_TOTAL):
        return
    dossierDescr['total']['battlesCount'] += 1
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        return
    for recordDBID in results['achievements']:
        __processArenaAchievement(dossierDescr, recordDBID)


def __updateAccountRecords(bonusCaps, dossierDescr, vehDossierDescr):
    blocks = __chooseAchievementBlock(bonusCaps)
    for targetBlock, recordsNames in blocks:
        if not recordsNames:
            continue
        achievements = dossierDescr[targetBlock]
        vehAchievements = vehDossierDescr[targetBlock]
        for recordName in recordsNames:
            if vehAchievements[recordName] > achievements[recordName]:
                achievements[recordName] = vehAchievements[recordName]


def __chooseAchievementBlock(bonusCaps):
    res = []
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        targetBlock = 'achievements'
        names = ('maxInvincibleSeries', 'maxDiehardSeries', 'maxSniperSeries', 'maxKillingSeries', 'maxPiercingSeries')
        res.append((targetBlock, names))
    elif bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_7X7):
        targetBlock = 'achievements7x7'
        names = ('maxTacticalBreakthroughSeries',)
        res.append((targetBlock, names))
        targetBlock = 'singleAchievements'
        names = ('tacticalBreakthrough',)
        res.append((targetBlock, names))
    elif bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_HISTORICAL):
        res.append(('historicalAchievements', ()))
    elif bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_SORTIE):
        res.append(('fortAchievements', ()))
    else:
        raise Exception, 'Unknown achievement mode'
    return res


def __updateCapturePointsWithBaseCapture(dossierDescr, results):
    if results['isEnemyBaseCaptured'] and results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['infiltrator'] += results['capturePoints']


def __updateDefencePoints(dossierDescr, results):
    if results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['sentinel'] += results['droppedCapturePoints']
