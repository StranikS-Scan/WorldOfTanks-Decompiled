# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers/helpers.py
# Compiled at: 2011-11-02 13:49:22
import time
import dossiers
import battle_heroes
import arena_achievements
from debug_utils import *
from itertools import izip
from constants import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS

def updateVehicleDossier(descr, battleResults, originalXP, premiumXP, resultsOverriding=None):
    results = _resultOverriding(battleResults, resultsOverriding)
    res, stop, _, _ = _updateDossierCommonPart(descr, results, originalXP, premiumXP)
    if stop:
        return res
    return _updateVehicleDossierImpl(descr, originalXP, results)


def updateAccountDossier(databaseID, descr, battleResults, originalXP, premiumXP, vehTypeCompDescr, vehDossierDescr, resultsOverriding=None):
    results = _resultOverriding(battleResults, resultsOverriding)
    res, stop, isMaxFragsGained, isMaxXPGained = _updateDossierCommonPart(descr, results, originalXP, premiumXP)
    if stop:
        return res
    res = _updateAccountDossierImpl(descr, results, vehTypeCompDescr, vehDossierDescr, isMaxFragsGained, isMaxXPGained)
    _validateAccountAndVehicleDossiers(databaseID, descr, vehDossierDescr, vehTypeCompDescr)
    return res


def updateTankmanDossier(descr, battleResults, resultsOverriding=None):
    results = _resultOverriding(battleResults, resultsOverriding)
    return _updateTankmanDossierImpl(descr, results)


def _resultOverriding(battleResults, resultsOverriding):
    if resultsOverriding is None:
        return battleResults
    else:
        results = dict(battleResults)
        results.update(resultsOverriding)
        return results


def _updateDossierCommonPart(descr, results, originalXP, premiumXP):
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_TOTAL_VALUES):
        return (set(),
         True,
         False,
         False)
    descr['battleLifeTime'] += results['lifeTime']
    descr['lastBattleTime'] = int(time.time())
    _updateDossierRecordsWithBonusTypePrefix(descr, '', results, premiumXP)
    if bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_COMPANY_VALUES):
        _updateDossierRecordsWithBonusTypePrefix(descr, 'company/', results, premiumXP)
    if bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_CLAN_VALUES):
        _updateDossierRecordsWithBonusTypePrefix(descr, 'clan/', results, premiumXP)
    if results['killerID'] == 0 and results['isWinner'] == 1:
        descr['winAndSurvived'] += 1
    ownVehicleID = results['vehicleID']
    ownAchieveIndices = [ code for code, vehicleID in izip(results['achieveIndices'], results['heroVehicleIDs']) if vehicleID == ownVehicleID ]
    for achieveIdx in ownAchieveIndices:
        record = battle_heroes.ACHIEVEMENT_NAMES[achieveIdx]
        descr[record] += 1

    killedTypeCompDescrs = results['killedTypeCompDescrs']
    if killedTypeCompDescrs:
        vehTypeFrags = dict(descr['vehTypeFrags'])
        vehicles8p = dossiers._g_cache['vehicles8+']
        beastVehicles = dossiers._g_cache['beastVehicles']
        frags8p = 0
        fragsBeast = 0
        for vtcd in killedTypeCompDescrs:
            frags = vehTypeFrags.get(vtcd, 0)
            vehTypeFrags[vtcd] = min(frags + 1, 60001)
            if vtcd in vehicles8p:
                frags8p += 1
            if vtcd in beastVehicles:
                fragsBeast += 1

        descr['vehTypeFrags'] = vehTypeFrags
        if frags8p != 0:
            descr['frags8p'] += frags8p
        if fragsBeast != 0:
            descr['fragsBeast'] += fragsBeast
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_RND_VALUES):
        return (set(),
         False,
         False,
         False)
    isMaxXPGained = False
    if premiumXP != 0 and premiumXP >= descr['maxXP']:
        isMaxXPGained = True
        descr['maxXP'] = premiumXP
    for achieveIdx in results['epicAchievements']:
        record = arena_achievements.ACHIEVEMENT_NAMES[achieveIdx]
        descr[record] += 1

    for achieveName in ('raider', 'kamikaze'):
        achieveIdx = arena_achievements.ACHIEVEMENTS_INDICES[achieveName]
        if achieveIdx << 24 in results['honorTitles']:
            descr[achieveName] += 1

    isMaxFragsGained = False
    if killedTypeCompDescrs and len(killedTypeCompDescrs) >= descr['maxFrags']:
        descr['maxFrags'] = len(killedTypeCompDescrs)
        isMaxFragsGained = True
    return (set(),
     False,
     isMaxFragsGained,
     isMaxXPGained)


