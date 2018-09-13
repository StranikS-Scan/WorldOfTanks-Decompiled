# Embedded file name: scripts/common/dossiers1/__init__.py
import nations
from struct import *
from debug_utils import *
from items import vehicles
from functools import partial
from constants import DOSSIER_TYPE
from dossiers1.config import RECORD_CONFIGS
from dossier_updaters import *
from utils import *
from dependences import *
ACCOUNT_DOSSIER_VERSION = 32
VEHICLE_DOSSIER_VERSION = 29
TANKMAN_DOSSIER_VERSION = 14
RECORD_NAMES = ('reserved', 'xp', 'maxXP', 'battlesCount', 'wins', 'losses', 'survivedBattles', 'lastBattleTime', 'battleLifeTime', 'winAndSurvived', 'battleHeroes', 'frags', 'maxFrags', 'frags8p', 'fragsBeast', 'shots', 'directHits', 'spotted', 'damageDealt', 'damageReceived', 'treesCut', 'capturePoints', 'droppedCapturePoints', 'sniperSeries', 'maxSniperSeries', 'invincibleSeries', 'maxInvincibleSeries', 'diehardSeries', 'maxDiehardSeries', 'killingSeries', 'maxKillingSeries', 'piercingSeries', 'maxPiercingSeries', 'vehTypeFrags', 'warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout', 'medalKay', 'medalCarius', 'medalKnispel', 'medalPoppel', 'medalAbrams', 'medalLeClerc', 'medalLavrinenko', 'medalEkins', 'medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin', 'tankExpert', 'titleSniper', 'invincible', 'diehard', 'raider', 'handOfDeath', 'armorPiercer', 'kamikaze', 'lumberjack', 'beasthunter', 'mousebane', 'creationTime', 'maxXPVehicle', 'maxFragsVehicle', 'a15x15Cut', 'evileye', 'medalRadleyWalters', 'medalLafayettePool', 'medalBrunoPietro', 'medalTarczay', 'medalPascucci', 'medalDumitru', 'markOfMastery', 'company/xp', 'company/battlesCount', 'company/wins', 'company/losses', 'company/survivedBattles', 'company/frags', 'company/shots', 'company/directHits', 'company/spotted', 'company/damageDealt', 'company/damageReceived', 'company/capturePoints', 'company/droppedCapturePoints', 'clan/xp', 'clan/battlesCount', 'clan/wins', 'clan/losses', 'clan/survivedBattles', 'clan/frags', 'clan/shots', 'clan/directHits', 'clan/spotted', 'clan/damageDealt', 'clan/damageReceived', 'clan/capturePoints', 'clan/droppedCapturePoints', 'medalLehvaslaiho', 'medalNikolas', 'fragsSinai', 'sinai', 'heroesOfRassenay', 'mechanicEngineer', 'tankExpert0', 'tankExpert1', 'tankExpert2', 'tankExpert3', 'tankExpert4', 'tankExpert5', 'tankExpert6', 'tankExpert7', 'tankExpert8', 'tankExpert9', 'tankExpert10', 'tankExpert11', 'tankExpert12', 'tankExpert13', 'tankExpert14', 'mechanicEngineer0', 'mechanicEngineer1', 'mechanicEngineer2', 'mechanicEngineer3', 'mechanicEngineer4', 'mechanicEngineer5', 'mechanicEngineer6', 'mechanicEngineer7', 'mechanicEngineer8', 'mechanicEngineer9', 'mechanicEngineer10', 'mechanicEngineer11', 'mechanicEngineer12', 'mechanicEngineer13', 'mechanicEngineer14', 'rareAchievements', 'medalBrothersInArms', 'medalCrucialContribution', 'medalDeLanglade', 'medalTamadaYoshio', 'bombardier', 'huntsman', 'alaric', 'sturdy', 'ironMan', 'luckyDevil', 'fragsPatton', 'pattonValley', 'xpBefore8_8', 'battlesCountBefore8_8', 'originalXP', 'damageAssistedTrack', 'damageAssistedRadio', 'mileage', 'directHitsReceived', 'noDamageDirectHitsReceived', 'piercingsReceived', 'explosionHitsReceived', 'explosionHits', 'piercings')
RECORD_INDICES = dict(((x[1], x[0]) for x in enumerate(RECORD_NAMES)))
_ACCOUNT_POP_UP_RECORDS = set(['warrior',
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
 'evileye',
 'medalRadleyWalters',
 'medalLafayettePool',
 'medalBrunoPietro',
 'medalTarczay',
 'medalPascucci',
 'medalDumitru',
 'medalLehvaslaiho',
 'medalNikolas',
 'sinai',
 'pattonValley',
 'heroesOfRassenay',
 'mechanicEngineer',
 'tankExpert0',
 'tankExpert1',
 'tankExpert2',
 'tankExpert3',
 'tankExpert4',
 'tankExpert5',
 'tankExpert6',
 'tankExpert7',
 'tankExpert8',
 'tankExpert9',
 'tankExpert10',
 'tankExpert11',
 'tankExpert12',
 'tankExpert13',
 'tankExpert14',
 'mechanicEngineer0',
 'mechanicEngineer1',
 'mechanicEngineer2',
 'mechanicEngineer3',
 'mechanicEngineer4',
 'mechanicEngineer5',
 'mechanicEngineer6',
 'mechanicEngineer7',
 'mechanicEngineer8',
 'mechanicEngineer9',
 'mechanicEngineer10',
 'mechanicEngineer11',
 'mechanicEngineer12',
 'mechanicEngineer13',
 'mechanicEngineer14',
 'medalBrothersInArms',
 'medalCrucialContribution',
 'medalDeLanglade',
 'medalTamadaYoshio',
 'bombardier',
 'huntsman',
 'alaric',
 'sturdy',
 'ironMan',
 'luckyDevil',
 'maxXP'])
