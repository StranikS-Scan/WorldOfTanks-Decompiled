# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers/__init__.py
# Compiled at: 2011-11-28 16:05:24
import nations
import collections
from struct import *
from debug_utils import *
from items import vehicles
from functools import partial
from constants import DOSSIER_TYPE
from dossiers.config import RECORD_CONFIGS
from dossier_updaters import *
from utils import buildStaticRecordPositions, buildStaticRecordsFmt, getVehTypeFragsFmtValues, unpackVehTypeFrags, getVehDossiersCutFmtValues, unpackVehDossiersCut, extendRecordPacking
ACCOUNT_DOSSIER_VERSION = 21
VEHICLE_DOSSIER_VERSION = 20
TANKMAN_DOSSIER_VERSION = 11
RECORD_NAMES = ('reserved', 'xp', 'maxXP', 'battlesCount', 'wins', 'losses', 'survivedBattles', 'lastBattleTime', 'battleLifeTime', 'winAndSurvived', 'battleHeroes', 'frags', 'maxFrags', 'frags8p', 'fragsBeast', 'shots', 'hits', 'spotted', 'damageDealt', 'damageReceived', 'treesCut', 'capturePoints', 'droppedCapturePoints', 'sniperSeries', 'maxSniperSeries', 'invincibleSeries', 'maxInvincibleSeries', 'diehardSeries', 'maxDiehardSeries', 'killingSeries', 'maxKillingSeries', 'piercingSeries', 'maxPiercingSeries', 'vehTypeFrags', 'warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout', 'medalKay', 'medalCarius', 'medalKnispel', 'medalPoppel', 'medalAbrams', 'medalLeClerc', 'medalLavrinenko', 'medalEkins', 'medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin', 'tankExpert', 'titleSniper', 'invincible', 'diehard', 'raider', 'handOfDeath', 'armorPiercer', 'kamikaze', 'lumberjack', 'beasthunter', 'mousebane', 'creationTime', 'maxXPVehicle', 'maxFragsVehicle', 'vehDossiersCut', 'evileye', 'medalHeroesOfRassenai', 'medalDeLaglanda', 'medalTamadaYoshio', 'medalErohin', 'medalHoroshilov', 'medalLister', 'markOfMastery', 'company/xp', 'company/battlesCount', 'company/wins', 'company/losses', 'company/survivedBattles', 'company/frags', 'company/shots', 'company/hits', 'company/spotted', 'company/damageDealt', 'company/damageReceived', 'company/capturePoints', 'company/droppedCapturePoints', 'clan/xp', 'clan/battlesCount', 'clan/wins', 'clan/losses', 'clan/survivedBattles', 'clan/frags', 'clan/shots', 'clan/hits', 'clan/spotted', 'clan/damageDealt', 'clan/damageReceived', 'clan/capturePoints', 'clan/droppedCapturePoints')
RECORD_INDICES = dict(((x[1], x[0]) for x in enumerate(RECORD_NAMES)))
POP_UP_RECORDS = set(['warrior',
 'invader',
 'sniper',
 'defender',
 'steelwall',
 'supporter',
 'scout',
 'medalKay',
 'medalCarius',
 'medalKnispel',
 'medalPoppel',
 'medalAbrams',
 'medalLeClerc',
 'medalLavrinenko',
 'medalEkins',
 'medalWittmann',
 'medalOrlik',
 'medalOskin',
 'medalHalonen',
 'medalBurda',
 'medalBillotte',
 'medalKolobanov',
 'medalFadin',
 'beasthunter',
 'mousebane',
 'tankExpert',
 'titleSniper',
 'invincible',
 'diehard',
 'raider',
 'handOfDeath',
 'armorPiercer',
 'kamikaze',
 'lumberjack',
 'medalHeroesOfRassenai',
 'medalDeLaglanda',
 'medalTamadaYoshio',
 'medalErohin',
 'medalHoroshilov',
 'medalLister',
 'markOfMastery',
 'evileye'])
EVENT_RECORDS = set(['titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer'])

