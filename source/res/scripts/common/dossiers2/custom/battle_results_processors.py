# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/battle_results_processors.py
import time
from constants import DESTR_CODES_BY_TAGS, GLOBAL_MAP_DIVISION, DOSSIER_TYPE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from battle_results_helpers import determineWinnerTeam
from debug_utils import LOG_DEBUG_DEV
from dossiers2.custom import records
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.custom.cache import getCache
from dossiers2.custom.utils import isVehicleSPG, getInBattleSeriesIndex
_saveRecordsInAccountDescr = {BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15: [{'block': 'achievements',
                                          'records': ('maxInvincibleSeries', 'maxDiehardSeries', 'maxSniperSeries', 'maxKillingSeries', 'maxPiercingSeries', 'maxAimerSeries')}],
 BONUS_CAPS.DOSSIER_ACHIEVEMENTS_7X7: [{'block': 'achievements7x7',
                                        'records': ('maxTacticalBreakthroughSeries',)}]}

def updateVehicleDossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, avatarResults):
    __updateDossierCommonPart(DOSSIER_TYPE.VEHICLE, dossierDescr, battleResults, dossierXP, avatarResults)
    __updateVehicleDossierImpl(vehTypeCompDescr, dossierDescr, battleResults, dossierXP)


def getMaxVehResults(results):
    if not results:
        return {}
    tmpVehMaxResults = {}
    for vehTypeCompDescr, vehResults in results.iteritems():
        for record in ('maxFragsVehicle', 'maxWinPointsVehicle', 'maxDamageVehicle', 'maxXPVehicle'):
            if record == 'maxFragsVehicle':
                kills = len(vehResults['killList'])
                if tmpVehMaxResults.get('maxFragsVehicle', (0, 0))[1] <= kills:
                    tmpVehMaxResults['maxFragsVehicle'] = (vehTypeCompDescr, kills)
            if record == 'maxWinPointsVehicle':
                winPoints = vehResults['winPoints']
                if tmpVehMaxResults.get('maxWinPointsVehicle', (0, 0))[1] <= winPoints:
                    tmpVehMaxResults['maxWinPointsVehicle'] = (vehTypeCompDescr, winPoints)
            if record == 'maxDamageVehicle':
                damageDealt = vehResults['damageDealt']
                if tmpVehMaxResults.get('maxDamageVehicle', (0, 0))[1] <= damageDealt:
                    tmpVehMaxResults['maxDamageVehicle'] = (vehTypeCompDescr, damageDealt)
            if record == 'maxXPVehicle':
                xp = vehResults['xp']
                if tmpVehMaxResults.get('maxXPVehicle', (0, 0))[1] <= xp:
                    tmpVehMaxResults['maxXPVehicle'] = (vehTypeCompDescr, xp)

    return {key:value[0] for key, value in tmpVehMaxResults.iteritems()}


