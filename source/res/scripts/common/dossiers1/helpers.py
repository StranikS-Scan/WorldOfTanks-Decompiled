# Embedded file name: scripts/common/dossiers1/helpers.py
import time
import utils
import arena_achievements
import dossiers1
from constants import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import DESTR_CODES_BY_TAGS
from debug_utils import *

def updateVehicleDossier(descr, battleResults, dossierXP, vehTypeCompDescr, resultsOverriding = None):
    results = _resultOverriding(battleResults, resultsOverriding)
    stop, _, _ = _updateDossierCommonPart(descr, results, dossierXP)
    if not stop:
        _updateVehicleDossierImpl(vehTypeCompDescr, descr, results)
    return set(descr.popUps)


def updateAccountDossier(databaseID, descr, battleResults, dossierXP, vehTypeCompDescr, vehDossierDescr, resultsOverriding = None):
    results = _resultOverriding(battleResults, resultsOverriding)
    stop, isMaxFragsGained, isMaxXPGained = _updateDossierCommonPart(descr, results, dossierXP)
    if not stop:
        _updateAccountDossierImpl(descr, results, vehTypeCompDescr, vehDossierDescr, isMaxFragsGained, isMaxXPGained)
        _validateAccountAndVehicleDossiers(databaseID, descr, vehDossierDescr, vehTypeCompDescr)
    return set(descr.popUps)


def updateTankmanDossier(descr, battleResults, resultsOverriding = None):
    results = _resultOverriding(battleResults, resultsOverriding)
    _updateTankmanDossierImpl(descr, results)
    return set(descr.popUps)


def _resultOverriding(battleResults, resultsOverriding):
    if resultsOverriding is None:
        return battleResults
    else:
        results = dict(battleResults)
        results.update(resultsOverriding)
        return results


def _updateDossierCommonPart(descr, results, dossierXP):
    raise False or AssertionError


def _updateDossierRecordsWithBonusTypePrefix(descr, prefix, results, dossierXP):
    descr[prefix + 'battlesCount'] += 1
    if dossierXP != 0:
        descr[prefix + 'xp'] += dossierXP
    if results['winnerTeam'] == results['team']:
        descr[prefix + 'wins'] += 1
    elif results['winnerTeam'] == 3 - results['team']:
        descr[prefix + 'losses'] += 1
    if results['killerID'] == 0:
        descr[prefix + 'survivedBattles'] += 1
    shots = results['shots']
    if shots != 0:
        descr[prefix + 'shots'] += shots
    hits = results['directHits']
    if hits != 0:
        descr[prefix + 'directHits'] += hits
    spotted = results['spotted']
    if spotted:
        descr[prefix + 'spotted'] += spotted
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
    kills = results['kills']
    if kills:
        descr[prefix + 'frags'] += kills


def _updateVehicleDossierImpl(vehTypeCompDescr, descr, results):
    raise False or AssertionError


def _updatePerBattleSeries(descr, achieveName, isNotInterrupted):
    if achieveName not in descr:
        return
    if isNotInterrupted:
        descr[achieveName] += 1
    else:
        descr[achieveName] = 0


def _updateInBattleSeries(descr, achieveName, results):
    achieveIdx = arena_achievements.INBATTLE_SERIES_INDICES[achieveName]
    recordName = achieveName + 'Series'
    if recordName not in descr:
        return
    series = results['series'].get(achieveIdx, [])
    if series:
        descr[recordName] = descr[recordName] + series[0]
    for runLength in series[1:]:
        descr[recordName] = runLength


def _updateAccountDossierImpl(descr, results, vehTypeCompDescr, vehDossierDescr, isMaxFragsGained, isMaxXPGained):
    raise False or AssertionError


def _updateTankmanDossierImpl(descr, results):
    raise False or AssertionError