def _set_RECORD_PACKING():
    global _RECORD_PACKING
    _RECORD_PACKING = {'_version': ('p', 'H', 2, 32767),
     'warrior': ('p', 'H', 2, 60001),
     'invader': ('p', 'H', 2, 60001),
     'sniper': ('p', 'H', 2, 60001),
     'defender': ('p', 'H', 2, 60001),
     'steelwall': ('p', 'H', 2, 60001),
     'supporter': ('p', 'H', 2, 60001),
     'scout': ('p', 'H', 2, 60001),
     'evileye': ('p', 'H', 2, 60001),
     'battleHeroes': ('p', 'H', 2, 60001),
     'treesCut': ('p', 'H', 2, 60001),
     'maxXP': ('p', 'H', 2, 60001),
     'sniperSeries': ('p', 'H', 2, 60001),
     'maxSniperSeries': ('p', 'H', 2, 60001),
     'invincibleSeries': ('p', 'B', 1, 201),
     'maxInvincibleSeries': ('p', 'B', 1, 201),
     'diehardSeries': ('p', 'B', 1, 201),
     'maxDiehardSeries': ('p', 'B', 1, 201),
     'killingSeries': ('p', 'B', 1, 201),
     'maxKillingSeries': ('p', 'B', 1, 201),
     'piercingSeries': ('p', 'B', 1, 201),
     'maxPiercingSeries': ('p', 'B', 1, 201),
     'maxFrags': ('p', 'B', 1, 201),
     'xp': ('p', 'I', 4, 4000000001L),
     'company/xp': ('p', 'I', 4, 4000000001L),
     'clan/xp': ('p', 'I', 4, 4000000001L),
     'battlesCount': ('p', 'I', 4, 4000000001L),
     'company/battlesCount': ('p', 'I', 4, 4000000001L),
     'clan/battlesCount': ('p', 'I', 4, 4000000001L),
     'wins': ('p', 'I', 4, 4000000001L),
     'company/wins': ('p', 'I', 4, 4000000001L),
     'clan/wins': ('p', 'I', 4, 4000000001L),
     'losses': ('p', 'I', 4, 4000000001L),
     'company/losses': ('p', 'I', 4, 4000000001L),
     'clan/losses': ('p', 'I', 4, 4000000001L),
     'survivedBattles': ('p', 'I', 4, 4000000001L),
     'company/survivedBattles': ('p', 'I', 4, 4000000001L),
     'clan/survivedBattles': ('p', 'I', 4, 4000000001L),
     'winAndSurvived': ('p', 'I', 4, 4000000001L),
     'lastBattleTime': ('p', 'I', 4, 4000000001L),
     'frags': ('p', 'I', 4, 4000000001L),
     'company/frags': ('p', 'I', 4, 4000000001L),
     'clan/frags': ('p', 'I', 4, 4000000001L),
     'frags8p': ('p', 'I', 4, 4000000001L),
     'fragsBeast': ('p', 'I', 4, 4000000001L),
     'shots': ('p', 'I', 4, 4000000001L),
     'company/shots': ('p', 'I', 4, 4000000001L),
     'clan/shots': ('p', 'I', 4, 4000000001L),
     'hits': ('p', 'I', 4, 4000000001L),
     'company/hits': ('p', 'I', 4, 4000000001L),
     'clan/hits': ('p', 'I', 4, 4000000001L),
     'spotted': ('p', 'I', 4, 4000000001L),
     'company/spotted': ('p', 'I', 4, 4000000001L),
     'clan/spotted': ('p', 'I', 4, 4000000001L),
     'damageDealt': ('p', 'I', 4, 4000000001L),
     'company/damageDealt': ('p', 'I', 4, 4000000001L),
     'clan/damageDealt': ('p', 'I', 4, 4000000001L),
     'damageReceived': ('p', 'I', 4, 4000000001L),
     'company/damageReceived': ('p', 'I', 4, 4000000001L),
     'clan/damageReceived': ('p', 'I', 4, 4000000001L),
     'capturePoints': ('p', 'I', 4, 4000000001L),
     'company/capturePoints': ('p', 'I', 4, 4000000001L),
     'clan/capturePoints': ('p', 'I', 4, 4000000001L),
     'droppedCapturePoints': ('p', 'I', 4, 4000000001L),
     'company/droppedCapturePoints': ('p', 'I', 4, 4000000001L),
     'clan/droppedCapturePoints': ('p', 'I', 4, 4000000001L),
     'battleLifeTime': ('p', 'I', 4, 4000000001L),
     'creationTime': ('p', 'I', 4, 4000000001L),
     'maxXPVehicle': ('p', 'I', 4, 4294967295L),
     'maxFragsVehicle': ('p', 'I', 4, 4294967295L),
     'medalKay': ('p', 'B', 1, 4),
     'medalCarius': ('p', 'B', 1, 4),
     'medalKnispel': ('p', 'B', 1, 4),
     'medalPoppel': ('p', 'B', 1, 4),
     'medalAbrams': ('p', 'B', 1, 4),
     'medalLeClerc': ('p', 'B', 1, 4),
     'medalLavrinenko': ('p', 'B', 1, 4),
     'medalEkins': ('p', 'B', 1, 4),
     'medalWittmann': ('p', 'H', 2, 60001),
     'medalOrlik': ('p', 'H', 2, 60001),
     'medalOskin': ('p', 'H', 2, 60001),
     'medalHalonen': ('p', 'H', 2, 60001),
     'medalBurda': ('p', 'H', 2, 60001),
     'medalBillotte': ('p', 'H', 2, 60001),
     'medalKolobanov': ('p', 'H', 2, 60001),
     'medalFadin': ('p', 'H', 2, 60001),
     'medalHeroesOfRassenai': ('p', 'H', 2, 60001),
     'medalDeLaglanda': ('p', 'H', 2, 60001),
     'medalTamadaYoshio': ('p', 'H', 2, 60001),
     'medalErohin': ('p', 'H', 2, 60001),
     'medalHoroshilov': ('p', 'H', 2, 60001),
     'medalLister': ('p', 'H', 2, 60001),
     'beasthunter': ('p', 'H', 2, 60001),
     'mousebane': ('p', 'H', 2, 60001),
     'tankExpert': ('p', 'B', 1, 1),
     'titleSniper': ('p', 'B', 1, 1),
     'invincible': ('p', 'B', 1, 1),
     'diehard': ('p', 'B', 1, 1),
     'raider': ('p', 'H', 2, 60001),
     'handOfDeath': ('p', 'B', 1, 1),
     'armorPiercer': ('p', 'B', 1, 1),
     'kamikaze': ('p', 'H', 2, 60001),
     'lumberjack': ('p', 'B', 1, 1),
     'markOfMastery': ('p', 'B', 1, 4),
     'vehTypeFrags': ('d', getVehTypeFragsFmtValues, unpackVehTypeFrags),
     'vehDossiersCut': ('d', getVehDossiersCutFmtValues, unpackVehDossiersCut)}