def _updateDossierRecordsWithBonusTypePrefix(descr, prefix, results, premiumXP):
    descr[prefix + 'battlesCount'] += 1
    if premiumXP != 0:
        descr[prefix + 'xp'] += premiumXP
    isWinner = results['isWinner']
    if isWinner == 1:
        descr[prefix + 'wins'] += 1
    elif isWinner == -1:
        descr[prefix + 'losses'] += 1
    if results['killerID'] == 0:
        descr[prefix + 'survivedBattles'] += 1
    shots = results['shots']
    if shots != 0:
        descr[prefix + 'shots'] += shots
    hits = results['hits']
    if hits != 0:
        descr[prefix + 'hits'] += hits
    spotted = results['spotted']
    if spotted:
        descr[prefix + 'spotted'] += len(spotted)
    damageDealt = results['damageDealt']
    if damageDealt != 0:
        descr[prefix + 'damageDealt'] += damageDealt
    damageReceived = results['damageReceived']
    if damageReceived != 0:
        descr[prefix + 'damageReceived'] += damageReceived
    capturePoints = results['capturePoints']
    if capturePoints != 0:
        descr[prefix + 'capturePoints'] += capturePoints
    droppedCapturePoints = min(results['droppedCapturePoints'], 100)
    if droppedCapturePoints != 0:
        descr[prefix + 'droppedCapturePoints'] += droppedCapturePoints
    killedTypeCompDescrs = results['killedTypeCompDescrs']
    if killedTypeCompDescrs:
        descr[prefix + 'frags'] += len(killedTypeCompDescrs)


def _updateVehicleDossierImpl(descr, originalXP, results):
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_RND_VALUES):
        return set()
    perBattleSeriesAchievementNames = ('invincible', 'diehard')
    for achieveName in perBattleSeriesAchievementNames:
        achieveIdx = arena_achievements.ACHIEVEMENTS_INDICES[achieveName]
        recordName = achieveName + 'Series'
        if achieveIdx << 24 in results['honorTitles']:
            descr[recordName] += 1
        else:
            descr[recordName] = 0

    seriesAchievementNames = ('sniper', 'killing', 'piercing')
    for achieveName in seriesAchievementNames:
        achieveIdx = arena_achievements.ACHIEVEMENTS_INDICES[achieveName]
        recordName = achieveName + 'Series'
        series = [ code & 16777215 for code in results['honorTitles'] if code >> 24 == achieveIdx ]
        if series:
            descr[recordName] = descr[recordName] + series[0]
        for runLength in series[1:]:
            descr[recordName] = runLength

    return set(descr.notified) & dossiers.EVENT_RECORDS


def _updateAccountDossierImpl(descr, results, vehTypeCompDescr, vehDossierDescr, isMaxFragsGained, isMaxXPGained):
    assert vehDossierDescr is not None
    vehDossiersCut = dict(descr['vehDossiersCut'])
    battlesCount, wins = vehDossiersCut.get(vehTypeCompDescr, (0, 0))
    if results['isWinner'] == 1:
        wins += 1
    vehDossiersCut[vehTypeCompDescr] = (battlesCount + 1, wins)
    descr['vehDossiersCut'] = vehDossiersCut
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_RND_VALUES):
        return set()
    else:
        perBattleSeriesAchievementBestResults = ('maxInvincibleSeries', 'maxDiehardSeries')
        for recordName in perBattleSeriesAchievementBestResults:
            if vehDossierDescr[recordName] > descr[recordName]:
                descr[recordName] = vehDossierDescr[recordName]

        seriesAchievementBestResults = ('maxSniperSeries', 'maxKillingSeries', 'maxPiercingSeries')
        for recordName in seriesAchievementBestResults:
            if vehDossierDescr[recordName] > descr[recordName]:
                descr[recordName] = vehDossierDescr[recordName]

        if isMaxXPGained:
            descr['maxXPVehicle'] = vehTypeCompDescr
        if isMaxFragsGained:
            descr['maxFragsVehicle'] = vehTypeCompDescr
        return set(descr.notified)