def updateAccountDossier(dossierDescr, battleResults, dossierXP, vehDossiers, maxVehResults, avatarResults):
    bonusType = battleResults['bonusType']
    maxValuesChanged, frags8p = __updateDossierCommonPart(DOSSIER_TYPE.ACCOUNT, dossierDescr, battleResults, dossierXP, avatarResults)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_ACHIEVEMENTS):
        for vehTypeCompDescr, (_, vehDossierDescr) in vehDossiers.iteritems():
            __updateAccountRecords(BONUS_CAPS.get(bonusType), dossierDescr, vehDossierDescr)

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_7X7):
        __updateCapturePointsWithBaseCapture(dossierDescr, battleResults)
        __updateDefencePoints(dossierDescr, battleResults)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_SORTIE):
        __updateAggregatedValues(dossierDescr.expand('fortSortiesInClan'), dossierDescr.expand('fortSortiesInClan'), battleResults, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_FORT_BATTLE):
        __updateAggregatedValues(dossierDescr.expand('fortBattlesInClan'), dossierDescr.expand('fortBattlesInClan'), battleResults, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RATED7X7):
        clubDBID = battleResults['club'].get('clubDBID', 0)
        achievementsRated7x7 = dossierDescr['achievementsRated7x7']
        if clubDBID != achievementsRated7x7['victoryMarchClubDBID']:
            achievementsRated7x7['victoryMarchClubDBID'] = clubDBID
            achievementsRated7x7['victoryMarchSeries'] = 0
        _updatePerBattleSeries(dossierDescr['achievementsRated7x7'], 'victoryMarchSeries', battleResults['winnerTeam'] == battleResults['team'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_GLOBAL_MAP):
        division = battleResults['division']
        if division in GLOBAL_MAP_DIVISION._ORDER:
            if division == GLOBAL_MAP_DIVISION.MIDDLE:
                blockName = 'globalMapMiddle'
                blockNameMax = 'maxGlobalMapMiddle'
            elif division == GLOBAL_MAP_DIVISION.CHAMPION:
                blockName = 'globalMapChampion'
                blockNameMax = 'maxGlobalMapChampion'
            elif division == GLOBAL_MAP_DIVISION.ABSOLUTE:
                blockName = 'globalMapAbsolute'
                blockNameMax = 'maxGlobalMapAbsolute'
            __updateAggregatedValues(dossierDescr.expand(blockName), dossierDescr.expand(blockName), battleResults, dossierXP, frags8p)
            for record in __updateMaxValues(dossierDescr.expand(blockNameMax), battleResults, dossierXP):
                dossierDescr[blockNameMax][record] = maxVehResults[record]

            for record in maxValuesChanged:
                dossierDescr[blockNameMax][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RANKED):
        seasonBlock = 'rankedSeason{}'.format(avatarResults['rankedSeasonNum'])
        __updateAggregatedValues(dossierDescr.expand(seasonBlock), dossierDescr.expand(seasonBlock), battleResults, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX15X15):
        for record in maxValuesChanged:
            dossierDescr['max15x15'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX30X30):
        for record in maxValuesChanged:
            dossierDescr['max30x30'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX7X7):
        for record in maxValuesChanged:
            dossierDescr['max7x7'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRATED7X7):
        for record in maxValuesChanged:
            dossierDescr['maxRated7x7'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXFALLOUT):
        __updateMaxValuesWithAvatar(dossierDescr['maxFallout'], battleResults)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXSORTIE):
        for record in __updateMaxValues(dossierDescr.expand('maxFortSortiesInClan'), battleResults, dossierXP):
            dossierDescr['maxFortSortiesInClan'][record] = maxVehResults[record]

        for record in maxValuesChanged:
            dossierDescr['maxFortSorties'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXFORTBATTLE):
        for record in __updateMaxValues(dossierDescr.expand('maxFortBattlesInClan'), battleResults, dossierXP):
            dossierDescr['maxFortBattlesInClan'][record] = maxVehResults[record]

        for record in maxValuesChanged:
            dossierDescr['maxFortBattles'][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRANKED):
        seasonBlock = 'maxRankedSeason{}'.format(avatarResults['rankedSeasonNum'])
        for record in __updateMaxValues(dossierDescr.expand(seasonBlock), battleResults, dossierXP):
            dossierDescr[seasonBlock][record] = maxVehResults[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX_EPIC_BATTLE):
        for record in maxValuesChanged:
            dossierDescr['maxEpicBattle'][record] = maxVehResults[record]

    for vehTypeCompDescr, (_, vehDossierDescr) in vehDossiers.iteritems():
        __updateAccountDossierCuts(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr, avatarResults)


def __updateAccountRecords(bonusCaps, dossierDescr, vehDossierDescr):
    for cap, descr in _saveRecordsInAccountDescr.iteritems():
        if cap in bonusCaps:
            for item in descr:
                blockName = item['block']
                achievements = dossierDescr[blockName]
                vehAchievements = vehDossierDescr[blockName]
                for recordName in item['records']:
                    if vehAchievements[recordName] > achievements[recordName]:
                        achievements[recordName] = vehAchievements[recordName]