def _set_RECORD_DEPENDENCIES():
    global _RECORD_DEPENDENCIES
    _RECORD_DEPENDENCIES = {'battleHeroes': (('warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout'), _updateBattleHeroes),
     'medalKay': (('battleHeroes',), _updateMedalKay),
     'medalCarius': (('frags',), _updateMedalCarius),
     'medalKnispel': (('damageDealt', 'damageReceived'), _updateMedalKnispel),
     'medalPoppel': (('spotted',), _updateMedalPoppel),
     'medalAbrams': (('winAndSurvived',), _updateMedalAbrams),
     'medalLeClerc': (('capturePoints',), _updateMedalLeClerc),
     'medalLavrinenko': (('droppedCapturePoints',), _updateMedalLavrinenko),
     'medalEkins': (('frags8p',), _updateMedalEkins),
     'beasthunter': (('fragsBeast',), _updateBeasthunter),
     'maxSniperSeries': (('sniperSeries',), _updateMaxSniperSeries),
     'titleSniper': (('maxSniperSeries',), _updateTitleSniper),
     'maxInvincibleSeries': (('invincibleSeries',), _updateMaxInvincibleSeries),
     'invincible': (('maxInvincibleSeries',), _updateInvincible),
     'maxDiehardSeries': (('diehardSeries',), _updateMaxDiehardSeries),
     'diehard': (('maxDiehardSeries',), _updateDiehard),
     'maxKillingSeries': (('killingSeries',), _updateMaxKillingSeries),
     'handOfDeath': (('maxKillingSeries',), _updateHandOfDeath),
     'maxPiercingSeries': (('piercingSeries',), _updateMaxPiercingSeries),
     'armorPiercer': (('maxPiercingSeries',), _updateArmorPiercer),
     'lumberjack': (('treesCut',), _updateLumberjack),
     'mousebane': (('vehTypeFrags',), _updateMousebane),
     'tankExpert': (('vehTypeFrags',), _updateTankExpert)}


def _set_ACCOUNT_RECORD_DEPENDENCIES():
    global _ACCOUNT_RECORD_DEPENDENCIES
    global _ACCOUNT_RECORD_DEPENDENCIES2
    _ACCOUNT_RECORD_DEPENDENCIES = dict(_RECORD_DEPENDENCIES)
    _ACCOUNT_RECORD_DEPENDENCIES.update({})
    _ACCOUNT_RECORD_DEPENDENCIES2 = _buildDependencies2(_ACCOUNT_RECORD_DEPENDENCIES)


def _set_VEHICLE_RECORD_DEPENDENCIES():
    global _VEHICLE_RECORD_DEPENDENCIES2
    global _VEHICLE_RECORD_DEPENDENCIES
    _VEHICLE_RECORD_DEPENDENCIES = dict(_RECORD_DEPENDENCIES)
    _VEHICLE_RECORD_DEPENDENCIES.update({})
    _VEHICLE_RECORD_DEPENDENCIES2 = _buildDependencies2(_VEHICLE_RECORD_DEPENDENCIES)


def _set_TANKMAN_RECORD_DEPENDENCIES():
    global _TANKMAN_RECORD_DEPENDENCIES2
    global _TANKMAN_RECORD_DEPENDENCIES
    _TANKMAN_RECORD_DEPENDENCIES = dict({})
    _TANKMAN_RECORD_DEPENDENCIES.update({})
    _TANKMAN_RECORD_DEPENDENCIES2 = _buildDependencies2(_TANKMAN_RECORD_DEPENDENCIES)