_VEHICLE_POP_UP_RECORDS = set(['beasthunter',
 'mousebane',
 'tankExpert',
 'titleSniper',
 'invincible',
 'diehard',
 'handOfDeath',
 'armorPiercer',
 'markOfMastery',
 'sinai',
 'tankExpert0',
 'tankExpert1',
 'tankExpert2',
 'tankExpert3',
 'tankExpert4',
 'tankExpert5',
 'tankExpert6',
 'tankExpert7',
 'tankExpert8',
 'tankExpert9',
 'tankExpert10',
 'tankExpert11',
 'tankExpert12',
 'tankExpert13',
 'tankExpert14',
 'maxXP',
 'pattonValley'])
_TANKMAN_POP_UP_RECORDS = set()

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
     'fragsSinai': ('p', 'I', 4, 4000000001L),
     'shots': ('p', 'I', 4, 4000000001L),
     'company/shots': ('p', 'I', 4, 4000000001L),
     'clan/shots': ('p', 'I', 4, 4000000001L),
     'directHits': ('p', 'I', 4, 4000000001L),
     'company/directHits': ('p', 'I', 4, 4000000001L),
     'clan/directHits': ('p', 'I', 4, 4000000001L),
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
     'medalRadleyWalters': ('p', 'H', 2, 60001),
     'medalLafayettePool': ('p', 'H', 2, 60001),
     'heroesOfRassenay': ('p', 'H', 2, 60001),
     'medalBrunoPietro': ('p', 'H', 2, 60001),
     'medalTarczay': ('p', 'H', 2, 60001),
     'medalPascucci': ('p', 'H', 2, 60001),
     'medalDumitru': ('p', 'H', 2, 60001),
     'medalLehvaslaiho': ('p', 'H', 2, 60001),
     'medalNikolas': ('p', 'H', 2, 60001),
     'beasthunter': ('p', 'H', 2, 60001),
     'sinai': ('p', 'H', 2, 60001),
     'mousebane': ('p', 'H', 2, 60001),
     'tankExpertStrg': ('p', 'H', 2, 65535),
     'mechanicEngineerStrg': ('p', 'H', 2, 65535),
     'titleSniper': ('p', 'B', 1, 1),
     'invincible': ('p', 'B', 1, 1),
     'diehard': ('p', 'B', 1, 1),
     'raider': ('p', 'H', 2, 60001),
     'handOfDeath': ('p', 'B', 1, 1),
     'armorPiercer': ('p', 'B', 1, 1),
     'kamikaze': ('p', 'H', 2, 60001),
     'lumberjack': ('p', 'H', 2, 60001),
     'markOfMastery': ('p', 'B', 1, 4),
     'vehTypeFrags': ('d', getVehTypeFragsFmtValues, unpackVehTypeFrags),
     'a15x15Cut': ('d', getA15x15CutFmtValues, unpackA15x15Cut),
     'tankExpert': ('b', 'tankExpertStrg', 0),
     'tankExpert0': ('b', 'tankExpertStrg', 1),
     'tankExpert1': ('b', 'tankExpertStrg', 2),
     'tankExpert2': ('b', 'tankExpertStrg', 3),
     'tankExpert3': ('b', 'tankExpertStrg', 4),
     'tankExpert4': ('b', 'tankExpertStrg', 5),
     'tankExpert5': ('b', 'tankExpertStrg', 6),
     'tankExpert6': ('b', 'tankExpertStrg', 7),
     'tankExpert7': ('b', 'tankExpertStrg', 8),
     'tankExpert8': ('b', 'tankExpertStrg', 9),
     'tankExpert9': ('b', 'tankExpertStrg', 10),
     'tankExpert10': ('b', 'tankExpertStrg', 11),
     'tankExpert11': ('b', 'tankExpertStrg', 12),
     'tankExpert12': ('b', 'tankExpertStrg', 13),
     'tankExpert13': ('b', 'tankExpertStrg', 14),
     'tankExpert14': ('b', 'tankExpertStrg', 15),
     'mechanicEngineer': ('b', 'mechanicEngineerStrg', 0),
     'mechanicEngineer0': ('b', 'mechanicEngineerStrg', 1),
     'mechanicEngineer1': ('b', 'mechanicEngineerStrg', 2),
     'mechanicEngineer2': ('b', 'mechanicEngineerStrg', 3),
     'mechanicEngineer3': ('b', 'mechanicEngineerStrg', 4),
     'mechanicEngineer4': ('b', 'mechanicEngineerStrg', 5),
     'mechanicEngineer5': ('b', 'mechanicEngineerStrg', 6),
     'mechanicEngineer6': ('b', 'mechanicEngineerStrg', 7),
     'mechanicEngineer7': ('b', 'mechanicEngineerStrg', 8),
     'mechanicEngineer8': ('b', 'mechanicEngineerStrg', 9),
     'mechanicEngineer9': ('b', 'mechanicEngineerStrg', 10),
     'mechanicEngineer10': ('b', 'mechanicEngineerStrg', 11),
     'mechanicEngineer11': ('b', 'mechanicEngineerStrg', 12),
     'mechanicEngineer12': ('b', 'mechanicEngineerStrg', 13),
     'mechanicEngineer13': ('b', 'mechanicEngineerStrg', 14),
     'mechanicEngineer14': ('b', 'mechanicEngineerStrg', 15),
     'rareAchievements': ('d', getRareAchievementsFmtValues, unpackRareAchievements),
     'medalBrothersInArms': ('p', 'H', 2, 60001),
     'medalCrucialContribution': ('p', 'H', 2, 60001),
     'medalDeLanglade': ('p', 'H', 2, 60001),
     'medalTamadaYoshio': ('p', 'H', 2, 60001),
     'bombardier': ('p', 'H', 2, 60001),
     'huntsman': ('p', 'H', 2, 60001),
     'alaric': ('p', 'H', 2, 60001),
     'sturdy': ('p', 'H', 2, 60001),
     'ironMan': ('p', 'H', 2, 60001),
     'luckyDevil': ('p', 'H', 2, 60001),
     'fragsPatton': ('p', 'I', 4, 4000000001L),
     'pattonValley': ('p', 'H', 2, 60001),
     'originalXP': ('p', 'I', 4, 4000000001L),
     'damageAssistedTrack': ('p', 'I', 4, 4000000001L),
     'damageAssistedRadio': ('p', 'I', 4, 4000000001L),
     'mileage': ('p', 'I', 4, 4000000001L),
     'directHitsReceived': ('p', 'I', 4, 4000000001L),
     'noDamageDirectHitsReceived': ('p', 'I', 4, 4000000001L),
     'piercingsReceived': ('p', 'I', 4, 4000000001L),
     'explosionHitsReceived': ('p', 'I', 4, 4000000001L),
     'explosionHits': ('p', 'I', 4, 4000000001L),
     'piercings': ('p', 'I', 4, 4000000001L),
     'xpBefore8_8': ('p', 'I', 4, 4000000001L),
     'battlesCountBefore8_8': ('p', 'I', 4, 4000000001L)}


