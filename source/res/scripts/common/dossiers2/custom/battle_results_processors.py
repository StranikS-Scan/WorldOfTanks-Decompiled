# Embedded file name: scripts/common/dossiers2/custom/battle_results_processors.py
import time
from constants import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS, DESTR_CODES_BY_TAGS, FORT_BATTLE_RESULT, GLOBAL_MAP_DIVISION
from dossiers2.custom import records
from dossiers2.custom.cache import getCache
from dossiers2.custom.utils import isVehicleSPG, getInBattleSeriesIndex
from dossiers2.custom.records import RECORD_DB_IDS as DOSSIER_REC_DB_IDS
from UnitBase import SORTIE_DIVISION_NAMES, SORTIE_DIVISION
from debug_utils import *
_divisionToRecordNames = {'MIDDLE': ('middleBattlesCount', 'fortResourceInMiddle'),
 'CHAMPION': ('championBattlesCount', 'fortResourceInChampion'),
 'ABSOLUTE': ('absoluteBattlesCount', 'fortResourceInAbsolute')}

def updateFortSortieDossier(dossierDescr, divisionName, winner, fortResource, isCommander):
    if divisionName not in _divisionToRecordNames:
        raise Exception, 'Unknown sortie division'
    counterRecordName, resourceRecordName = _divisionToRecordNames[divisionName]
    sortieBlock = dossierDescr['fortSorties']
    sortieBlock[resourceRecordName] += fortResource
    if not isCommander:
        return
    sortieBlock['battlesCount'] += 1
    if winner == 1:
        sortieBlock['wins'] += 1
    if winner == 2:
        sortieBlock['losses'] += 1
    sortieBlock[counterRecordName] += 1


def updateFortBattleDossier(dossierDescr, isDefence, isWinner, enemyBaseCaptured, ownBaseLost, combatCount, combatWins, enemyBuildingCapture, ownBuildingLost, resourceCapture, resourceLost, **kwargs):
    block = dossierDescr['fortBattles']
    block['battlesCount'] += 1
    if isDefence:
        block['defenceCount'] += 1
    else:
        block['attackCount'] += 1
    if enemyBaseCaptured:
        block['enemyBaseCaptureCount'] += 1
    if ownBaseLost:
        block['ownBaseLossCount'] += 1
    block['combatCount'] += combatCount
    block['combatWins'] += combatWins
    if isWinner == FORT_BATTLE_RESULT.WIN:
        if not isDefence:
            block['successAttackCount'] += 1
        else:
            block['successDefenceCount'] += 1
    block['captureEnemyBuildingTotalCount'] += enemyBuildingCapture
    block['lossOwnBuildingTotalCount'] += ownBuildingLost
    block['resourceCaptureCount'] += resourceCapture
    block['resourceLossCount'] += resourceLost


def updateAccountDossierWithFortBattleResults(accountDBID, accDossierDescr, results):
    fortResource = results['accDBIDToResource'].get(accountDBID, 0)
    isDefence = results['isDefence']
    ownBaseLost = results['ownBaseLost']
    enemyBaseCaptured = results['enemyBaseCaptured']
    participateInFinalBattle = accountDBID in results['finialBattleParticipants']
    for blockName in ('fortMisc', 'fortMiscInClan'):
        miscBlock = accDossierDescr.expand(blockName)
        miscBlock['fortResourceInBattles'] += fortResource
        if fortResource > miscBlock['maxFortResourceInBattles']:
            miscBlock['maxFortResourceInBattles'] = fortResource
        if isDefence:
            miscBlock['defenceHours'] += 1
            if not ownBaseLost:
                miscBlock['successfulDefenceHours'] += 1
        else:
            miscBlock['attackNumber'] += 1
        if enemyBaseCaptured and participateInFinalBattle:
            miscBlock['enemyBasePlunderNumber'] += 1
            if not isDefence:
                miscBlock['enemyBasePlunderNumberInAttack'] += 1

    isWinner = results['isWinner']
    ownFortLevel = results['ownFortLevel']
    enemyFortLevel = results['enemyFortLevel']
    fortAchievements = accDossierDescr.expand('fortAchievements')
    if isWinner == FORT_BATTLE_RESULT.WIN:
        fortAchievements['wins'] += 1
    if enemyBaseCaptured and enemyFortLevel >= ownFortLevel:
        if isDefence:
            fortAchievements['capturedBasesInDefence'] += 1
        else:
            fortAchievements['capturedBasesInAttack'] += 1
    popUps = accDossierDescr.popPopUps()
    results['dossierPopUps'] = [ (DOSSIER_REC_DB_IDS[block, record], value) for (block, record), value in popUps.iteritems() ]
    return results


def updateVehicleDossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr):
    __updateDossierCommonPart(dossierDescr, battleResults, dossierXP)
    __updateVehicleDossierImpl(vehTypeCompDescr, dossierDescr, battleResults)


def updateAccountDossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr):
    maxValuesChanged, frags8p = __updateDossierCommonPart(dossierDescr, battleResults, dossierXP)
    __updateAccountDossierImpl(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr, maxValuesChanged, frags8p)


def updateRated7x7Dossier(dossierDescr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr):
    bonusCaps = BONUS_CAPS.get(battleResults['bonusType'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_RATED7X7):
        __updateAggregatedValues(dossierDescr.expand('rated7x7'), dossierDescr.expand('rated7x7'), battleResults, dossierXP, frags8p=0)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXRATED7X7):
        __updateMaxValues(dossierDescr.expand('maxRated7x7'), battleResults, dossierXP)


def updateClubDossier(dossierDescr, battleResults, geometryID, teamInDefence):
    bonusCaps = BONUS_CAPS.get(battleResults['bonusType'])
    if not bool(bonusCaps & BONUS_CAPS.DOSSIER_CLUB):
        return
    block = dossierDescr['total']
    block['lastBattleTime'] = int(time.time())
    block = dossierDescr.expand('clubBattles')
    block['battlesCount'] += 1
    team = battleResults['team']
    winnerTeam = battleResults['winnerTeam']
    if team == winnerTeam:
        block['wins'] += 1
    else:
        if winnerTeam == 0:
            LOG_ERROR('[EXCEPTION] updateClubDossier(dossierDescr, battleResults, geometryID): draw is not allowed for cybersport rated battles.')
        block['losses'] += 1
    for record in ('killedVehicles', 'lostVehicles', 'damageDealt', 'damageReceived', 'capturePoints', 'droppedCapturePoints'):
        block[record] += battleResults['club'][record]

    isInAttack = team != teamInDefence
    if isInAttack:
        block['battlesCountInAttack'] += 1
        block['damageDealtInAttack'] += battleResults['club']['damageDealt']
    else:
        block['damageDealtInDefence'] += battleResults['club']['damageDealt']
    block = dossierDescr['vehicles']
    for typeCompDescr, xp in battleResults['club']['vehicles']:
        battlesCount, experience = block.get(typeCompDescr, (0, 0))
        block[typeCompDescr] = (battlesCount + 1, experience + xp)

    block = dossierDescr['maps']
    battlesCount, wins = block.get(geometryID, (0, 0))
    block[geometryID] = (battlesCount + 1, wins + 1 if team == winnerTeam else 0)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_RATED7X7):
        for recordDBID in battleResults['club']['achievements']:
            __processArenaAchievement(dossierDescr, recordDBID)

        _updatePerBattleSeries(dossierDescr['achievementsRated7x7'], 'victoryMarchSeries', team == winnerTeam)


def updateTankmanDossier(dossierDescr, battleResults):
    __updateTankmanDossierImpl(dossierDescr, battleResults)