def _set_ACCOUNT_RECORDS_LAYOUT():
    global _ACCOUNT_RECORDS_LAYOUT
    _ACCOUNT_RECORDS_LAYOUT = (['_version',
      'creationTime',
      'maxXPVehicle',
      'maxFragsVehicle',
      'lastBattleTime',
      'battleLifeTime',
      'maxFrags',
      'xp',
      'maxXP',
      'battlesCount',
      'wins',
      'losses',
      'survivedBattles',
      'winAndSurvived',
      'frags',
      'frags8p',
      'fragsBeast',
      'shots',
      'hits',
      'spotted',
      'damageDealt',
      'damageReceived',
      'treesCut',
      'capturePoints',
      'droppedCapturePoints',
      'sniperSeries',
      'maxSniperSeries',
      'invincibleSeries',
      'maxInvincibleSeries',
      'diehardSeries',
      'maxDiehardSeries',
      'killingSeries',
      'maxKillingSeries',
      'piercingSeries',
      'maxPiercingSeries',
      'battleHeroes',
      'warrior',
      'invader',
      'sniper',
      'defender',
      'steelwall',
      'supporter',
      'scout',
      'evileye',
      'medalKay',
      'medalCarius',
      'medalKnispel',
      'medalPoppel',
      'medalAbrams',
      'medalLeClerc',
      'medalLavrinenko',
      'medalEkins',
      'medalWittmann',
      'medalOrlik',
      'medalOskin',
      'medalHalonen',
      'medalBurda',
      'medalBillotte',
      'medalKolobanov',
      'medalFadin',
      'medalHeroesOfRassenai',
      'medalDeLaglanda',
      'medalTamadaYoshio',
      'medalErohin',
      'medalHoroshilov',
      'medalLister',
      'beasthunter',
      'mousebane',
      'tankExpert',
      'titleSniper',
      'invincible',
      'diehard',
      'raider',
      'handOfDeath',
      'armorPiercer',
      'kamikaze',
      'lumberjack',
      'company/xp',
      'company/battlesCount',
      'company/wins',
      'company/losses',
      'company/survivedBattles',
      'company/frags',
      'company/shots',
      'company/hits',
      'company/spotted',
      'company/damageDealt',
      'company/damageReceived',
      'company/capturePoints',
      'company/droppedCapturePoints',
      'clan/xp',
      'clan/battlesCount',
      'clan/wins',
      'clan/losses',
      'clan/survivedBattles',
      'clan/frags',
      'clan/shots',
      'clan/hits',
      'clan/spotted',
      'clan/damageDealt',
      'clan/damageReceived',
      'clan/capturePoints',
      'clan/droppedCapturePoints',
      '_dynRecPos_account'], ['vehTypeFrags', 'vehDossiersCut'])
    extendRecordPacking(_ACCOUNT_RECORDS_LAYOUT, '_dynRecPos_account', _RECORD_PACKING)


def _set_VEHICLE_RECORDS_LAYOUT():
    global _VEHICLE_RECORDS_LAYOUT
    _VEHICLE_RECORDS_LAYOUT = (['_version',
      'lastBattleTime',
      'battleLifeTime',
      'maxFrags',
      'xp',
      'maxXP',
      'battlesCount',
      'wins',
      'losses',
      'survivedBattles',
      'winAndSurvived',
      'frags',
      'frags8p',
      'fragsBeast',
      'shots',
      'hits',
      'spotted',
      'damageDealt',
      'damageReceived',
      'treesCut',
      'capturePoints',
      'droppedCapturePoints',
      'sniperSeries',
      'maxSniperSeries',
      'invincibleSeries',
      'maxInvincibleSeries',
      'diehardSeries',
      'maxDiehardSeries',
      'killingSeries',
      'maxKillingSeries',
      'piercingSeries',
      'maxPiercingSeries',
      'battleHeroes',
      'warrior',
      'invader',
      'sniper',
      'defender',
      'steelwall',
      'supporter',
      'scout',
      'evileye',
      'medalKay',
      'medalCarius',
      'medalKnispel',
      'medalPoppel',
      'medalAbrams',
      'medalLeClerc',
      'medalLavrinenko',
      'medalEkins',
      'medalWittmann',
      'medalOrlik',
      'medalOskin',
      'medalHalonen',
      'medalBurda',
      'medalBillotte',
      'medalKolobanov',
      'medalFadin',
      'medalHeroesOfRassenai',
      'medalDeLaglanda',
      'medalTamadaYoshio',
      'medalErohin',
      'medalHoroshilov',
      'medalLister',
      'beasthunter',
      'mousebane',
      'tankExpert',
      'titleSniper',
      'invincible',
      'diehard',
      'raider',
      'handOfDeath',
      'armorPiercer',
      'kamikaze',
      'lumberjack',
      'markOfMastery',
      'company/xp',
      'company/battlesCount',
      'company/wins',
      'company/losses',
      'company/survivedBattles',
      'company/frags',
      'company/shots',
      'company/hits',
      'company/spotted',
      'company/damageDealt',
      'company/damageReceived',
      'company/capturePoints',
      'company/droppedCapturePoints',
      'clan/xp',
      'clan/battlesCount',
      'clan/wins',
      'clan/losses',
      'clan/survivedBattles',
      'clan/frags',
      'clan/shots',
      'clan/hits',
      'clan/spotted',
      'clan/damageDealt',
      'clan/damageReceived',
      'clan/capturePoints',
      'clan/droppedCapturePoints',
      '_dynRecPos_vehicle'], ['vehTypeFrags'])
    extendRecordPacking(_VEHICLE_RECORDS_LAYOUT, '_dynRecPos_vehicle', _RECORD_PACKING)


def _set_TANKMAN_RECORDS_LAYOUT():
    global _TANKMAN_RECORDS_LAYOUT
    _TANKMAN_RECORDS_LAYOUT = (['_version',
      'battlesCount',
      'warrior',
      'invader',
      'sniper',
      'defender',
      'steelwall',
      'supporter',
      'scout',
      'evileye',
      'medalWittmann',
      'medalOrlik',
      'medalOskin',
      'medalHalonen',
      'medalBurda',
      'medalBillotte',
      'medalKolobanov',
      'medalFadin',
      'medalHeroesOfRassenai',
      'medalDeLaglanda',
      'medalTamadaYoshio',
      'medalErohin',
      'medalHoroshilov',
      'medalLister',
      '_dynRecPos_tankman'], [])
    extendRecordPacking(_TANKMAN_RECORDS_LAYOUT, '_dynRecPos_tankman', _RECORD_PACKING)