def _validateAccountAndVehicleDossiers(databaseID, accDossier, vehDossier, vehTypeCompDescr):
    needRecalculateBattlesCountAndWins = False
    try:
        if accDossier['battlesCount'] < vehDossier['battlesCount']:
            raise Exception, "Sum 'battlesCount' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             accDossier['battlesCount'],
             vehDossier['battlesCount'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        needRecalculateBattlesCountAndWins = True

    battlesCount, wins, markOfMastery, xp = accDossier['a15x15Cut'].get(vehTypeCompDescr, (0, 0, 0, 0))
    try:
        if battlesCount != vehDossier['battlesCount']:
            raise Exception, "'battlesCount' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             battlesCount,
             vehDossier['battlesCount'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        a15x15Cut = dict(accDossier['a15x15Cut'])
        a15x15Cut[vehTypeCompDescr] = (vehDossier['battlesCount'],
         wins,
         markOfMastery,
         xp)
        accDossier['a15x15Cut'] = a15x15Cut
        battlesCount = vehDossier['battlesCount']
        needRecalculateBattlesCountAndWins = True

    try:
        if wins != vehDossier['wins']:
            raise Exception, "'wins' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             wins,
             vehDossier['wins'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        a15x15Cut = dict(accDossier['a15x15Cut'])
        a15x15Cut[vehTypeCompDescr] = (battlesCount,
         vehDossier['wins'],
         markOfMastery,
         xp)
        accDossier['a15x15Cut'] = a15x15Cut
        wins = vehDossier['wins']
        needRecalculateBattlesCountAndWins = True

    try:
        if markOfMastery != vehDossier['markOfMastery']:
            raise Exception, "'markOfMastery' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             markOfMastery,
             vehDossier['markOfMastery'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        a15x15Cut = dict(accDossier['a15x15Cut'])
        a15x15Cut[vehTypeCompDescr] = (battlesCount,
         wins,
         vehDossier['markOfMastery'],
         xp)
        accDossier['a15x15Cut'] = a15x15Cut
        markOfMastery = vehDossier['markOfMastery']

    try:
        if xp != vehDossier['xp']:
            raise Exception, "'xp' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             xp,
             vehDossier['xp'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        a15x15Cut = dict(accDossier['a15x15Cut'])
        a15x15Cut[vehTypeCompDescr] = (battlesCount,
         wins,
         markOfMastery,
         vehDossier['xp'])
        accDossier['a15x15Cut'] = a15x15Cut

    if needRecalculateBattlesCountAndWins:
        _recalculateBattlesCountAndWins(accDossier)
    try:
        if accDossier['maxXP'] < vehDossier['maxXP']:
            raise Exception, "'maxXP' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             accDossier['maxXP'],
             vehDossier['maxXP'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        accDossier['maxXP'] = vehDossier['maxXP']
        accDossier['maxXPVehicle'] = vehTypeCompDescr

    try:
        if accDossier['maxFrags'] < vehDossier['maxFrags']:
            raise Exception, "'maxFrags' mismatch (%s, %s, %s, %s)" % (databaseID,
             vehTypeCompDescr,
             accDossier['maxFrags'],
             vehDossier['maxFrags'])
    except Exception:
        LOG_CURRENT_EXCEPTION()
        accDossier['maxFrags'] = vehDossier['maxFrags']
        accDossier['maxFragsVehicle'] = vehTypeCompDescr

    for record in arena_achievements.ACHIEVEMENTS:
        try:
            if record in accDossier and record in vehDossier and accDossier[record] < vehDossier[record]:
                raise Exception, "'%s' mismatch (%s, %s, %s, %s)" % (record,
                 databaseID,
                 vehTypeCompDescr,
                 accDossier[record],
                 vehDossier[record])
        except Exception:
            LOG_CURRENT_EXCEPTION()
            accDossier[record] = vehDossier[record]


def _recalculateBattlesCountAndWins(accDossier):
    battlesCountSum = winsSum = 0
    for battlesCount, wins, _, _ in accDossier['a15x15Cut'].itervalues():
        battlesCountSum += battlesCount
        winsSum += wins

    accDossier['battlesCount'] = battlesCountSum
    accDossier['wins'] = winsSum