def _set_RECORD_DEPENDENCIES():
    global _RECORD_DEPENDENCIES
    _RECORD_DEPENDENCIES = {'battleHeroes': (('warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout', 'evileye'), updateBattleHeroes),
     'medalKay': (('battleHeroes',), updateMedalKay),
     'medalCarius': (('frags',), updateMedalCarius),
     'medalKnispel': (('damageDealt', 'damageReceived'), updateMedalKnispel),
     'medalPoppel': (('spotted',), updateMedalPoppel),
     'medalAbrams': (('winAndSurvived',), updateMedalAbrams),
     'medalLeClerc': (('capturePoints',), updateMedalLeClerc),
     'medalLavrinenko': (('droppedCapturePoints',), updateMedalLavrinenko),
     'medalEkins': (('frags8p',), updateMedalEkins),
     'beasthunter': (('fragsBeast',), updateBeasthunter),
     'sinai': (('fragsSinai',), updateSinai),
     'pattonValley': (('fragsPatton',), updatePattonValley),
     'maxSniperSeries': (('sniperSeries',), updateMaxSniperSeries),
     'titleSniper': (('maxSniperSeries',), updateTitleSniper),
     'maxInvincibleSeries': (('invincibleSeries',), updateMaxInvincibleSeries),
     'invincible': (('maxInvincibleSeries',), updateInvincible),
     'maxDiehardSeries': (('diehardSeries',), updateMaxDiehardSeries),
     'diehard': (('maxDiehardSeries',), updateDiehard),
     'maxKillingSeries': (('killingSeries',), updateMaxKillingSeries),
     'handOfDeath': (('maxKillingSeries',), updateHandOfDeath),
     'maxPiercingSeries': (('piercingSeries',), updateMaxPiercingSeries),
     'armorPiercer': (('maxPiercingSeries',), updateArmorPiercer),
     'mousebane': (('vehTypeFrags',), partial(updateMousebane, g_cache)),
     'tankExpert': (('vehTypeFrags',), partial(updateTankExpert, g_cache))}