def _set_STATIC_RECORD_POSITIONS():
    global _ACCOUNT_STATIC_RECORD_POSITIONS
    global _TANKMAN_STATIC_RECORD_POSITIONS
    global _VEHICLE_STATIC_RECORD_POSITIONS
    _ACCOUNT_STATIC_RECORD_POSITIONS = buildStaticRecordPositions(_ACCOUNT_RECORDS_LAYOUT, _RECORD_PACKING)
    _VEHICLE_STATIC_RECORD_POSITIONS = buildStaticRecordPositions(_VEHICLE_RECORDS_LAYOUT, _RECORD_PACKING)
    _TANKMAN_STATIC_RECORD_POSITIONS = buildStaticRecordPositions(_TANKMAN_RECORDS_LAYOUT, _RECORD_PACKING)


def _set_STATIC_RECORDS_FMT():
    global _TANKMAN_STATIC_RECORDS_FMT
    global _ACCOUNT_STATIC_RECORDS_FMT
    global _VEHICLE_STATIC_RECORDS_FMT
    _ACCOUNT_STATIC_RECORDS_FMT = buildStaticRecordsFmt(_ACCOUNT_RECORDS_LAYOUT, _RECORD_PACKING)
    _VEHICLE_STATIC_RECORDS_FMT = buildStaticRecordsFmt(_VEHICLE_RECORDS_LAYOUT, _RECORD_PACKING)
    _TANKMAN_STATIC_RECORDS_FMT = buildStaticRecordsFmt(_TANKMAN_RECORDS_LAYOUT, _RECORD_PACKING)


def getAccountDossierDescr(compDescr=''):
    return _DossierDescr(compDescr, _ACCOUNT_RECORDS_LAYOUT, '_dynRecPos_account', _ACCOUNT_STATIC_RECORD_POSITIONS, _ACCOUNT_STATIC_RECORDS_FMT, _ACCOUNT_RECORD_DEPENDENCIES2, ACCOUNT_DOSSIER_VERSION, _ACCOUNT_DOSSIER_UPDATERS)


def getVehicleDossierDescr(compDescr=''):
    return _DossierDescr(compDescr, _VEHICLE_RECORDS_LAYOUT, '_dynRecPos_vehicle', _VEHICLE_STATIC_RECORD_POSITIONS, _VEHICLE_STATIC_RECORDS_FMT, _VEHICLE_RECORD_DEPENDENCIES2, VEHICLE_DOSSIER_VERSION, _VEHICLE_DOSSIER_UPDATERS)


def getTankmanDossierDescr(compDescr=''):
    return _DossierDescr(compDescr, _TANKMAN_RECORDS_LAYOUT, '_dynRecPos_tankman', _TANKMAN_STATIC_RECORD_POSITIONS, _TANKMAN_STATIC_RECORDS_FMT, _TANKMAN_RECORD_DEPENDENCIES2, TANKMAN_DOSSIER_VERSION, _TANKMAN_DOSSIER_UPDATERS)


def getDossierDescr(dossierType, compDescr=''):
    if dossierType == DOSSIER_TYPE.VEHICLE:
        return getVehicleDossierDescr(compDescr)
    elif dossierType == DOSSIER_TYPE.TANKMAN:
        return getTankmanDossierDescr(compDescr)
    elif dossierType == DOSSIER_TYPE.ACCOUNT:
        return getAccountDossierDescr(compDescr)
    else:
        return None


def getRecordMaxValue(record):
    recordPacking = _RECORD_PACKING[record]
    assert recordPacking[0] == 'p'
    return recordPacking[3]


def _buildDependencies2(dependencies):
    dependencies2 = collections.defaultdict(list)
    for record, (affectingRecords, updater) in dependencies.iteritems():
        for affectingRecord in affectingRecords:
            dependencies2[affectingRecord].append(updater)

    return dependencies2


def _updateBattleHeroes(dossierDescr, affectingRecord, value, prevValue):
    dossierDescr['battleHeroes'] = dossierDescr['battleHeroes'] + value - prevValue


def _updateMedalKay(dossierDescr, affectingRecord, value, prevValue):
    medalKayCfg = RECORD_CONFIGS['medalKay']
    battleHeroes = dossierDescr['battleHeroes']
    maxMedalClass = len(medalKayCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if battleHeroes >= medalKayCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalKay']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalKay'] = medalClass


def _updateMedalCarius(dossierDescr, affectingRecord, value, prevValue):
    medalCariusCfg = RECORD_CONFIGS['medalCarius']
    frags = dossierDescr['frags']
    maxMedalClass = len(medalCariusCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if frags >= medalCariusCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalCarius']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalCarius'] = medalClass


def _updateMedalKnispel(dossierDescr, affectingRecord, value, prevValue):
    medalKnispelCfg = RECORD_CONFIGS['medalKnispel']
    damageDealt = dossierDescr['damageDealt']
    damageReceived = dossierDescr['damageReceived']
    maxMedalClass = len(medalKnispelCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if damageDealt + damageReceived >= medalKnispelCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalKnispel']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalKnispel'] = medalClass