def updateRated7x7Dossier(dossierDescr, battleResults, dossierXP):
    bonusType = battleResults['bonusType']
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RATED7X7):
        __updateAggregatedValues(dossierDescr.expand('rated7x7'), dossierDescr.expand('rated7x7'), battleResults, dossierXP, frags8p=0)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRATED7X7):
        __updateMaxValues(dossierDescr.expand('maxRated7x7'), battleResults, dossierXP)


def updateTankmanDossier(dossierDescr, battleResults):
    __updateTankmanDossierImpl(dossierDescr, battleResults)


def updatePotapovQuestAchievements(accDossierDescr, progress):
    import potapov_quests
    achievementCounters = dict()
    completedCounters = dict()
    tileCache = potapov_quests.g_tileCache
    for questID, (flags, state) in progress.iteritems():
        if state < potapov_quests.PQ_STATE.NEED_GET_MAIN_REWARD:
            continue
        pqType = potapov_quests.g_cache.questByPotapovQuestID(questID)
        tileInfo = tileCache.getTileInfo(pqType.tileID)
        if state >= potapov_quests.PQ_STATE.NEED_GET_MAIN_REWARD:
            seasonID = tileInfo['seasonID']
            completedCounters[seasonID] = completedCounters.get(seasonID, 0) + 1
        if state >= potapov_quests.PQ_STATE.NEED_GET_ADD_REWARD:
            pqAchievements = tileInfo['achievements'] or {}
            chainAchievement = pqAchievements.get(pqType.chainID, None)
            if chainAchievement:
                achievementCounters[chainAchievement] = achievementCounters.get(chainAchievement, 0) + 1

    for seasonID, minCounter, achievementName in ((1, 1, 'firstMerit'), (2, 5, 'newMeritPM2')):
        needToAward = completedCounters.get(seasonID, 0) >= minCounter
        if needToAward and achievementName not in accDossierDescr['singleAchievements']:
            accDossierDescr['singleAchievements'][achievementName] = True

    for chainAchievement, counter in achievementCounters.iteritems():
        if chainAchievement not in RECORD_CONFIGS:
            continue
        steps = RECORD_CONFIGS[chainAchievement]
        maxLevel = len(steps)
        level = sum((1 for i in xrange(maxLevel) if counter >= steps[i]))
        stage = 0 if level == 0 else maxLevel - level + 1
        currStage = accDossierDescr['achievements'][chainAchievement]
        if currStage == 0 or stage < currStage:
            accDossierDescr['achievements'][chainAchievement] = stage

    return


def __updateDossierCommonPart(dossierType, dossierDescr, results, dossierXP, avatarResults):
    bonusType = results['bonusType']
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_TOTAL):
        __updateTotalValues(dossierDescr, results)
    frags8p = 0
    maxValuesChanged = []
    LOG_DEBUG_DEV('__updateDossierCommonPart', bonusType)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_KILL_LIST):
        frags8p = __processKillList(dossierDescr, results['killList'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_15X15):
        __updateAggregatedValues(dossierDescr.expand('a15x15'), dossierDescr.expand('a15x15_2'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_30X30):
        __updateAggregatedValues(dossierDescr.expand('a30x30'), dossierDescr.expand('a30x30'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_7X7):
        __updateAggregatedValues(dossierDescr.expand('a7x7'), dossierDescr.expand('a7x7'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RATED7X7):
        __updateAggregatedValues(dossierDescr.expand('rated7x7'), dossierDescr.expand('rated7x7'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_CLAN):
        __updateBaseStatistics(dossierDescr.expand('clan'), dossierDescr.expand('clan2'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_FALLOUT):
        __updateAggregatedValues(dossierDescr.expand('fallout'), dossierDescr.expand('fallout'), results, dossierXP, frags8p)
        for record in ('winPoints', 'flagCapture', 'soloFlagCapture', 'resourceAbsorbed', 'deathCount'):
            dossierDescr['fallout'][record] += results[record]

        if dossierType == DOSSIER_TYPE.ACCOUNT:
            for record in ('avatarDamageDealt', 'avatarKills'):
                dossierDescr['fallout'][record] += results[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_GLOBAL_MAP):
        if dossierDescr.isBlockInLayout('globalMapCommon'):
            __updateAggregatedValues(dossierDescr.expand('globalMapCommon'), dossierDescr.expand('globalMapCommon'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_SORTIE):
        __updateAggregatedValues(dossierDescr.expand('fortSorties'), dossierDescr.expand('fortSorties'), results, dossierXP, frags8p)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_FORT_BATTLE):
        __updateAggregatedValues(dossierDescr.expand('fortBattles'), dossierDescr.expand('fortBattles'), results, dossierXP, frags8p, determineWinnerTeam(avatarResults))
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_EPIC_BATTLE):
        __updateAggregatedValues(dossierDescr.expand('epicBattle'), dossierDescr.expand('epicBattle'), results, dossierXP, frags8p)
        for record in ['deathCount']:
            dossierDescr['epicBattle'][record] += results[record]

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_ACHIEVEMENTS, BONUS_CAPS.DOSSIER_ACHIEVEMENTS_FALLOUT):
        for recordDBID in results['achievements']:
            __processArenaAchievement(dossierDescr, recordDBID)

    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX15X15):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max15x15'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX30X30):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max30x30'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX7X7):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max7x7'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRATED7X7):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxRated7x7'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXSORTIE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFortSorties'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXFORTBATTLE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFortBattles'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRANKED):
        seasonBlock = 'maxRankedSeason{}'.format(avatarResults['rankedSeasonNum'])
        maxValuesChanged = __updateMaxValues(dossierDescr.expand(seasonBlock), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_GLOBAL_MAP):
        if dossierDescr.isBlockInLayout('maxGlobalMapCommon'):
            maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxGlobalMapCommon'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXFALLOUT):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFallout'), results, dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAX_EPIC_BATTLE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxEpicBattle'), results, dossierXP)
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
    for _, vehTypeCompDescr, _ in killList:
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