def _set_ACCOUNT_RECORD_DEPENDENCIES():
    global _ACCOUNT_RECORD_DEPENDENCIES
    global _ACCOUNT_RECORD_DEPENDENCIES2
    _ACCOUNT_RECORD_DEPENDENCIES = dict(_RECORD_DEPENDENCIES)
    _ACCOUNT_RECORD_DEPENDENCIES.update({})
    _ACCOUNT_RECORD_DEPENDENCIES2 = buildDependencies2(_ACCOUNT_RECORD_DEPENDENCIES)


def _set_VEHICLE_RECORD_DEPENDENCIES():
    global _VEHICLE_RECORD_DEPENDENCIES2
    global _VEHICLE_RECORD_DEPENDENCIES
    _VEHICLE_RECORD_DEPENDENCIES = dict(_RECORD_DEPENDENCIES)
    _VEHICLE_RECORD_DEPENDENCIES.update({})
    _VEHICLE_RECORD_DEPENDENCIES2 = buildDependencies2(_VEHICLE_RECORD_DEPENDENCIES)


def _set_TANKMAN_RECORD_DEPENDENCIES():
    global _TANKMAN_RECORD_DEPENDENCIES2
    global _TANKMAN_RECORD_DEPENDENCIES
    _TANKMAN_RECORD_DEPENDENCIES = dict({})
    _TANKMAN_RECORD_DEPENDENCIES.update({})
    _TANKMAN_RECORD_DEPENDENCIES2 = buildDependencies2(_TANKMAN_RECORD_DEPENDENCIES)


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
      'directHits',
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
      'fragsSinai',
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
      'medalRadleyWalters',
      'medalBrunoPietro',
      'medalTarczay',
      'medalPascucci',
      'medalDumitru',
      'medalLehvaslaiho',
      'medalNikolas',
      'medalLafayettePool',
      'sinai',
      'heroesOfRassenay',
      'mechanicEngineerStrg',
      'beasthunter',
      'mousebane',
      'tankExpertStrg',
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
      'company/directHits',
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
      'clan/directHits',
      'clan/spotted',
      'clan/damageDealt',
      'clan/damageReceived',
      'clan/capturePoints',
      'clan/droppedCapturePoints',
      'tankExpert',
      'tankExpert0',
      'tankExpert1',
      'tankExpert2',
      'tankExpert3',
      'tankExpert4',
      'tankExpert5',
      'tankExpert6',
      'tankExpert7',
      'tankExpert8',
      'tankExpert9',
      'tankExpert10',
      'tankExpert11',
      'tankExpert12',
      'tankExpert13',
      'tankExpert14',
      'mechanicEngineer',
      'mechanicEngineer0',
      'mechanicEngineer0',
      'mechanicEngineer1',
      'mechanicEngineer2',
      'mechanicEngineer3',
      'mechanicEngineer4',
      'mechanicEngineer5',
      'mechanicEngineer6',
      'mechanicEngineer7',
      'mechanicEngineer8',
      'mechanicEngineer9',
      'mechanicEngineer10',
      'mechanicEngineer11',
      'mechanicEngineer12',
      'mechanicEngineer13',
      'mechanicEngineer14',
      'medalBrothersInArms',
      'medalCrucialContribution',
      'medalDeLanglade',
      'medalTamadaYoshio',
      'bombardier',
      'huntsman',
      'alaric',
      'sturdy',
      'ironMan',
      'luckyDevil',
      'pattonValley',
      'fragsPatton',
      'originalXP',
      'damageAssistedTrack',
      'damageAssistedRadio',
      'mileage',
      'directHitsReceived',
      'noDamageDirectHitsReceived',
      'piercingsReceived',
      'explosionHitsReceived',
      'explosionHits',
      'piercings',
      'xpBefore8_8',
      'battlesCountBefore8_8',
      '_dynRecPos_account'], ['vehTypeFrags', 'a15x15Cut', 'rareAchievements'])
    extendRecordPacking(_ACCOUNT_RECORDS_LAYOUT, '_dynRecPos_account', _RECORD_PACKING)