def _updateTankmanDossierImpl(descr, results):
    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_TOTAL_VALUES):
        return set()
    descr['battlesCount'] += 1
    ownVehicleID = results['vehicleID']
    ownAchieveIndices = [ code for code, vehicleID in izip(results['achieveIndices'], results['heroVehicleIDs']) if vehicleID == ownVehicleID ]
    for achieveIdx in ownAchieveIndices:
        record = battle_heroes.ACHIEVEMENT_NAMES[achieveIdx]
        descr[record] += 1

    if not bool(BONUS_CAPS.get(results['bonusType']) & BONUS_CAPS.DOSSIER_RND_VALUES):
        return set()
    for achieveIdx in results['epicAchievements']:
        record = arena_achievements.ACHIEVEMENT_NAMES[achieveIdx]
        descr[record] += 1

    return set()


def _validateAccountAndVehicleDossiers(databaseID, accDossier, vehDossier, vehTypeCompDescr):
    try:
        if accDossier['battlesCount'] < vehDossier['battlesCount']:
            raise Exception, "Sum 'battlesCount' is mismatched for vehicle: %s, account databaseID: %d." % (vehTypeCompDescr, databaseID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        accDossier['battlesCount'] = vehDossier['battlesCount']

    battlesCount, wins = accDossier['vehDossiersCut'].get(vehTypeCompDescr, (0, 0))
    try:
        if battlesCount != vehDossier['battlesCount']:
            raise Exception, "'battlesCount' is mismatched for vehicle: %s, account databaseID: %d." % (vehTypeCompDescr, databaseID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        vehDossiersCut = dict(accDossier['vehDossiersCut'])
        vehDossiersCut[vehTypeCompDescr] = (vehDossier['battlesCount'], wins)
        accDossier['vehDossiersCut'] = vehDossiersCut
        battlesCount = vehDossier['battlesCount']

    try:
        if wins != vehDossier['wins']:
            raise Exception, "'wins' is mismatched for vehicle: %s, account databaseID: %d." % (vehTypeCompDescr, databaseID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        vehDossiersCut = dict(accDossier['vehDossiersCut'])
        vehDossiersCut[vehTypeCompDescr] = (battlesCount, vehDossier['wins'])
        accDossier['vehDossiersCut'] = vehDossiersCut

    try:
        if accDossier['maxXP'] < vehDossier['maxXP']:
            raise Exception, "'maxXPVehicle' is mismatched for vehicle: %s, account databaseID: %d." % (vehTypeCompDescr, databaseID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        accDossier['maxXP'] = vehDossier['maxXP']
        accDossier['maxXPVehicle'] = vehTypeCompDescr

    try:
        if accDossier['maxFrags'] < vehDossier['maxFrags']:
            raise Exception, "'maxFragsVehicle' is mismatched for vehicle: %s, account databaseID: %d." % (vehTypeCompDescr, databaseID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        accDossier['maxFrags'] = vehDossier['maxFrags']
        accDossier['maxFragsVehicle'] = vehTypeCompDescr

    for record in battle_heroes.ACHIEVEMENT_NAMES + arena_achievements.ACHIEVEMENT_NAMES:
        try:
            if record in accDossier and record in vehDossier and accDossier[record] < vehDossier[record]:
                raise Exception, "'%s' is mismatched for vehicle: %s, account databaseID: %d." % (record, vehTypeCompDescr, databaseID)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            accDossier[record] = vehDossier[record]