def __updateAggregatedValues(block, block2, results, dossierXP, frags8p, winnerTeam=None):
    __updateBaseStatistics(block, block2, results, dossierXP, winnerTeam)
    if results['deathCount'] == 0 and results['winnerTeam'] == results['team']:
        block['winAndSurvived'] += 1
    if frags8p != 0:
        block['frags8p'] += frags8p


def __updateBaseStatistics(block, block2, results, dossierXP, winnerTeam=None):
    block['battlesCount'] += 1
    if results['canStun']:
        block2['battlesOnStunningVehicles'] += 1
    if dossierXP != 0:
        block['xp'] += dossierXP
        block2['originalXP'] += results['originalXP']
    if not winnerTeam:
        winnerTeam = results['winnerTeam']
    if winnerTeam == results['team']:
        block['wins'] += 1
    elif winnerTeam == 0:
        pass
    else:
        block['losses'] += 1
    if results['deathCount'] == 0:
        block['survivedBattles'] += 1
    directHits = results['directEnemyHits']
    if directHits != 0:
        block['directHits'] += directHits
    for record in ('shots', 'spotted', 'damageDealt', 'damageReceived', 'capturePoints'):
        if bool(results[record]):
            block[record] += results[record]

    droppedCapturePoints = min(results['droppedCapturePoints'], 100)
    if droppedCapturePoints != 0:
        block['droppedCapturePoints'] += droppedCapturePoints
    kills = len(results['killList'])
    if kills:
        block['frags'] += kills
    for record in ('damageAssistedTrack', 'damageAssistedRadio', 'directHitsReceived', 'noDamageDirectHitsReceived', 'piercingsReceived', 'explosionHitsReceived', 'explosionHits', 'piercings', 'potentialDamageReceived', 'damageBlockedByArmor', 'stunNum', 'damageAssistedStun'):
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
    kills = len(results['killList'])
    if kills > 0 and kills >= block['maxFrags']:
        block['maxFrags'] = kills
        maxValuesChanged.append('maxFragsVehicle')
    damageDealt = results['damageDealt']
    if damageDealt > 0 and damageDealt >= block['maxDamage']:
        block['maxDamage'] = damageDealt
        maxValuesChanged.append('maxDamageVehicle')
    if BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_MAXFALLOUT):
        winPoints = results['winPoints']
        if winPoints > 0 and winPoints >= block['maxWinPoints']:
            block['maxWinPoints'] = winPoints
        maxValuesChanged.append('maxWinPointsVehicle')
    return maxValuesChanged