def _updateMedalPoppel(dossierDescr, affectingRecord, value, prevValue):
    medalPoppelCfg = RECORD_CONFIGS['medalPoppel']
    spotted = dossierDescr['spotted']
    maxMedalClass = len(medalPoppelCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if spotted >= medalPoppelCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalPoppel']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalPoppel'] = medalClass


def _updateMedalAbrams(dossierDescr, affectingRecord, value, prevValue):
    medalAbramsCfg = RECORD_CONFIGS['medalAbrams']
    winAndSurvived = dossierDescr['winAndSurvived']
    maxMedalClass = len(medalAbramsCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if winAndSurvived >= medalAbramsCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalAbrams']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalAbrams'] = medalClass


def _updateMedalLeClerc(dossierDescr, affectingRecord, value, prevValue):
    medalLeClercCfg = RECORD_CONFIGS['medalLeClerc']
    capturePoints = dossierDescr['capturePoints']
    maxMedalClass = len(medalLeClercCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if capturePoints >= medalLeClercCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalLeClerc']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalLeClerc'] = medalClass


def _updateMedalLavrinenko(dossierDescr, affectingRecord, value, prevValue):
    medalLavrinenkoCfg = RECORD_CONFIGS['medalLavrinenko']
    droppedCapturePoints = dossierDescr['droppedCapturePoints']
    maxMedalClass = len(medalLavrinenkoCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if droppedCapturePoints >= medalLavrinenkoCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalLavrinenko']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalLavrinenko'] = medalClass