def _set_VEHICLE_RECORDS_LAYOUT():
    global _VEHICLE_RECORDS_LAYOUT
    _VEHICLE_RECORDS_LAYOUT = (['_version',
      'creationTime',
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
      'directHits',
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
      'fragsSinai',
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
      'medalRadleyWalters',
      'medalBrunoPietro',
      'medalTarczay',
      'medalPascucci',
      'medalDumitru',
      'medalLehvaslaiho',
      'medalNikolas',
      'medalLafayettePool',
      'sinai',
      'heroesOfRassenay',
      'beasthunter',
      'mousebane',
      'tankExpertStrg',
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
      'company/directHits',
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
      'clan/directHits',
      'clan/spotted',
      'clan/damageDealt',
      'clan/damageReceived',
      'clan/capturePoints',
      'clan/droppedCapturePoints',
      'tankExpert',
      'tankExpert0',
      'tankExpert1',
      'tankExpert2',
      'tankExpert3',
      'tankExpert4',
      'tankExpert5',
      'tankExpert6',
      'tankExpert7',
      'tankExpert8',
      'tankExpert9',
      'tankExpert10',
      'tankExpert11',
      'tankExpert12',
      'tankExpert13',
      'tankExpert14',
      'medalBrothersInArms',
      'medalCrucialContribution',
      'medalDeLanglade',
      'medalTamadaYoshio',
      'bombardier',
      'huntsman',
      'alaric',
      'sturdy',
      'ironMan',
      'luckyDevil',
      'pattonValley',
      'fragsPatton',
      'originalXP',
      'damageAssistedTrack',
      'damageAssistedRadio',
      'mileage',
      'directHitsReceived',
      'noDamageDirectHitsReceived',
      'piercingsReceived',
      'explosionHitsReceived',
      'explosionHits',
      'piercings',
      'xpBefore8_8',
      'battlesCountBefore8_8',
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
      'medalRadleyWalters',
      'medalBrunoPietro',
      'medalTarczay',
      'medalPascucci',
      'medalDumitru',
      'medalLehvaslaiho',
      'medalNikolas',
      'medalLafayettePool',
      'heroesOfRassenay',
      'medalDeLanglade',
      'medalTamadaYoshio',
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


def _set_ACCOUNT_RECORDS_SET():
    global _ACCOUNT_RECORDS_SET
    _ACCOUNT_RECORDS_SET = set(_ACCOUNT_RECORDS_LAYOUT[0] + _ACCOUNT_RECORDS_LAYOUT[1])


def _set_VEHICLE_RECORDS_SET():
    global _VEHICLE_RECORDS_SET
    _VEHICLE_RECORDS_SET = set(_VEHICLE_RECORDS_LAYOUT[0] + _VEHICLE_RECORDS_LAYOUT[1])


def _set_TANKMAN_RECORDS_SET():
    global _TANKMAN_RECORDS_SET
    _TANKMAN_RECORDS_SET = set(_TANKMAN_RECORDS_LAYOUT[0] + _TANKMAN_RECORDS_LAYOUT[1])


def getAccountDossierDescr(compDescr = ''):
    return _DossierDescr(compDescr, _ACCOUNT_RECORDS_LAYOUT, _ACCOUNT_RECORDS_SET, '_dynRecPos_account', _ACCOUNT_STATIC_RECORD_POSITIONS, _ACCOUNT_STATIC_RECORDS_FMT, _ACCOUNT_RECORD_DEPENDENCIES2, _ACCOUNT_POP_UP_RECORDS, ACCOUNT_DOSSIER_VERSION, _ACCOUNT_DOSSIER_UPDATERS)


def getVehicleDossierDescr(compDescr = ''):
    return _DossierDescr(compDescr, _VEHICLE_RECORDS_LAYOUT, _VEHICLE_RECORDS_SET, '_dynRecPos_vehicle', _VEHICLE_STATIC_RECORD_POSITIONS, _VEHICLE_STATIC_RECORDS_FMT, _VEHICLE_RECORD_DEPENDENCIES2, _VEHICLE_POP_UP_RECORDS, VEHICLE_DOSSIER_VERSION, _VEHICLE_DOSSIER_UPDATERS)


def getTankmanDossierDescr(compDescr = ''):
    return _DossierDescr(compDescr, _TANKMAN_RECORDS_LAYOUT, _TANKMAN_RECORDS_SET, '_dynRecPos_tankman', _TANKMAN_STATIC_RECORD_POSITIONS, _TANKMAN_STATIC_RECORDS_FMT, _TANKMAN_RECORD_DEPENDENCIES2, _TANKMAN_POP_UP_RECORDS, TANKMAN_DOSSIER_VERSION, _TANKMAN_DOSSIER_UPDATERS)


def getDossierDescr(dossierType, compDescr = ''):
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
    if recordPacking[0] == 'b':
        return 1
    raise recordPacking[0] == 'p' or AssertionError
    return recordPacking[3]


def _set_ACCOUNT_DOSSIER_UPDATERS():
    global _ACCOUNT_DOSSIER_UPDATERS
    _ACCOUNT_DOSSIER_UPDATERS = {0: partial(getNewDossierData, ACCOUNT_DOSSIER_VERSION, _ACCOUNT_RECORDS_LAYOUT),
     19: partial(updateDossier1, 20, DOSSIER_TYPE.ACCOUNT),
     20: partial(updateDossier3, 21, DOSSIER_TYPE.ACCOUNT),
     21: partial(updateDossier4, 22, DOSSIER_TYPE.ACCOUNT),
     22: partial(updateDossier5, 23, DOSSIER_TYPE.ACCOUNT),
     23: partial(updateDossier6, 24, DOSSIER_TYPE.ACCOUNT, g_cache),
     24: partial(updateDossier7, 25, DOSSIER_TYPE.ACCOUNT),
     25: partial(updateDossier8, 26, DOSSIER_TYPE.ACCOUNT),
     26: partial(updateDossier9, 27, DOSSIER_TYPE.ACCOUNT),
     27: partial(updateDossier10, 28, DOSSIER_TYPE.ACCOUNT, g_cache),
     28: partial(updateDossier11, 29, DOSSIER_TYPE.ACCOUNT),
     29: partial(updateDossier13, 30, DOSSIER_TYPE.ACCOUNT),
     30: partial(updateDossier14, 31, DOSSIER_TYPE.ACCOUNT),
     31: partial(updateDossier15, 32, DOSSIER_TYPE.ACCOUNT)}


def _set_VEHICLE_DOSSIER_UPDATERS():
    global _VEHICLE_DOSSIER_UPDATERS
    _VEHICLE_DOSSIER_UPDATERS = {0: partial(getNewDossierData, VEHICLE_DOSSIER_VERSION, _VEHICLE_RECORDS_LAYOUT),
     17: partial(updateDossier1, 18, DOSSIER_TYPE.VEHICLE),
     18: partial(updateDossier2, 19, DOSSIER_TYPE.VEHICLE),
     19: partial(updateDossier3, 20, DOSSIER_TYPE.VEHICLE),
     20: partial(updateDossier5, 21, DOSSIER_TYPE.VEHICLE),
     21: partial(updateDossier6, 22, DOSSIER_TYPE.VEHICLE, g_cache),
     22: partial(updateDossier8, 23, DOSSIER_TYPE.VEHICLE),
     23: partial(updateDossier9, 24, DOSSIER_TYPE.VEHICLE),
     24: partial(updateDossier10, 25, DOSSIER_TYPE.VEHICLE, g_cache),
     25: partial(updateDossier11, 26, DOSSIER_TYPE.VEHICLE),
     26: partial(updateDossier12, 27, DOSSIER_TYPE.VEHICLE),
     27: partial(updateDossier13, 28, DOSSIER_TYPE.VEHICLE),
     28: partial(updateDossier15, 29, DOSSIER_TYPE.VEHICLE)}


def _set_TANKMAN_DOSSIER_UPDATERS():
    global _TANKMAN_DOSSIER_UPDATERS
    _TANKMAN_DOSSIER_UPDATERS = {0: partial(getNewDossierData, TANKMAN_DOSSIER_VERSION, _TANKMAN_RECORDS_LAYOUT),
     10: partial(updateDossier1, 11, DOSSIER_TYPE.TANKMAN),
     11: partial(updateDossier5, 12, DOSSIER_TYPE.TANKMAN),
     12: partial(updateDossier6, 13, DOSSIER_TYPE.TANKMAN, g_cache),
     13: partial(updateDossier9, 14, DOSSIER_TYPE.TANKMAN)}


class _DossierDescr(object):

    def __init__(self, compDescr, recordsLayout, recordsSet, dynRecPosRecord, staticRecordPositions, staticRecordsFmt, dependencies, popUpRecords, curVersion, versionUpdaters):
        if len(compDescr) < 2:
            self.__compDescr = '\x00\x00'
        else:
            self.__compDescr = compDescr
        self._recordsLayout = recordsLayout
        self.__recordsSet = recordsSet
        self.__dynRecPosRecord = dynRecPosRecord
        self.__staticRecordPositions = staticRecordPositions
        self.__staticRecordsFmt = staticRecordsFmt
        self.__dependencies = dependencies
        self.__popUpRecords = popUpRecords
        self.__curVersion = curVersion
        self.__versionUpdaters = versionUpdaters
        self.__isExpanded = False
        self.__dependentUpdates = 0
        self.__data = {}
        self.__changed = set([])
        self.popUps = set([])
        self.__updateVersion()

    def __getitem__(self, record):
        data = self.__data
        if record in data:
            return data[record]
        if record in self._recordsLayout[0]:
            packing = _RECORD_PACKING[record]
            if packing[0] == 'b':
                storageName, shift = packing[1:3]
                return bool(self[storageName] & 1 << shift)
            position = self.__staticRecordPositions[record]
            values = unpack('<' + packing[1], self.__compDescr[position:position + packing[2]])
            if packing[0] == 'p':
                data[record] = values[0]
            else:
                data[record] = packing[5](values)
            return data[record]
        packing = _RECORD_PACKING[record]
        dynRecIdx = self._recordsLayout[1].index(record)
        offset = self[self.__dynRecPosRecord][dynRecIdx]
        data[record], _ = packing[2](self.__compDescr, offset)
        return data[record]

    def __setitem__(self, record, value):
        if record in self.__popUpRecords:
            self.popUps.add(record)
        packing = _RECORD_PACKING[record]
        if packing[0] == 'b':
            prevValue = self[record]
            if bool(value) == prevValue:
                return
            storageName, shift = packing[1:3]
            value = self[storageName] ^ 1 << shift
            record = storageName
        elif packing[0] == 'p':
            value = min(value, packing[3])
        prevValue = self[record]
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

    def __contains__(self, record):
        return record in self.__recordsSet

    def __iter__(self):
        return _DossierDescrIterator(self)

    def update(self, d):
        for key, value in d.iteritems():
            self[key] = value

    def expand(self):
        if self.__isExpanded:
            return
        prevData = dict(self.__data)
        self.__data = unpackDossierCompDescr(self._recordsLayout, _RECORD_PACKING, self.__compDescr, self.__staticRecordsFmt, self.__staticRecordPositions)
        self.__data.update(prevData)
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
                if packing[0] == 'b':
                    continue
                fmt += packing[1]
                if packing[0] == 'p':
                    values.append(data[record])
                else:
                    values += packing[4](data[record])

            self.__compDescr = pack((fmt + dynRecordsFmt), *(values + dynRecordsValues))
        else:
            while self.__changed:
                changed = list(self.__changed)
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
        self.popUps.clear()
        return self.__compDescr

    def __updateVersion(self):
        while True:
            ver = self['_version']
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
    global g_cache
    g_cache = _buildCache()
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
    _set_ACCOUNT_RECORDS_SET()
    _set_VEHICLE_RECORDS_SET()
    _set_TANKMAN_RECORDS_SET()


def _buildCache():
    vehiclesByLevel = {}
    vehicles8p = set()
    beastVehicles = set()
    sinaiVehicles = set()
    pattonVehicles = set()
    vehiclesInTreesByNation = {}
    vehiclesInTrees = set()
    unlocksSources = vehicles.getUnlocksSources()
    for nationIdx in xrange(len(nations.NAMES)):
        nationList = vehicles.g_list.getList(nationIdx)
        vehiclesInNationTrees = set()
        for vehDescr in nationList.itervalues():
            vehiclesByLevel.setdefault(vehDescr['level'], set()).add(vehDescr['compactDescr'])
            if 'beast' in vehDescr['tags']:
                beastVehicles.add(vehDescr['compactDescr'])
            if 'sinai' in vehDescr['tags']:
                sinaiVehicles.add(vehDescr['compactDescr'])
            if len(unlocksSources.get(vehDescr['compactDescr'], set())) > 0 or len(vehicles.g_cache.vehicle(nationIdx, vehDescr['id']).unlocksDescrs) > 0:
                vehiclesInNationTrees.add(vehDescr['compactDescr'])
            if 'patton' in vehDescr['tags']:
                pattonVehicles.add(vehDescr['compactDescr'])

        vehiclesInTrees.update(vehiclesInNationTrees)
        vehiclesInTreesByNation[nationIdx] = vehiclesInNationTrees

    vehicles8p = vehiclesByLevel[8] | vehiclesByLevel[9] | vehiclesByLevel[10]
    return {'vehiclesByLevel': vehiclesByLevel,
     'vehicles8+': vehicles8p,
     'beastVehicles': beastVehicles,
     'sinaiVehicles': sinaiVehicles,
     'pattonVehicles': pattonVehicles,
     'mausTypeCompDescr': vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName('germany:Maus')),
     'vehiclesInTreesByNation': vehiclesInTreesByNation,
     'vehiclesInTrees': vehiclesInTrees}