def __updateMaxValuesWithAvatar(block, results):
    if BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_MAXFALLOUT):
        kills = len(results['killList']) + results['avatarKills']
        if kills > 0 and kills >= block['maxFragsWithAvatar']:
            block['maxFragsWithAvatar'] = kills
        damageDealt = results['damageDealt'] + results['avatarDamageDealt']
        if damageDealt > 0 and damageDealt >= block['maxDamageWithAvatar']:
            block['maxDamageWithAvatar'] = damageDealt


def __updateMarksOnGun(dossierDescr, results):
    if not BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_MARKS_ON_GUN):
        return
    achievements = dossierDescr['achievements']
    damageRating = int(results['damageRating'] * 100)
    if damageRating != 0:
        achievements['damageRating'] = damageRating
    achievements['movingAvgDamage'] = results['movingAvgDamage']
    if achievements['marksOnGun'] < results['marksOnGun']:
        achievements['marksOnGun'] = results['marksOnGun']


def __updateMarkOfMastery(dossierDescr, results):
    if not BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_MARK_OF_MASTERY):
        return
    achievements = dossierDescr['achievements']
    markOfMasterField = 'marksOfMasteryCount{}'.format(results['markOfMastery'])
    if markOfMasterField in achievements:
        achievements[markOfMasterField] += 1
    if achievements['markOfMastery'] < results['markOfMastery']:
        achievements['markOfMastery'] = results['markOfMastery']


def __updateVehicleDossierImpl(vehTypeCompDescr, dossierDescr, results, dossierXP):
    bonusType = results['bonusType']
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_ACHIEVEMENTS_7X7):
        _updatePerBattleSeries(dossierDescr['achievements7x7'], 'tacticalBreakthroughSeries', results['winnerTeam'] == results['team'])
        return
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RANKED):
        __updateAggregatedValues(dossierDescr.expand('ranked_10x10'), dossierDescr.expand('ranked_10x10'), results, dossierXP, 0)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MAXRANKED):
        __updateMaxValues(dossierDescr.expand('maxRanked_10x10'), results, dossierXP)
    __updateMarksOnGun(dossierDescr, results)
    __updateMarkOfMastery(dossierDescr, results)
    if not BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        return
    achievements = dossierDescr['achievements']
    if results['winnerTeam'] == results['team'] and results['aimerSeries'] > 0:
        dossierDescr['singleAchievements']['aimer'] = 1
        if achievements['maxAimerSeries'] < results['aimerSeries']:
            achievements['maxAimerSeries'] = results['aimerSeries']
    isSPG = isVehicleSPG(vehTypeCompDescr)
    _updatePerBattleSeries(achievements, 'invincibleSeries', results['deathCount'] == 0 and results['damageReceived'] == 0 and not isSPG)
    _updatePerBattleSeries(achievements, 'diehardSeries', results['deathCount'] == 0 and not isSPG)
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