def _updateMedalEkins(dossierDescr, affectingRecord, value, prevValue):
    medalEkinsCfg = RECORD_CONFIGS['medalEkins']
    frags = dossierDescr['frags8p']
    maxMedalClass = len(medalEkinsCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if frags >= medalEkinsCfg[maxMedalClass - medalClass]:
            break
    else:
        return

    curClass = dossierDescr['medalEkins']
    if curClass == 0 or curClass > medalClass:
        dossierDescr['medalEkins'] = medalClass


def _updateBeasthunter(dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['beasthunter']
    beastFrags = dossierDescr['fragsBeast']
    medals, series = divmod(beastFrags, minFrags)
    if dossierDescr['beasthunter'] != medals:
        dossierDescr['beasthunter'] = medals


def _updateMousebane(dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['mousebane']
    mausFrags = dossierDescr['vehTypeFrags'].get(_g_cache['mausTypeCompDescr'], 0)
    medals, series = divmod(mausFrags, minFrags)
    if dossierDescr['mousebane'] != medals:
        dossierDescr['mousebane'] = medals


def _updateTankExpert(dossierDescr, affectingRecord, value, prevValue):
    treeVehiclesFragged = 0
    for compactDescr in dossierDescr['vehTypeFrags'].iterkeys():
        if compactDescr in _g_cache['vehiclesInTrees']:
            treeVehiclesFragged += 1

    if treeVehiclesFragged == len(_g_cache['vehiclesInTrees']):
        dossierDescr['tankExpert'] = 1


def _updateMaxSniperSeries(dossierDescr, affectingRecord, value, prevValue):
    maxSniperSeries = dossierDescr['maxSniperSeries']
    if dossierDescr['sniperSeries'] > maxSniperSeries:
        dossierDescr['maxSniperSeries'] = dossierDescr['sniperSeries']


def _updateTitleSniper(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['titleSniper']
    if dossierDescr['maxSniperSeries'] >= minLength:
        dossierDescr['titleSniper'] = 1


def _updateMaxInvincibleSeries(dossierDescr, affectingRecord, value, prevValue):
    maxInvincibleSeries = dossierDescr['maxInvincibleSeries']
    if dossierDescr['invincibleSeries'] > maxInvincibleSeries:
        dossierDescr['maxInvincibleSeries'] = dossierDescr['invincibleSeries']


def _updateInvincible(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['invincible']
    if dossierDescr['maxInvincibleSeries'] >= minLength:
        dossierDescr['invincible'] = 1


def _updateMaxDiehardSeries(dossierDescr, affectingRecord, value, prevValue):
    maxDiehardSeries = dossierDescr['maxDiehardSeries']
    if dossierDescr['diehardSeries'] > maxDiehardSeries:
        dossierDescr['maxDiehardSeries'] = dossierDescr['diehardSeries']


def _updateDiehard(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['diehard']
    if dossierDescr['maxDiehardSeries'] >= minLength:
        dossierDescr['diehard'] = 1


def _updateMaxKillingSeries(dossierDescr, affectingRecord, value, prevValue):
    maxKillingSeries = dossierDescr['maxKillingSeries']
    if dossierDescr['killingSeries'] > maxKillingSeries:
        dossierDescr['maxKillingSeries'] = dossierDescr['killingSeries']


def _updateHandOfDeath(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['handOfDeath']
    if dossierDescr['maxKillingSeries'] >= minLength:
        dossierDescr['handOfDeath'] = 1


def _updateMaxPiercingSeries(dossierDescr, affectingRecord, value, prevValue):
    maxPiercingSeries = dossierDescr['maxPiercingSeries']
    if dossierDescr['piercingSeries'] > maxPiercingSeries:
        dossierDescr['maxPiercingSeries'] = dossierDescr['piercingSeries']


def _updateArmorPiercer(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['armorPiercer']
    if dossierDescr['maxPiercingSeries'] >= minLength:
        dossierDescr['armorPiercer'] = 1


def _updateLumberjack(dossierDescr, affectingRecord, value, prevValue):
    minTrees = RECORD_CONFIGS['lumberjack']
    if dossierDescr['treesCut'] >= minTrees:
        dossierDescr['lumberjack'] = 1


def _set_ACCOUNT_DOSSIER_UPDATERS():
    global _ACCOUNT_DOSSIER_UPDATERS
    _ACCOUNT_DOSSIER_UPDATERS = {0: partial(getNewAccountDossierData, ACCOUNT_DOSSIER_VERSION, _ACCOUNT_RECORDS_LAYOUT),
     19: partial(updateDossier1, 20, DOSSIER_TYPE.ACCOUNT),
     20: partial(updateDossier3, 21, DOSSIER_TYPE.ACCOUNT)}


def _set_VEHICLE_DOSSIER_UPDATERS():
    global _VEHICLE_DOSSIER_UPDATERS
    _VEHICLE_DOSSIER_UPDATERS = {0: partial(getNewDossierData, VEHICLE_DOSSIER_VERSION, _VEHICLE_RECORDS_LAYOUT),
     17: partial(updateDossier1, 18, DOSSIER_TYPE.VEHICLE),
     18: partial(updateDossier2, 19, DOSSIER_TYPE.VEHICLE),
     19: partial(updateDossier3, 20, DOSSIER_TYPE.VEHICLE)}


def _set_TANKMAN_DOSSIER_UPDATERS():
    global _TANKMAN_DOSSIER_UPDATERS
    _TANKMAN_DOSSIER_UPDATERS = {0: partial(getNewDossierData, TANKMAN_DOSSIER_VERSION, _TANKMAN_RECORDS_LAYOUT),
     10: partial(updateDossier1, 11, DOSSIER_TYPE.TANKMAN)}


class _DossierDescr(object):

    def __init__(self, compDescr, recordsLayout, dynRecPosRecord, staticRecordPositions, staticRecordsFmt, dependencies, curVersion, versionUpdaters):
        if len(compDescr) < 2:
            self.__compDescr = '\x00\x00'
        else:
            self.__compDescr = compDescr
        self._recordsLayout = recordsLayout
        self.__dynRecPosRecord = dynRecPosRecord
        self.__staticRecordPositions = staticRecordPositions
        self.__staticRecordsFmt = staticRecordsFmt
        self.__dependencies = dependencies
        self.__curVersion = curVersion
        self.__versionUpdaters = versionUpdaters
        self.__isExpanded = False
        self.__dependentUpdates = 0
        self.__data = {}
        self.__changed = set([])
        self.notified = set([])
        self.__updateVersion()

    def __getitem__(self, record):
        if record in self.__data:
            return self.__data[record]
        if record in self._recordsLayout[0]:
            packing = _RECORD_PACKING[record]
            position = self.__staticRecordPositions[record]
            values = unpack('<' + packing[1], self.__compDescr[position:position + packing[2]])
            if packing[0] == 'p':
                self.__data[record] = values[0]
            else:
                self.__data[record] = packing[5](values)
            return self.__data[record]
        packing = _RECORD_PACKING[record]
        dynRecIdx = self._recordsLayout[1].index(record)
        offset = self[self.__dynRecPosRecord][dynRecIdx]
        self.__data[record], _ = packing[2](self.__compDescr, offset)
        return self.__data[record]

    def __setitem__(self, record, value):
        packing = _RECORD_PACKING[record]
        if packing[0] == 'p':
            value = min(value, packing[3])
        prevValue = self[record]
        if record in POP_UP_RECORDS:
            if value != prevValue or record in EVENT_RECORDS:
                self.notified.add(record)
        if value == prevValue:
            return
        self.__data[record] = value
        self.__changed.add(record)
        isFromOutside = self.__dependentUpdates == 0
        self.__dependentUpdates += 1
        if self.__dependentUpdates >= 100:
            LOG_ERROR('Too many subsequent updates of dependent records')
            return
        for updater in self.__dependencies[record]:
            updater(self, record, value, prevValue)

        if isFromOutside:
            self.__dependentUpdates = 0

    def __iter__(self):
        return _DossierDescrIterator(self)

    def update(self, d):
        for key, value in d.iteritems():
            self[key] = value

    def expand(self):
        if self.__isExpanded:
            return
        data = self.__data
        prevData = dict(data)
        fmt = self.__staticRecordsFmt
        offset = self.__staticRecordPositions['_staticRecordsSize']
        values = unpack(fmt, self.__compDescr[:offset])
        index = 0
        for record in self._recordsLayout[0]:
            packing = _RECORD_PACKING[record]
            if packing[0] == 'p':
                self.__data[record] = values[index]
                index += 1
            else:
                self.__data[record] = packing[5](values[index:index + packing[3]])
                index += packing[3]

        for record in self._recordsLayout[1]:
            packing = _RECORD_PACKING[record]
            self.__data[record], offset = packing[2](self.__compDescr, offset)

        data.update(prevData)
        self.__isExpanded = True

    def makeCompDescr(self):
        if not self.__changed:
            return self.__compDescr
        data = self.__data
        if self.__isExpanded:
            dynRecordsFmt = ''
            dynRecordsValues = []
            dynRecOffset = self.__staticRecordPositions['_staticRecordsSize']
            dynRecPos = list(data[self.__dynRecPosRecord])
            for i in xrange(len(self._recordsLayout[1])):
                record = self._recordsLayout[1][i]
                packing = _RECORD_PACKING[record]
                dynRecPos[i] = dynRecOffset
                recFmt, recValues, recSize = packing[1](data[record])
                dynRecordsFmt += recFmt
                dynRecordsValues += recValues
                dynRecOffset += recSize

            data[self.__dynRecPosRecord] = dynRecPos
            fmt = '<'
            values = []
            for record in self._recordsLayout[0]:
                packing = _RECORD_PACKING[record]
                fmt += packing[1]
                if packing[0] == 'p':
                    values.append(data[record])
                else:
                    values += packing[4](data[record])

            self.__compDescr = pack((fmt + dynRecordsFmt), *(values + dynRecordsValues))
        else:
            while 1:
                changed = self.__changed and list(self.__changed)
                self.__changed.clear()
                for record in changed:
                    packing = _RECORD_PACKING[record]
                    if packing[0] == 'p':
                        substr = pack('<' + packing[1], data[record])
                        prevSize = packing[2]
                        position = self.__staticRecordPositions[record]
                    elif packing[0] == 's':
                        substr = pack(('<' + packing[1]), *packing[4](data[record]))
                        prevSize = packing[2]
                        position = self.__staticRecordPositions[record]
                    else:
                        fmt, values, size = packing[1](data[record])
                        substr = pack(('<' + fmt), *values)
                        dynRecIdx = self._recordsLayout[1].index(record)
                        dynRecPosExt = self[self.__dynRecPosRecord] + (len(self.__compDescr),)
                        position = dynRecPosExt[dynRecIdx]
                        prevSize = dynRecPosExt[dynRecIdx + 1] - position
                        sizeDiff = size - prevSize
                        if sizeDiff != 0:
                            dynRecPos = list(dynRecPosExt[:-1])
                            for i in xrange(dynRecIdx + 1, len(self._recordsLayout[1])):
                                dynRecPos[i] += sizeDiff

                            self[self.__dynRecPosRecord] = tuple(dynRecPos)
                    self.__compDescr = self.__compDescr[:position] + substr + self.__compDescr[position + prevSize:]

        self.__changed.clear()
        self.notified.clear()
        return self.__compDescr

    def __updateVersion(self):
        while 1:
            ver = True and self['_version']
            if ver == self.__curVersion:
                break
            updater = self.__versionUpdaters.get(ver, self.__versionUpdaters[0])
            self.__data, self.__compDescr = updater(self.__isExpanded, self.__compDescr, self.__data)
            self.__isExpanded = True
            self.__changed.add('_version')


class _DossierDescrIterator(object):

    def __init__(self, dossierDescr):
        self.__dossierDescr = dossierDescr
        self.__dossierDescr.expand()
        self.__recordNames = dossierDescr._recordsLayout[0] + dossierDescr._recordsLayout[1]
        self.__recordIdx = 0

    def next(self):
        if self.__recordIdx >= len(self.__recordNames):
            raise StopIteration
        record = self.__recordNames[self.__recordIdx]
        self.__recordIdx += 1
        return (record, self.__dossierDescr[record])


def init():
    global _g_cache
    _set_RECORD_PACKING()
    _set_RECORD_DEPENDENCIES()
    _set_ACCOUNT_RECORD_DEPENDENCIES()
    _set_VEHICLE_RECORD_DEPENDENCIES()
    _set_TANKMAN_RECORD_DEPENDENCIES()
    _set_ACCOUNT_RECORDS_LAYOUT()
    _set_VEHICLE_RECORDS_LAYOUT()
    _set_TANKMAN_RECORDS_LAYOUT()
    _set_STATIC_RECORD_POSITIONS()
    _set_STATIC_RECORDS_FMT()
    _set_ACCOUNT_DOSSIER_UPDATERS()
    _set_VEHICLE_DOSSIER_UPDATERS()
    _set_TANKMAN_DOSSIER_UPDATERS()
    _g_cache = _buildCache()


def _buildCache():
    vehicles8p = set()
    beastVehicles = set()
    vehiclesInTrees = set()
    unlocksSources = vehicles.getUnlocksSources()
    for nationIdx in xrange(len(nations.NAMES)):
        nationList = vehicles.g_list.getList(nationIdx)
        for vehDescr in nationList.itervalues():
            if vehDescr['level'] >= 8:
                vehicles8p.add(vehDescr['compactDescr'])
            if 'beast' in vehDescr['tags']:
                beastVehicles.add(vehDescr['compactDescr'])
            if len(unlocksSources.get(vehDescr['compactDescr'], set())) > 0 or len(vehicles.g_cache.vehicle(nationIdx, vehDescr['id']).unlocksDescrs) > 0:
                vehiclesInTrees.add(vehDescr['compactDescr'])

    return {'vehicles8+': vehicles8p,
     'beastVehicles': beastVehicles,
     'mausTypeCompDescr': vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName('germany:Maus')),
     'vehiclesInTrees': vehiclesInTrees}