def updatePotapovQuestAchievements(accDossierDescr, vehClass, progress, curQuest, bonusCount):
    if not bonusCount:
        return
    elif vehClass not in curQuest.vehClasses:
        return
    else:
        if curQuest.isInitial and not accDossierDescr['singleAchievements']['firstMerit']:
            accDossierDescr['singleAchievements']['firstMerit'] = 1
        tileID, chainID = curQuest.tileID, curQuest.chainID
        import potapov_quests
        tileInfo = potapov_quests.g_tileCache.getTileInfo(tileID)
        if tileInfo['seasonID'] != 1:
            return
        pqAchievements = tileInfo['achievements']
        if not pqAchievements:
            return
        chainAchievement = pqAchievements.get(chainID, None)
        if chainAchievement is None:
            return
        chainSize = 15
        tilesCount = 1
        completedQuestsCount = 0
        for tileID, tileInfo in potapov_quests.g_tileCache:
            if tileInfo['seasonID'] != 1:
                continue
            tilesCount += 1
            questList = potapov_quests.g_cache.questListByTileIDChainID(tileID, chainID)
            raise len(questList) == chainSize or AssertionError
            for potapovQuestID in questList:
                flags, state = progress.get(potapovQuestID)
                if state is None:
                    continue
                if state >= potapov_quests.PQ_STATE.NEED_GET_ADD_REWARD:
                    completedQuestsCount += 1

        res = max(tilesCount - completedQuestsCount / chainSize, 1)
        if res <= 4:
            accDossierDescr['achievements'][chainAchievement] = res
        return


def __updateDossierCommonPart(dossierDescr, results, dossierXP):
    bonusCaps = BONUS_CAPS.get(results['bonusType'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_TOTAL):
        __updateTotalValues(dossierDescr, results)
    frags8p = 0
    maxValuesChanged = []
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_KILL_LIST):
        frags8p = __processKillList(dossierDescr, results['kill_list'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_15X15):
        __updateAggregatedValues(dossierDescr.expand('a15x15'), dossierDescr.expand('a15x15_2'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_7X7):
        __updateAggregatedValues(dossierDescr.expand('a7x7'), dossierDescr.expand('a7x7'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_RATED7X7):
        __updateAggregatedValues(dossierDescr.expand('rated7x7'), dossierDescr.expand('rated7x7'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_COMPANY):
        __updateBaseStatistics(dossierDescr.expand('company'), dossierDescr.expand('company2'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_CLAN):
        __updateBaseStatistics(dossierDescr.expand('clan'), dossierDescr.expand('clan2'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_GLOBAL_MAP):
        if dossierDescr.isBlockInLayout('globalMapCommon'):
            __updateAggregatedValues(dossierDescr.expand('globalMapCommon'), dossierDescr.expand('globalMapCommon'), results, dossierXP, frags8p)
        if dossierDescr.isBlockInLayout('maxGlobalMapCommon'):
            maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxGlobalMapCommon'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_HISTORICAL):
        __updateAggregatedValues(dossierDescr.expand('historical'), dossierDescr.expand('historical'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_SORTIE):
        __updateAggregatedValues(dossierDescr.expand('fortSorties'), dossierDescr.expand('fortSorties'), results, dossierXP, frags8p)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_FORT_BATTLE):
        if results['winnerTeam'] == 0:
            winnerTeam = results['fortBuilding']['buildTeam']
        else:
            winnerTeam = results['winnerTeam']
        __updateAggregatedValues(dossierDescr.expand('fortBattles'), dossierDescr.expand('fortBattles'), results, dossierXP, frags8p, winnerTeam)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS):
        for recordDBID in results['achievements'] + results['protoAchievements']:
            __processArenaAchievement(dossierDescr, recordDBID)

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX15X15):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max15x15'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX7X7):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('max7x7'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXRATED7X7):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxRated7x7'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXHISTORICAL):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxHistorical'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXSORTIE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFortSorties'), results, dossierXP)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXFORTBATTLE):
        maxValuesChanged = __updateMaxValues(dossierDescr.expand('maxFortBattles'), results, dossierXP)
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