def __updateAccountDossierCuts(dossierDescr, results, dossierXP, vehTypeCompDescr, vehDossierDescr, avatarResults):
    bonusType = results['bonusType']
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_15X15):
        a15x15Cut = dossierDescr['a15x15Cut']
        vehA15x15 = vehDossierDescr['a15x15']
        a15x15Cut[vehTypeCompDescr] = (vehA15x15['battlesCount'], vehA15x15['wins'], vehA15x15['xp'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_30X30):
        a30x30Cut = dossierDescr['a30x30Cut']
        vehA30x30 = vehDossierDescr['a30x30']
        a30x30Cut[vehTypeCompDescr] = (vehA30x30['battlesCount'], vehA30x30['wins'], vehA30x30['xp'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_7X7):
        a7x7Cut = dossierDescr['a7x7Cut']
        vehA7x7 = vehDossierDescr['a7x7']
        a7x7Cut[vehTypeCompDescr] = (vehA7x7['battlesCount'],
         vehA7x7['wins'],
         vehA7x7['xp'],
         vehA7x7['originalXP'],
         vehA7x7['damageDealt'],
         vehA7x7['damageAssistedRadio'],
         vehA7x7['damageAssistedTrack'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_SORTIE):
        sortieCut = dossierDescr['fortSortiesCut']
        vehSortie = vehDossierDescr['fortSorties']
        sortieCut[vehTypeCompDescr] = (vehSortie['battlesCount'], vehSortie['wins'], vehSortie['xp'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_FORT_BATTLE):
        battleCut = dossierDescr['fortBattlesCut']
        vehBattles = vehDossierDescr['fortBattles']
        battleCut[vehTypeCompDescr] = (vehBattles['battlesCount'], vehBattles['wins'], vehBattles['xp'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RANKED):
        cut = dossierDescr['rankedCut']
        veh = vehDossierDescr['ranked_10x10']
        cut[vehTypeCompDescr] = (veh['battlesCount'], veh['wins'], veh['xp'])
        seasonBlock = 'rankedCutSeason{}'.format(avatarResults['rankedSeasonNum'])
        currentCut = dossierDescr[seasonBlock]
        battlesCount, wins, xp = currentCut.get(vehTypeCompDescr, (0, 0, 0))
        win = 1 if results['winnerTeam'] == results['team'] else 0
        currentCut[vehTypeCompDescr] = (battlesCount + 1, wins + win, xp + dossierXP)
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_RATED7X7):
        rated7x7Cut = dossierDescr['rated7x7Cut']
        vehRated7x7 = vehDossierDescr['rated7x7']
        rated7x7Cut[vehTypeCompDescr] = (vehRated7x7['battlesCount'],
         vehRated7x7['wins'],
         vehRated7x7['xp'],
         vehRated7x7['originalXP'],
         vehRated7x7['damageDealt'],
         vehRated7x7['damageAssistedRadio'],
         vehRated7x7['damageAssistedTrack'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_GLOBAL_MAP):
        globalMapCommonCut = dossierDescr['globalMapCommonCut']
        vehGlobalMapCommon = vehDossierDescr['globalMapCommon']
        globalMapCommonCut[vehTypeCompDescr] = (vehGlobalMapCommon['battlesCount'], vehGlobalMapCommon['wins'], vehGlobalMapCommon['xp'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_FALLOUT):
        falloutAccountDossierCut = dossierDescr['falloutCut']
        falloutVehicleDossier = vehDossierDescr['fallout']
        falloutAccountDossierCut[vehTypeCompDescr] = (falloutVehicleDossier['battlesCount'],
         falloutVehicleDossier['wins'],
         falloutVehicleDossier['xp'],
         falloutVehicleDossier['winPoints'])
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_MARK_OF_MASTERY):
        if vehDossierDescr['achievements']['markOfMastery'] != 0:
            markOfMasteryCut = dossierDescr['markOfMasteryCut']
            markOfMasteryCut[vehTypeCompDescr] = vehDossierDescr['achievements']['markOfMastery']
    if BONUS_CAPS.checkAny(bonusType, BONUS_CAPS.DOSSIER_EPIC_BATTLE):
        epicBattleAccountDossierCut = dossierDescr['epicBattleCut']
        epicBattleVehicleDossier = vehDossierDescr['epicBattle']
        epicBattleAccountDossierCut[vehTypeCompDescr] = (epicBattleVehicleDossier['battlesCount'], epicBattleVehicleDossier['wins'], epicBattleVehicleDossier['xp'])


def __updateTankmanDossierImpl(dossierDescr, results):
    if not BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_TOTAL):
        return
    dossierDescr['total']['battlesCount'] += 1
    if not BONUS_CAPS.checkAny(results['bonusType'], BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        return
    for recordDBID in results['achievements']:
        __processArenaAchievement(dossierDescr, recordDBID)


def __updateCapturePointsWithBaseCapture(dossierDescr, results):
    if results['isEnemyBaseCaptured'] and results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['infiltrator'] += results['capturePoints']


def __updateDefencePoints(dossierDescr, results):
    if results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['sentinel'] += results['droppedCapturePoints']