def __updateAggregatedValues(block, block2, results, dossierXP, frags8p, winnerTeam = None):
    __updateBaseStatistics(block, block2, results, dossierXP, winnerTeam)
    if results['killerID'] == 0 and results['winnerTeam'] == results['team']:
        block['winAndSurvived'] += 1
    if frags8p != 0:
        block['frags8p'] += frags8p


def __updateBaseStatistics(block, block2, results, dossierXP, winnerTeam = None):
    block['battlesCount'] += 1
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
    bonusCaps = BONUS_CAPS.get(results['bonusType'])
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_7X7):
        _updatePerBattleSeries(dossierDescr['achievements7x7'], 'tacticalBreakthroughSeries', results['winnerTeam'] == results['team'])
    if not bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_15X15):
        return
    achievements = dossierDescr['achievements']
    if achievements['markOfMastery'] < results['markOfMastery']:
        achievements['markOfMastery'] = results['markOfMastery']
    damageRating = int(results['damageRating'] * 100)
    achievements['damageRating'] = damageRating
    achievements['movingAvgDamage'] = results['movingAvgDamage']
    if achievements['marksOnGun'] < results['marksOnGun']:
        achievements['marksOnGun'] = results['marksOnGun']
    if results['winnerTeam'] == results['team'] and results['aimerSeries'] > 0:
        dossierDescr['singleAchievements']['aimer'] = 1
        if achievements['maxAimerSeries'] < results['aimerSeries']:
            achievements['maxAimerSeries'] = results['aimerSeries']
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
            _updatePerBattleSeries(dossierDescr['achievements'], 'reliableComradeSeries', results['tdamageDealt'] == 0 and not results['tdestroyedModules'])
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

            dossierDescr['fortSortiesInClan']['fortResource'] += results['personalFortResource']
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_FORT_BATTLE):
            battleCut = dossierDescr['fortBattlesCut']
            vehBattles = vehDossierDescr['fortBattles']
            battleCut[vehTypeCompDescr] = (vehBattles['battlesCount'], vehBattles['wins'], vehBattles['xp'])
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_SORTIE):
            __updateAggregatedValues(dossierDescr.expand('fortSortiesInClan'), dossierDescr.expand('fortSortiesInClan'), results, dossierXP, frags8p)
            if results['division']:
                divisionNumber = getattr(SORTIE_DIVISION, results['division'])
                fortSortiesInClanBlock = dossierDescr['fortSortiesInClan']
                divisionLowerCase = SORTIE_DIVISION_NAMES[divisionNumber].lower()
                sortiesCombatsVar = '%sBattlesCount' % divisionLowerCase
                fortSortiesInClanBlock[sortiesCombatsVar] += 1
                if results['team'] == results['winnerTeam']:
                    sortiesCombatsWinsVar = '%sWins' % divisionLowerCase
                    fortSortiesInClanBlock[sortiesCombatsWinsVar] += 1
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_FORT_BATTLE):
            __updateAggregatedValues(dossierDescr.expand('fortBattlesInClan'), dossierDescr.expand('fortBattlesInClan'), results, dossierXP, frags8p)
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_RATED7X7):
            rated7x7Cut = dossierDescr['rated7x7Cut']
            vehRated7x7 = vehDossierDescr['rated7x7']
            rated7x7Cut[vehTypeCompDescr] = (vehRated7x7['battlesCount'],
             vehRated7x7['wins'],
             vehRated7x7['xp'],
             vehRated7x7['originalXP'],
             vehRated7x7['damageDealt'],
             vehRated7x7['damageAssistedRadio'],
             vehRated7x7['damageAssistedTrack'])
            if results['club']['clubDBID'] != dossierDescr['achievementsRated7x7']['victoryMarchClubDBID']:
                dossierDescr['achievementsRated7x7']['victoryMarchClubDBID'] = results['club']['clubDBID']
                dossierDescr['achievementsRated7x7']['victoryMarchSeries'] = 0
            _updatePerBattleSeries(dossierDescr['achievementsRated7x7'], 'victoryMarchSeries', results['winnerTeam'] == results['team'])
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS):
            __updateAccountRecords(bonusCaps, dossierDescr, vehDossierDescr)
        if bool(bonusCaps & BONUS_CAPS.DOSSIER_GLOBAL_MAP):
            division = results['division']
            if division in GLOBAL_MAP_DIVISION._ORDER:
                blockName = division == GLOBAL_MAP_DIVISION.MIDDLE and 'globalMapMiddle'
                blockNameMax = 'maxGlobalMapMiddle'
            elif division == GLOBAL_MAP_DIVISION.CHAMPION:
                blockName = 'globalMapChampion'
                blockNameMax = 'maxGlobalMapChampion'
            elif division == GLOBAL_MAP_DIVISION.ABSOLUTE:
                blockName = 'globalMapAbsolute'
                blockNameMax = 'maxGlobalMapAbsolute'
            __updateAggregatedValues(dossierDescr.expand(blockName), dossierDescr.expand(blockName), results, dossierXP, frags8p)
            for record in __updateMaxValues(dossierDescr.expand(blockNameMax), results, dossierXP):
                dossierDescr[blockNameMax][record] = vehTypeCompDescr

            for record in maxValuesChanged:
                dossierDescr[blockNameMax][record] = vehTypeCompDescr

            globalMapCommonCut = dossierDescr['globalMapCommonCut']
            vehGlobalMapCommon = vehDossierDescr['globalMapCommon']
            globalMapCommonCut[vehTypeCompDescr] = (vehGlobalMapCommon['battlesCount'], vehGlobalMapCommon['wins'], vehGlobalMapCommon['xp'])
        else:
            LOG_ERROR('Unknown global map division:', division)
    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX15X15):
        for record in maxValuesChanged:
            dossierDescr['max15x15'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAX7X7):
        for record in maxValuesChanged:
            dossierDescr['max7x7'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXRATED7X7):
        for record in maxValuesChanged:
            dossierDescr['maxRated7x7'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXHISTORICAL):
        for record in maxValuesChanged:
            dossierDescr['maxHistorical'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXSORTIE):
        for record in __updateMaxValues(dossierDescr.expand('maxFortSortiesInClan'), results, dossierXP):
            dossierDescr['maxFortSortiesInClan'][record] = vehTypeCompDescr

        for record in maxValuesChanged:
            dossierDescr['maxFortSorties'][record] = vehTypeCompDescr

    if bool(bonusCaps & BONUS_CAPS.DOSSIER_MAXFORTBATTLE):
        for record in __updateMaxValues(dossierDescr.expand('maxFortBattlesInClan'), results, dossierXP):
            dossierDescr['maxFortBattlesInClan'][record] = vehTypeCompDescr

        for record in maxValuesChanged:
            dossierDescr['maxFortBattles'][record] = vehTypeCompDescr

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
        names = ('maxInvincibleSeries', 'maxDiehardSeries', 'maxSniperSeries', 'maxKillingSeries', 'maxPiercingSeries', 'maxAimerSeries')
        res.append((targetBlock, names))
        targetBlock = 'singleAchievements'
        names = ('aimer',)
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
    elif bool(bonusCaps & BONUS_CAPS.DOSSIER_ACHIEVEMENTS_RATED7X7):
        res.append(('achievementsRated7x7', ()))
    else:
        raise Exception, 'Unknown achievement mode'
    return res


def __updateCapturePointsWithBaseCapture(dossierDescr, results):
    if results['isEnemyBaseCaptured'] and results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['infiltrator'] += results['capturePoints']


def __updateDefencePoints(dossierDescr, results):
    if results['winnerTeam'] == results['team']:
        dossierDescr['achievements7x7']['sentinel'] += results['droppedCapturePoints']
