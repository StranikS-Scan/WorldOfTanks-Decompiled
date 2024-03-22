# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/updaters.py
import sys
import struct
from functools import partial
from comp7_helpers import archiveSeasonsGriffin, archiveMaxSeasonsGriffin, archiveCutSeasonsGriffin, addSeasonRecord
from dossiers2.common.updater_utils import getNewStaticSizeBlockValues, getStaticSizeBlockRecordValues
from dossiers2.common.updater_utils import getDictBlockRecordValues, updateDictRecords
from dossiers2.common.updater_utils import getNewBinarySetBlockValues, setStaticSizeBlockRecordValues
from dossiers2.common.updater_utils import addBlock, removeBlock, addRecords, removeRecords, setVersion
from dossiers2.common.updater_utils import getHeader, getBlockSize, getBlockCompDescr, setBlockCompDescr
from dossiers2.common.updater_utils import getBinarySetValue, updateStaticSizeBlockRecords, updateBinaryBlockRecords
import dossiers2.custom.tankmen_dossier1_updater
from dossiers2.custom.config import RECORD_CONFIGS
from VersionUpdater import VersionUpdaterBase
from serialization import ComponentBinSerializer
from wotdecorators import singleton
from debug_utils import LOG_DEBUG_DEV
ACCOUNT_DOSSIER_VERSION = 153
ACCOUNT_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromAccountDossier%d'
VEHICLE_DOSSIER_VERSION = 111
VEHICLE_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromVehicleDossier%d'
TANKMAN_DOSSIER_VERSION = 66
TANKMAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromTankmanDossier%d'
CLAN_DOSSIER_VERSION = 1
CLAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromClanDossier%d'
RATED7X7_DOSSIER_VERSION = 1
RATED7X7_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromRated7x7Dossier%d'
CLUB_DOSSIER_VERSION = 2
CLUB_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromClubDossier%d'
VEHICLE_DOSSIER_MINIMAL_SUPPORTED_VERSION = 64

def __updateFromAccountDossier64(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements']
    a15x15packing = {'creationTime': (0, 'I'),
     'battleLifeTime': (8, 'I'),
     'lastBattleTime': (4, 'I')}
    a15x15_2packing = {'mileage': (38, 'I'),
     'treesCut': (36, 'H')}
    achievementsPacking = {'maxXPVehicle': (136, 'I'),
     'maxFrags': (0, 'B'),
     'maxXP': (1, 'H'),
     'winAndSurvived': (3, 'I'),
     'maxFragsVehicle': (140, 'I'),
     'frags8p': (7, 'I')}
    totalLayout = [('creationTime', 'I'),
     ('lastBattleTime', 'I'),
     ('battleLifeTime', 'I'),
     ('treesCut', 'H'),
     ('mileage', 'I')]
    max15x15Layout = [('maxXP', 'H'),
     ('maxFrags', 'B'),
     ('maxDamage', 'H'),
     ('maxXPVehicle', 'I'),
     ('maxFragsVehicle', 'I'),
     ('maxDamageVehicle', 'I')]
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    totalDefaults = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    totalDefaults.update(getStaticSizeBlockRecordValues(updateCtx, 'a15x15_2', a15x15_2packing))
    if bool(totalDefaults):
        blockFormat, blockValues = getNewStaticSizeBlockValues(totalLayout, totalDefaults)
    else:
        blockFormat, blockValues = ('', None)
    addBlock(updateCtx, 'total', blockFormat, blockValues)
    removeRecords(updateCtx, 'a15x15', a15x15packing)
    removeRecords(updateCtx, 'a15x15_2', a15x15_2packing)
    addBlock(updateCtx, 'a7x7Cut')
    achievementsValues = getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking)
    addRecords(updateCtx, 'a15x15', [('winAndSurvived', 'I'), ('frags8p', 'I')], achievementsValues)
    addRecords(updateCtx, 'a7x7', [('winAndSurvived', 'I'), ('frags8p', 'I')], {})
    if bool(achievementsValues):
        blockFormat, blockValues = getNewStaticSizeBlockValues(max15x15Layout, achievementsValues)
    else:
        blockFormat, blockValues = ('', None)
    addBlock(updateCtx, 'max15x15', blockFormat, blockValues)
    addBlock(updateCtx, 'max7x7')
    removeRecords(updateCtx, 'achievements', achievementsPacking)
    setVersion(updateCtx, 65)
    return (65, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier65(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements', [('sniper2', 'H'), ('mainGun', 'H')], {})
    setVersion(updateCtx, 66)
    return (66, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier66(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    blockFormat = '<' + 'HHHHHHHH'
    blockValues = [0] * 8
    addBlock(updateCtx, 'achievements7x7', blockFormat, blockValues)
    setVersion(updateCtx, 67)
    return (67, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier67(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements7x7', [('tacticalBreakthrough', 'B')], {'tacticalBreakthrough': 0})
    setVersion(updateCtx, 68)
    return (68, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier68(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('battleCitizen', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 69)
    return (69, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier69(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('potentialDamageReceived', 'I'), ('damageBlockedByArmor', 'I')]
    addRecords(updateCtx, 'a15x15_2', recordFormats, {})
    addRecords(updateCtx, 'company2', recordFormats, {})
    addRecords(updateCtx, 'clan2', recordFormats, {})
    addRecords(updateCtx, 'a7x7', recordFormats, {})
    setVersion(updateCtx, 70)
    return (70, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier70(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('battlesCountBefore9_0', 'I')]
    a15x15packing = {'battlesCount': (4, 'I')}
    a15x15defaults = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    addRecords(updateCtx, 'a15x15', recordFormats, {'battlesCountBefore9_0': a15x15defaults.get('battlesCount', 0)})
    companyPacking = {'battlesCount': (4, 'I')}
    companyDefaults = getStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking)
    addRecords(updateCtx, 'company', recordFormats, {'battlesCountBefore9_0': companyDefaults.get('battlesCount', 0)})
    clanPacking = {'battlesCount': (4, 'I')}
    clanDefaults = getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking)
    addRecords(updateCtx, 'clan', recordFormats, {'battlesCountBefore9_0': clanDefaults.get('battlesCount', 0)})
    a7x7packing = {'battlesCount': (4, 'I')}
    a7x7defaults = getStaticSizeBlockRecordValues(updateCtx, 'a7x7', a7x7packing)
    addRecords(updateCtx, 'a7x7', recordFormats, {'battlesCountBefore9_0': a7x7defaults.get('battlesCount', 0)})
    setVersion(updateCtx, 71)
    return (71, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier71(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    setVersion(updateCtx, 72)
    return (72, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier72(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'historical')
    addBlock(updateCtx, 'maxHistorical')
    addBlock(updateCtx, 'historicalAchievements')
    addBlock(updateCtx, 'historicalCut')
    setVersion(updateCtx, 73)
    return (73, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier73(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('godOfWar', 'H'),
     ('fightingReconnaissance', 'H'),
     ('fightingReconnaissanceMedal', 'H'),
     ('willToWinSpirit', 'H'),
     ('crucialShot', 'H'),
     ('crucialShotMedal', 'H'),
     ('forTacticalOperations', 'B')]
    defaultValues = {'godOfWar': 0,
     'fightingReconnaissance': 0,
     'fightingReconnaissanceMedal': 0,
     'willToWinSpirit': 0,
     'crucialShot': 0,
     'crucialShotMedal': 0,
     'forTacticalOperations': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 74)
    return (74, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier74(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('medalMonolith', 'H'),
     ('medalAntiSpgFire', 'H'),
     ('medalGore', 'H'),
     ('medalCoolBlood', 'H'),
     ('medalStark', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 75)
    return (75, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier75(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'uniqueAchievements')
    setVersion(updateCtx, 76)
    return (76, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier76(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'fortBattles')
    addBlock(updateCtx, 'maxFortBattles')
    addBlock(updateCtx, 'fortBattlesCut')
    addBlock(updateCtx, 'fortSorties')
    addBlock(updateCtx, 'maxFortSorties')
    setVersion(updateCtx, 77)
    return (77, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier77(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'fortSortiesCut')
    addBlock(updateCtx, 'fortBattlesInClan')
    addBlock(updateCtx, 'maxFortBattlesInClan')
    addBlock(updateCtx, 'fortSortiesInClan')
    addBlock(updateCtx, 'maxFortSortiesInClan')
    addBlock(updateCtx, 'fortMisc')
    addBlock(updateCtx, 'fortMiscInClan')
    addBlock(updateCtx, 'fortAchievements')
    setVersion(updateCtx, 78)
    return (78, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier78(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('promisingFighter', 'H'),
     ('promisingFighterMedal', 'H'),
     ('heavyFire', 'H'),
     ('heavyFireMedal', 'H'),
     ('ranger', 'H'),
     ('rangerMedal', 'H'),
     ('fireAndSteel', 'H'),
     ('fireAndSteelMedal', 'H'),
     ('pyromaniac', 'H'),
     ('pyromaniacMedal', 'H'),
     ('noMansLand', 'H')]
    defaultValues = {'promisingFighter': 0,
     'promisingFighterMedal': 0,
     'heavyFire': 0,
     'heavyFireMedal': 0,
     'ranger': 0,
     'rangerMedal': 0,
     'fireAndSteel': 0,
     'fireAndSteelMedal': 0,
     'pyromaniac': 0,
     'pyromaniacMedal': 0,
     'noMansLand': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 79)
    return (79, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier79(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('WFC2014', 'B'), ('WFC2014WinSeries', 'B'), ('maxWFC2014WinSeries', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 80)
    return (80, updateCtx['dossierCompDescr'])


def _count7x7awards(ctx):
    packing = {'crucialShotMedal': (27, 'H'),
     'noMansLand': (50, 'H'),
     'fightingReconnaissanceMedal': (21, 'H'),
     'godOfWar': (17, 'H'),
     'armoredFist': (14, 'H'),
     'fireAndSteelMedal': (44, 'H'),
     'forTacticalOperations': (29, 'B'),
     'kingOfTheHill': (8, 'H'),
     'wolfAmongSheepMedal': (2, 'H'),
     'willToWinSpirit': (23, 'H'),
     'heavyFireMedal': (36, 'H'),
     'maxTacticalBreakthroughSeries': (12, 'H'),
     'promisingFighterMedal': (32, 'H'),
     'geniusForWarMedal': (6, 'H'),
     'rangerMedal': (40, 'H'),
     'pyromaniacMedal': (48, 'H')}
    awardNum = 0
    values = getStaticSizeBlockRecordValues(ctx, 'achievements7x7', packing)
    if values and values['maxTacticalBreakthroughSeries'] >= 3:
        awardNum += 1
        del values['maxTacticalBreakthroughSeries']
    if values and values['forTacticalOperations'] > 0:
        awardNum += 5 - values['forTacticalOperations']
        del values['forTacticalOperations']
    for val in values.itervalues():
        awardNum += val

    return awardNum


def __updateFromAccountDossier80(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    awardCount = _count7x7awards(updateCtx)
    formats = [('guerrilla', 'H'),
     ('guerrillaMedal', 'H'),
     ('infiltrator', 'H'),
     ('infiltratorMedal', 'H'),
     ('sentinel', 'H'),
     ('sentinelMedal', 'H'),
     ('prematureDetonation', 'H'),
     ('prematureDetonationMedal', 'H'),
     ('bruteForce', 'H'),
     ('bruteForceMedal', 'H'),
     ('awardCount', 'I'),
     ('battleTested', 'B')]
    defaultValues = {'guerrilla': 0,
     'guerrillaMedal': 0,
     'infiltrator': 0,
     'infiltratorMedal': 0,
     'sentinel': 0,
     'sentinelMedal': 0,
     'prematureDetonation': 0,
     'prematureDetonationMedal': 0,
     'bruteForce': 0,
     'bruteForceMedal': 0,
     'awardCount': awardCount,
     'battleTested': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 81)
    return (81, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier81(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    layout = ['titleSniper',
     'invincible',
     'diehard',
     'handOfDeath',
     'armorPiercer',
     'battleCitizen',
     'WFC2014',
     'tacticalBreakthrough']
    values = {}
    achievementsPacking = {'titleSniper': (88, 'B'),
     'invincible': (89, 'B'),
     'diehard': (90, 'B'),
     'handOfDeath': (93, 'B'),
     'armorPiercer': (94, 'B'),
     'battleCitizen': (131, 'B'),
     'WFC2014': (142, 'B')}
    values.update(getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking))
    achievements7x7Packing = {'tacticalBreakthrough': (16, 'B')}
    values.update(getStaticSizeBlockRecordValues(updateCtx, 'achievements7x7', achievements7x7Packing))
    blockFormat, blockValues = getNewBinarySetBlockValues(layout, values)
    addBlock(updateCtx, 'singleAchievements', blockFormat, blockValues)
    removeRecords(updateCtx, 'achievements', achievementsPacking)
    removeRecords(updateCtx, 'achievements7x7', achievements7x7Packing)
    setVersion(updateCtx, 82)
    return (82, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier82(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    blockLayout = [('medalRotmistrov', 'B')]
    blockFormat, blockValues = getNewStaticSizeBlockValues(blockLayout, {'medalRotmistrov': 0})
    addBlock(updateCtx, 'clanAchievements', blockFormat, blockValues)
    setVersion(updateCtx, 83)
    return (83, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier83(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    a15x15packing = {'battlesCountBefore9_0': (68, 'I'),
     'battlesCountBefore8_8': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    if values and values['battlesCountBefore8_8'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_8']
        setStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing, values)
    clanPacking = {'battlesCountBefore9_0': (60, 'I'),
     'battlesCountBefore8_9': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking)
    if values and values['battlesCountBefore8_9'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_9']
        setStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking, values)
    companyPacking = {'battlesCountBefore9_0': (60, 'I'),
     'battlesCountBefore8_9': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking)
    if values and values['battlesCountBefore8_9'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_9']
        setStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking, values)
    setVersion(updateCtx, 84)
    return (84, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier84(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('impenetrable', 'H'),
     ('reliableComradeSeries', 'H'),
     ('reliableComrade', 'H'),
     ('maxAimerSeries', 'B'),
     ('shootToKill', 'H'),
     ('fighter', 'H'),
     ('duelist', 'H'),
     ('demolition', 'H'),
     ('arsonist', 'H'),
     ('bonecrusher', 'H'),
     ('charmed', 'H'),
     ('even', 'H')]
    addRecords(updateCtx, 'achievements', recordFormats, {})
    setVersion(updateCtx, 85)
    return (85, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier85(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wins', 'H'), ('capturedBasesInAttack', 'H'), ('capturedBasesInDefence', 'H')]
    addRecords(updateCtx, 'fortAchievements', formats, {})
    setVersion(updateCtx, 86)
    return (86, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier86(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('deathTrackWinSeries', 'B'), ('maxDeathTrackWinSeries', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 87)
    return (87, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier87(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('readyForBattleLT', 'B'),
     ('readyForBattleMT', 'B'),
     ('readyForBattleHT', 'B'),
     ('readyForBattleSPG', 'B'),
     ('readyForBattleATSPG', 'B'),
     ('readyForBattleALL', 'B'),
     ('tankwomenProgress', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 88)
    return (88, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier88(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'rated7x7')
    addBlock(updateCtx, 'maxRated7x7')
    setVersion(updateCtx, 89)
    return (89, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier89(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'achievementsRated7x7')
    setVersion(updateCtx, 90)
    return (90, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier90(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'rated7x7Cut')
    setVersion(updateCtx, 91)
    return (91, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier91(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements', [('testartilleryman', 'H')], {})
    setVersion(updateCtx, 92)
    return (92, updateCtx['dossierCompDescr'])


def _countBattleHeroesBasedOn7x7Medals(ctx):
    packing = {'wolfAmongSheepMedal': (2, 'H'),
     'geniusForWarMedal': (6, 'H')}
    awardNum = 0
    values = getStaticSizeBlockRecordValues(ctx, 'achievements7x7', packing)
    for val in values.itervalues():
        awardNum += val

    return awardNum


def _medalKayClass(battleHeroes):
    medalKayCfg = (1, 10, 100, 1000)
    maxMedalClass = len(medalKayCfg)
    for medalClass in xrange(1, maxMedalClass + 1):
        if battleHeroes >= medalKayCfg[maxMedalClass - medalClass]:
            break
    else:
        medalClass = 0

    return medalClass


def __updateFromAccountDossier92(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    battleHeroes7x7Count = _countBattleHeroesBasedOn7x7Medals(updateCtx)
    if battleHeroes7x7Count > 0:
        achievementsPacking = {'battleHeroes': (20, 'H'),
         'medalKay': (38, 'B')}
        values = getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking)
        if values:
            values['battleHeroes'] += battleHeroes7x7Count
            values['medalKay'] = _medalKayClass(values['battleHeroes'])
            setStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking, values)
    setVersion(updateCtx, 93)
    return (93, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier93(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'globalMapCommon')
    addBlock(updateCtx, 'globalMapMiddle')
    addBlock(updateCtx, 'globalMapChampion')
    addBlock(updateCtx, 'globalMapAbsolute')
    setVersion(updateCtx, 94)
    return (94, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier94(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapCommon',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    removeBlock(updateCtx, 'globalMapCommon')
    recordFormats = [('xpBefore8_9', 'I'), ('battlesCountBefore8_9', 'I'), ('battlesCountBefore9_0', 'I')]
    addRecords(updateCtx, 'globalMapMiddle', recordFormats, {})
    addRecords(updateCtx, 'globalMapChampion', recordFormats, {})
    addRecords(updateCtx, 'globalMapAbsolute', recordFormats, {})
    setVersion(updateCtx, 95)
    return (95, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier95(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'fortSortiesInClan', [('middleBattlesCount', 'I'),
     ('championBattlesCount', 'I'),
     ('absoluteBattlesCount', 'I'),
     ('middleWins', 'I'),
     ('championWins', 'I'),
     ('absoluteWins', 'I'),
     ('fortResource', 'I')], {})
    setVersion(updateCtx, 96)
    return (96, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier96(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'maxGlobalMapMiddle')
    addBlock(updateCtx, 'maxGlobalMapChampion')
    addBlock(updateCtx, 'maxGlobalMapAbsolute')
    setVersion(updateCtx, 97)
    return (97, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier97(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'globalMapCommonCut')
    setVersion(updateCtx, 98)
    return (98, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier98(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'fallout')
    addBlock(updateCtx, 'falloutCut')
    addBlock(updateCtx, 'maxFallout')
    setVersion(updateCtx, 99)
    return (99, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier99(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'falloutAchievements')
    setVersion(updateCtx, 100)
    return (100, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier100(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('EFC2016WinSeries', 'H'), ('maxEFC2016WinSeries', 'H'), ('EFC2016Goleador', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 101)
    return (101, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier101(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('markIBomberman', 'H'), ('markIRepairer', 'H'), ('markI100Years', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 102)
    return (102, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier102(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    modes = ('a15x15_2', 'clan2', 'company2', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'rated7x7', 'fallout', 'globalMapMiddle', 'globalMapChampion', 'globalMapAbsolute')
    for mode in modes:
        recordsFormat = [('battlesOnStunningVehicles', 'I'), ('stunNum', 'I'), ('damageAssistedStun', 'I')]
        addRecords(updateCtx, mode, recordsFormat, {})

    setVersion(updateCtx, 103)
    return (103, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier103(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    for blockName, expectedFormat in (('fortBattlesInClan', '<IIIIIIIIIIIIIIIIIIIIIIIIIIIII'), ('fortSortiesInClan', '<IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII')):
        currentSize = getBlockSize(updateCtx, blockName)
        expectedSize = struct.calcsize(expectedFormat)
        if currentSize < expectedSize:
            recordsFormat = [('battlesOnStunningVehicles', 'I'), ('stunNum', 'I'), ('damageAssistedStun', 'I')]
            addRecords(updateCtx, blockName, recordsFormat, {})

    setVersion(updateCtx, 104)
    return (104, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier104(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'ranked')
    addBlock(updateCtx, 'maxRanked')
    addBlock(updateCtx, 'rankedCut')
    addBlock(updateCtx, 'rankedBadges')
    addBlock(updateCtx, 'rankedSeasons')
    addBlock(updateCtx, 'rankedCurrent')
    addBlock(updateCtx, 'rankedPrevious')
    addBlock(updateCtx, 'maxRankedCurrent')
    addBlock(updateCtx, 'maxRankedPrevious')
    addBlock(updateCtx, 'rankedCurrentCut')
    addBlock(updateCtx, 'rankedPreviousCut')
    addBlock(updateCtx, 'rankedCurrentCycle')
    addBlock(updateCtx, 'rankedPreviousCycle')
    setVersion(updateCtx, 105)
    return (105, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier105(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortMisc',
     'fortMiscInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedBadges',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    removeBlock(updateCtx, 'fortMisc')
    removeBlock(updateCtx, 'fortMiscInClan')
    fortSortiesInClanPacking = {'middleWins': (128, 'I'),
     'middleBattlesCount': (116, 'I'),
     'absoluteBattlesCount': (124, 'I'),
     'absoluteWins': (136, 'I'),
     'fortResource': (140, 'I'),
     'championWins': (132, 'I'),
     'championBattlesCount': (120, 'I')}
    removeRecords(updateCtx, 'fortSortiesInClan', fortSortiesInClanPacking)
    fortAchievementsPacking = {'wins': (8, 'H'),
     'capturedBasesInAttack': (10, 'H'),
     'capturedBasesInDefence': (12, 'H')}
    removeRecords(updateCtx, 'fortAchievements', fortAchievementsPacking)
    setVersion(updateCtx, 106)
    return (106, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier106(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedBadges',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'a30x30')
    addBlock(updateCtx, 'a30x30Cut')
    addBlock(updateCtx, 'max30x30')
    setVersion(updateCtx, 107)
    return (107, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier107(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedBadges',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    a15x15Cut = getBlockCompDescr(updateCtx, 'a15x15Cut')
    markOfMasteryCutBlockFormat = ''
    markOfMasteryCutBlockValues = None
    if a15x15Cut:
        keyFormat, valueFormat = ('I', 'IIII')
        itemFormat = keyFormat + valueFormat
        itemSize = struct.calcsize('<' + itemFormat)
        length = len(a15x15Cut) / itemSize
        fmt = '<' + itemFormat * length
        values = struct.unpack(fmt, a15x15Cut)
        newValues = []
        markOfMasteryCutBlockFormat = '<'
        markOfMasteryCutBlockValues = []
        itemLength = len(itemFormat)
        idx = 0
        for i in xrange(length):
            items = values[idx:idx + itemLength]
            newValues += items[:3] + items[4:]
            if items[3] != 0:
                markOfMasteryCutBlockFormat += 'IB'
                markOfMasteryCutBlockValues += [items[0], items[3]]
            idx += itemLength

        newKeyFormat, newValueFormat = ('I', 'III')
        newItemFormat = newKeyFormat + newValueFormat
        fmt = '<' + newItemFormat * length
        newA15x15CutCompDescr = struct.pack(fmt, *newValues)
        setBlockCompDescr(updateCtx, 'a15x15Cut', newA15x15CutCompDescr)
    addBlock(updateCtx, 'markOfMasteryCut', markOfMasteryCutBlockFormat, markOfMasteryCutBlockValues)
    setVersion(updateCtx, 108)
    return (108, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier108(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedBadges',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    rankedBadgesPacking = {'1': (0, 'H'),
     '2': (2, 'H'),
     '3': (4, 'H'),
     '4': (6, 'H'),
     '5': (8, 'H'),
     '6': (10, 'H'),
     '7': (12, 'H'),
     '8': (14, 'H'),
     '9': (16, 'H')}
    badges = getStaticSizeBlockRecordValues(updateCtx, 'rankedBadges', rankedBadgesPacking)
    addItems = {}
    _SECONDS_IN_DAY = 86400
    for strBadgeID, daysTimestamp in badges.iteritems():
        if daysTimestamp:
            addItems[int(strBadgeID)] = daysTimestamp * _SECONDS_IN_DAY

    LOG_DEBUG_DEV('addItems', addItems)
    itemFormat = 'II'
    subBlockFormat = '<'
    subBlockValues = []
    for k, v in addItems.iteritems():
        subBlockFormat += itemFormat
        subBlockValues.append(k)
        subBlockValues.append(v)

    LOG_DEBUG_DEV('subBlockFormat', subBlockFormat, subBlockValues)
    addBlock(updateCtx, 'playerBadges', subBlockFormat, subBlockValues)
    removeBlock(updateCtx, 'rankedBadges')
    setVersion(updateCtx, 109)
    return (109, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier109(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'epicBattle')
    addBlock(updateCtx, 'epicBattleCut')
    addBlock(updateCtx, 'maxEpicBattle')
    addBlock(updateCtx, 'epicBattleAchievements')
    setVersion(updateCtx, 110)
    return (110, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier110(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    isPresent = getBinarySetValue(updateCtx, 'singleAchievements', 4, 2)
    records = [(183, 'H', 1 if isPresent else 0)]
    updateStaticSizeBlockRecords(updateCtx, 'achievements', records)
    setVersion(updateCtx, 111)
    return (111, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier111(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('FE18ClosedStage', 'B'),
     ('FE18SoloStriker', 'B'),
     ('FE18SoloMidfielder', 'B'),
     ('FE18SoloDefender', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 112)
    return (112, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier112(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('readyForBattleAllianceUSSR', 'B'),
     ('readyForBattleAllianceGermany', 'B'),
     ('readyForBattleAllianceUSA', 'B'),
     ('readyForBattleAllianceFrance', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 113)
    return (113, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier113(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('superTesterVeteran', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 114)
    return (114, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier114(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('alphaTester', 'B'),
     ('betaTester', 'B'),
     ('10YearsOfService', 'B'),
     ('09YearsOfService', 'B'),
     ('08YearsOfService', 'B'),
     ('07YearsOfService', 'B'),
     ('06YearsOfService', 'B'),
     ('05YearsOfService', 'B'),
     ('04YearsOfService', 'B'),
     ('03YearsOfService', 'B'),
     ('02YearsOfService', 'B'),
     ('01YearsOfService', 'B')]
    addRecords(updateCtx, 'singleAchievements', formats, {})
    setVersion(updateCtx, 115)
    return (115, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier115(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('NY19A1', 'B'), ('NY19A2', 'B'), ('NY19A3', 'B')]
    addRecords(updateCtx, 'singleAchievements', formats, {})
    setVersion(updateCtx, 116)
    return (116, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier116(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('RP2018firstmed', 'B'),
     ('RP2018secondmed', 'B'),
     ('RP2018thirdmed', 'B'),
     ('RP2018sergeant', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 117)
    return (117, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier117(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('rankedDivisionFighter', 'I'), ('rankedStayingPower', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 118)
    return (118, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier118(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'rankedCurrent',
     'rankedPrevious',
     'maxRankedCurrent',
     'maxRankedPrevious',
     'rankedCurrentCut',
     'rankedPreviousCut',
     'rankedCurrentCycle',
     'rankedPreviousCycle',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'rankedSeason1')
    addBlock(updateCtx, 'rankedSeason2')
    addBlock(updateCtx, 'rankedSeason3')
    addBlock(updateCtx, 'maxRankedSeason1')
    addBlock(updateCtx, 'maxRankedSeason2')
    addBlock(updateCtx, 'maxRankedSeason3')
    addBlock(updateCtx, 'rankedCutSeason1')
    addBlock(updateCtx, 'rankedCutSeason2')
    addBlock(updateCtx, 'rankedCutSeason3')
    addBlock(updateCtx, 'rankedArchive')
    addBlock(updateCtx, 'maxRankedArchive')
    addBlock(updateCtx, 'rankedCutArchive')
    oldBlockCompDescr = getBlockCompDescr(updateCtx, 'ranked')
    if oldBlockCompDescr:
        setBlockCompDescr(updateCtx, 'rankedArchive', oldBlockCompDescr)
    oldBlockCompDescr = getBlockCompDescr(updateCtx, 'maxRanked')
    if oldBlockCompDescr:
        setBlockCompDescr(updateCtx, 'maxRankedArchive', oldBlockCompDescr)
    oldBlockCompDescr = getBlockCompDescr(updateCtx, 'rankedCut')
    if oldBlockCompDescr:
        setBlockCompDescr(updateCtx, 'rankedCutArchive', oldBlockCompDescr)
    removeBlock(updateCtx, 'rankedCurrent')
    removeBlock(updateCtx, 'rankedPrevious')
    removeBlock(updateCtx, 'rankedCurrentCycle')
    removeBlock(updateCtx, 'rankedPreviousCycle')
    removeBlock(updateCtx, 'maxRankedCurrent')
    removeBlock(updateCtx, 'maxRankedPrevious')
    removeBlock(updateCtx, 'rankedCurrentCut')
    removeBlock(updateCtx, 'rankedPreviousCut')
    setVersion(updateCtx, 119)
    return (119, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier119(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('BR2019Top1Solo', 'I'), ('BR2019Top1Squad', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 120)
    return (120, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier120(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'racing2019Achievements')
    setVersion(updateCtx, 121)
    return (121, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier121(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'racing2019Achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    rankedSeasonsValues = getDictBlockRecordValues(updateCtx, 'rankedSeasons', 'II', 'BBHHH')
    if rankedSeasonsValues:
        updateDictRecords(updateCtx, 'rankedSeasons', 'II', 'BHHHH', rankedSeasonsValues)
    setVersion(updateCtx, 122)
    return (122, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier122(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'racing2019Achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('superTesterVeteranCross', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 123)
    return (123, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier123(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'racing2019Achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    removeBlock(updateCtx, 'racing2019Achievements')
    setVersion(updateCtx, 124)
    return (124, updateCtx['dossierCompDescr'])


def _rankedAchievmentClass(counter, achievmentName):
    achievmentCfg = RECORD_CONFIGS[achievmentName]
    maxAchievmentClass = len(achievmentCfg)
    for achievmentClass in xrange(1, maxAchievmentClass + 1):
        if counter >= achievmentCfg[maxAchievmentClass - achievmentClass]:
            break
    else:
        achievmentClass = 0

    return achievmentClass


def __updateFromAccountDossier124(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    packing = {'rankedDivisionFighter': (198, 'I'),
     'rankedStayingPower': (202, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'achievements', packing)
    rankedDivisionFighterVal = values.get('rankedDivisionFighter', 0)
    rankedStayingPowerVal = values.get('rankedStayingPower', 0)
    removeRecords(updateCtx, 'achievements', packing)
    formats = [('rankedDivisionCounter', 'I'),
     ('rankedDivisionFighter', 'B'),
     ('rankedStayingCounter', 'I'),
     ('rankedStayingPower', 'B')]
    defaults = {'rankedDivisionCounter': rankedDivisionFighterVal,
     'rankedDivisionFighter': _rankedAchievmentClass(rankedDivisionFighterVal, 'rankedDivisionFighter'),
     'rankedStayingCounter': rankedStayingPowerVal,
     'rankedStayingPower': _rankedAchievmentClass(rankedStayingPowerVal, 'rankedStayingPower')}
    addRecords(updateCtx, 'achievements', formats, defaults)
    setVersion(updateCtx, 125)
    return (125, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier125(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'epicSeasons')
    setVersion(updateCtx, 126)
    return (126, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier126(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('collectorVehicleStrg', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 127)
    return (127, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier127(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('TenYearsCountdownStageMedal', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 128)
    return (128, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier128(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'battleRoyaleSeasons')
    setVersion(updateCtx, 129)
    return (129, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier129(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wtHunterWins', 'I'), ('wtBossWins', 'I'), ('wtSpecBossDefeat', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 130)
    return (130, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier130(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsFormat = [('playedBonusBattles', 'I')]
    addRecords(updateCtx, 'ranked', recordsFormat, {})
    addRecords(updateCtx, 'rankedSeason1', recordsFormat, {})
    addRecords(updateCtx, 'rankedSeason2', recordsFormat, {})
    addRecords(updateCtx, 'rankedSeason3', recordsFormat, {})
    addRecords(updateCtx, 'rankedArchive', recordsFormat, {})
    setVersion(updateCtx, 131)
    return (131, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier131(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsFormat = [('RP2018sergeantCounter', 'H')]
    addRecords(updateCtx, 'achievements', recordsFormat, {})
    setVersion(updateCtx, 132)
    return (132, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier132(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'ranked_10x10')
    addBlock(updateCtx, 'maxRanked_10x10')
    addBlock(updateCtx, 'rankedCut_10x10')
    setVersion(updateCtx, 133)
    return (133, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier133(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    epicSeasonsValues = getDictBlockRecordValues(updateCtx, 'epicSeasons', 'II', 'HHBB')
    for key, values in epicSeasonsValues.iteritems():
        battleCount, averageFamePts, tokensCount, level = values
        epicSeasonsValues[key] = (battleCount,
         averageFamePts,
         level,
         0,
         0)

    LOG_DEBUG_DEV('__updateFromAccountDossier133 epicSeasonsValues', epicSeasonsValues)
    if epicSeasonsValues:
        updateDictRecords(updateCtx, 'epicSeasons', 'II', 'HHBHH', epicSeasonsValues)
    setVersion(updateCtx, 134)
    return (134, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier134(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    rankedCut10x10CompDescr = getBlockCompDescr(updateCtx, 'rankedCut_10x10')
    setBlockCompDescr(updateCtx, 'rankedCut', rankedCut10x10CompDescr if rankedCut10x10CompDescr else '')
    setVersion(updateCtx, 135)
    return (135, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier135(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wtxHunterWins', 'I'), ('wtxBossWins', 'I'), ('wtxSpecBossDefeat', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 136)
    return (136, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier136(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'steamAchievements')
    setVersion(updateCtx, 137)
    return (137, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier137(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsFormat = [('whiteTiger2012', 'B')]
    addRecords(updateCtx, 'achievements', recordsFormat, {})
    setVersion(updateCtx, 138)
    return (138, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier138(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('lunarNY2022Progression', 'B')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 139)
    return (139, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier139(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('oowTankmanWins', 'H'), ('oowStrategistWins', 'H'), ('oowCompetetiveWin', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 140)
    return (140, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier140(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('mapboxUniversal', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 141)
    return (141, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier141(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wclTournamentParticipant', 'H'), ('wclParticipant', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 142)
    return (142, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier142(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wt2022HunterWins', 'I'), ('wt2022BossWins', 'I'), ('wt2022SpecBossDefeat', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 143)
    return (143, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier143(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season1')
    addBlock(updateCtx, 'maxComp7Season1')
    addBlock(updateCtx, 'comp7CutSeason1')
    setVersion(updateCtx, 144)
    return (144, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier144(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season2')
    addBlock(updateCtx, 'maxComp7Season2')
    addBlock(updateCtx, 'comp7CutSeason2')
    setVersion(updateCtx, 145)
    return (145, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier145(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('maxAssisted', 'H'),
     ('maxAssistedVehicle', 'I'),
     ('maxDamageBlockedByArmor', 'H'),
     ('maxDamageBlockedByArmorVehicle', 'I')]
    addRecords(updateCtx, 'max15x15', formats, {})
    setVersion(updateCtx, 146)
    return (146, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier146(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    achievements7x7Packing = {'maxTacticalBreakthroughSeries': (12, 'H')}
    achievements7x7Values = getStaticSizeBlockRecordValues(updateCtx, 'achievements7x7', achievements7x7Packing)
    isSingleAchievementClaimed = getBinarySetValue(updateCtx, 'singleAchievements', 0, 7)
    if not isSingleAchievementClaimed and achievements7x7Values.get('maxTacticalBreakthroughSeries', 0) >= 3:
        updateBinaryBlockRecords(updateCtx, 'singleAchievements', [(0, 7, True)])
    setVersion(updateCtx, 147)
    return (147, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier147(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season3')
    addBlock(updateCtx, 'maxComp7Season3')
    addBlock(updateCtx, 'comp7CutSeason3')
    addBlock(updateCtx, 'comp7ArchiveGriffin')
    addBlock(updateCtx, 'maxComp7ArchiveGriffin')
    addBlock(updateCtx, 'comp7CutArchiveGriffin')
    setVersion(updateCtx, 148)
    return (148, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier148(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7CutSeason3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin',
     'comp7CutArchiveGriffin']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    comp7SeasonsPacking = {'spotted': (32, 'I'),
     'losses': (12, 'I'),
     'roleSkillUsed': (124, 'I'),
     'damageAssistedTrack': (56, 'I'),
     'damageReceived': (40, 'I'),
     'battlesOnStunningVehicles': (100, 'I'),
     'piercingsReceived': (72, 'I'),
     'originalXP': (52, 'I'),
     'damageAssistedRadio': (60, 'I'),
     'battlesCount': (4, 'I'),
     'survivedBattles': (16, 'I'),
     'winSeries': (112, 'I'),
     'piercings': (84, 'I'),
     'damageBlockedByArmor': (96, 'I'),
     'noDamageDirectHitsReceived': (68, 'I'),
     'xp': (0, 'I'),
     'droppedCapturePoints': (48, 'I'),
     'healthRepair': (128, 'I'),
     'directHitsReceived': (64, 'I'),
     'comp7PrestigePoints': (120, 'I'),
     'explosionHitsReceived': (76, 'I'),
     'winAndSurvived': (88, 'I'),
     'capturePoints': (44, 'I'),
     'potentialDamageReceived': (92, 'I'),
     'damageDealt': (36, 'I'),
     'damageAssistedStun': (108, 'I'),
     'squadWinSeries': (116, 'I'),
     'explosionHits': (80, 'I'),
     'wins': (8, 'I'),
     'poiCapturable': (132, 'I'),
     'frags': (20, 'I'),
     'stunNum': (104, 'I'),
     'shots': (24, 'I'),
     'directHits': (28, 'I')}
    comp7SeasonsNewPacking = {'spotted': (32, 'I'),
     'losses': (12, 'I'),
     'roleSkillUsed': (132, 'I'),
     'damageAssistedTrack': (56, 'I'),
     'damageReceived': (40, 'I'),
     'battlesOnStunningVehicles': (100, 'I'),
     'piercingsReceived': (72, 'I'),
     'originalXP': (52, 'I'),
     'damageAssistedRadio': (60, 'I'),
     'battlesCount': (4, 'I'),
     'survivedBattles': (16, 'I'),
     'winSeries': (112, 'I'),
     'piercings': (84, 'I'),
     'damageBlockedByArmor': (96, 'I'),
     'noDamageDirectHitsReceived': (68, 'I'),
     'xp': (0, 'I'),
     'droppedCapturePoints': (48, 'I'),
     'healthRepair': (136, 'I'),
     'comp7PrestigePoints': (128, 'I'),
     'directHitsReceived': (64, 'I'),
     'superSquadWins': (124, 'I'),
     'explosionHitsReceived': (76, 'I'),
     'winAndSurvived': (88, 'I'),
     'capturePoints': (44, 'I'),
     'potentialDamageReceived': (92, 'I'),
     'damageDealt': (36, 'I'),
     'superSquadBattlesCount': (120, 'I'),
     'damageAssistedStun': (108, 'I'),
     'squadWinSeries': (116, 'I'),
     'explosionHits': (80, 'I'),
     'wins': (8, 'I'),
     'poiCapturable': (140, 'I'),
     'frags': (20, 'I'),
     'stunNum': (104, 'I'),
     'shots': (24, 'I'),
     'directHits': (28, 'I')}
    seasonsNumber = 3
    archiveSeasonsGriffin(seasonsNumber, updateCtx, comp7SeasonsPacking, comp7SeasonsNewPacking)
    addSeasonRecord(updateCtx, 'comp7Season1', [('superSquadBattlesCount', 'I'), ('superSquadWins', 'I')], {})
    addSeasonRecord(updateCtx, 'comp7Season2', [('superSquadBattlesCount', 'I'), ('superSquadWins', 'I')], {})
    maxComp7SeasonsPacking = {'maxDamage': (3, 'H'),
     'maxXPVehicle': (5, 'I'),
     'maxDamageVehicle': (13, 'I'),
     'maxFrags': (2, 'B'),
     'maxXP': (0, 'H'),
     'maxHealthRepair': (29, 'H'),
     'maxComp7PrestigePointsVehicle': (19, 'I'),
     'maxEquipmentDamageDealt': (23, 'H'),
     'maxFragsVehicle': (9, 'I'),
     'maxSquadWinSeries': (37, 'H'),
     'maxComp7PrestigePoints': (17, 'H'),
     'maxWinSeries': (35, 'H'),
     'maxEquipmentDamageDealtVehicle': (25, 'I'),
     'maxHealthRepairVehicle': (31, 'I')}
    archiveMaxSeasonsGriffin(seasonsNumber, updateCtx, maxComp7SeasonsPacking)
    archiveCutSeasonsGriffin(seasonsNumber, updateCtx)
    setVersion(updateCtx, 149)
    return (149, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier149(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7CutSeason3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin',
     'comp7CutArchiveGriffin']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('wt2023HunterWins', 'I'), ('wt2023BossWins', 'I'), ('wt2023MaxPlasma', 'I')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 150)
    return (150, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier150(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7CutSeason3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin',
     'comp7CutArchiveGriffin']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'prestigeSystem')
    setVersion(updateCtx, 151)
    return (151, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier151(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7CutSeason3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin',
     'comp7CutArchiveGriffin',
     'prestigeSystem']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    BADGES_TO_REMOVE = (136, 137, 138)
    playerBadges = getDictBlockRecordValues(updateCtx, 'playerBadges', 'I', 'I')
    for badge_id in BADGES_TO_REMOVE:
        playerBadges.pop((badge_id,), None)

    updateDictRecords(updateCtx, 'playerBadges', 'I', 'I', playerBadges)
    setVersion(updateCtx, 152)
    return (152, updateCtx['dossierCompDescr'])


def __updateFromAccountDossier152(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'a15x15Cut',
     'rareAchievements',
     'total',
     'a7x7Cut',
     'max15x15',
     'max7x7',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'historicalAchievements',
     'historicalCut',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortBattlesCut',
     'fortSorties',
     'maxFortSorties',
     'fortSortiesCut',
     'fortBattlesInClan',
     'maxFortBattlesInClan',
     'fortSortiesInClan',
     'maxFortSortiesInClan',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'achievementsRated7x7',
     'rated7x7Cut',
     'globalMapMiddle',
     'globalMapChampion',
     'globalMapAbsolute',
     'maxGlobalMapMiddle',
     'maxGlobalMapChampion',
     'maxGlobalMapAbsolute',
     'globalMapCommonCut',
     'fallout',
     'falloutCut',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedCut',
     'rankedSeasons',
     'a30x30',
     'a30x30Cut',
     'max30x30',
     'markOfMasteryCut',
     'playerBadges',
     'epicBattle',
     'epicBattleCut',
     'maxEpicBattle',
     'epicBattleAchievements',
     'rankedSeason1',
     'rankedSeason2',
     'rankedSeason3',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'rankedCutSeason1',
     'rankedCutSeason2',
     'rankedCutSeason3',
     'rankedArchive',
     'maxRankedArchive',
     'rankedCutArchive',
     'epicSeasons',
     'battleRoyaleSeasons',
     'ranked_10x10',
     'maxRanked_10x10',
     'rankedCut_10x10',
     'steamAchievements',
     'comp7Season1',
     'maxComp7Season1',
     'comp7CutSeason1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7CutSeason2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7CutSeason3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin',
     'comp7CutArchiveGriffin',
     'prestigeSystem']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    BADGES_TO_REMOVE = (142, 143, 144)
    playerBadges = getDictBlockRecordValues(updateCtx, 'playerBadges', 'I', 'I')
    for badge_id in BADGES_TO_REMOVE:
        playerBadges.pop((badge_id,), None)

    updateDictRecords(updateCtx, 'playerBadges', 'I', 'I', playerBadges)
    setVersion(updateCtx, 153)
    return (153, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier64(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags']
    a15x15packing = {'creationTime': (0, 'I'),
     'battleLifeTime': (8, 'I'),
     'lastBattleTime': (4, 'I')}
    a15x15_2packing = {'mileage': (38, 'I'),
     'treesCut': (36, 'H')}
    achievementsPacking = {'maxFrags': (0, 'B'),
     'maxXP': (1, 'H'),
     'winAndSurvived': (3, 'I'),
     'frags8p': (7, 'I')}
    totalLayout = [('creationTime', 'I'),
     ('lastBattleTime', 'I'),
     ('battleLifeTime', 'I'),
     ('treesCut', 'H'),
     ('mileage', 'I')]
    max15x15Layout = [('maxXP', 'H'), ('maxFrags', 'B'), ('maxDamage', 'H')]
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    totalDefaults = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    totalDefaults.update(getStaticSizeBlockRecordValues(updateCtx, 'a15x15_2', a15x15_2packing))
    if bool(totalDefaults):
        blockFormat, blockValues = getNewStaticSizeBlockValues(totalLayout, totalDefaults)
    else:
        blockFormat, blockValues = ('', None)
    addBlock(updateCtx, 'total', blockFormat, blockValues)
    removeRecords(updateCtx, 'a15x15', a15x15packing)
    removeRecords(updateCtx, 'a15x15_2', a15x15_2packing)
    achievementsValues = getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking)
    addRecords(updateCtx, 'a15x15', [('winAndSurvived', 'I'), ('frags8p', 'I')], achievementsValues)
    addRecords(updateCtx, 'a7x7', [('winAndSurvived', 'I'), ('frags8p', 'I')], {})
    if bool(achievementsValues):
        blockFormat, blockValues = getNewStaticSizeBlockValues(max15x15Layout, achievementsValues)
    else:
        blockFormat, blockValues = ('', None)
    addBlock(updateCtx, 'max15x15', blockFormat, blockValues)
    addBlock(updateCtx, 'max7x7')
    removeRecords(updateCtx, 'achievements', achievementsPacking)
    setVersion(updateCtx, 65)
    return (65, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier65(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'inscriptions')
    addBlock(updateCtx, 'emblems')
    addBlock(updateCtx, 'camouflages')
    addBlock(updateCtx, 'compensation')
    setVersion(updateCtx, 66)
    return (66, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier66(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements', [('sniper2', 'H'), ('mainGun', 'H')], {})
    setVersion(updateCtx, 67)
    return (67, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier67(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    blockFormat = '<' + 'HHHHHHHH'
    blockValues = [0] * 8
    addBlock(updateCtx, 'achievements7x7', blockFormat, blockValues)
    setVersion(updateCtx, 68)
    return (68, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier68(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements7x7', [('tacticalBreakthrough', 'B')], {'tacticalBreakthrough': 0})
    setVersion(updateCtx, 69)
    return (69, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier69(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    headerValues = updateCtx['header'][1:]
    sumAllValues = sum(headerValues)
    vehDossierCompDescrLen = len(compDescr) - updateCtx['headerLength']
    a7x7Size = headerValues[6]
    max7x7Size = headerValues[11]
    achievements7x7Size = headerValues[16]
    if vehDossierCompDescrLen != sumAllValues and vehDossierCompDescrLen == sumAllValues - a7x7Size - max7x7Size:
        updateCtx['header'][7] = 0
        updateCtx['header'][12] = 0
        updateCtx['header'][17] = 0
        compDescr = struct.pack(updateCtx['headerFormat'], *updateCtx['header']) + compDescr[updateCtx['headerLength']:]
        if achievements7x7Size != 0:
            compDescr = compDescr[:-achievements7x7Size]
        updateCtx = {'dossierCompDescr': compDescr,
         'blockSizeFormat': 'H',
         'versionFormat': 'H',
         'blocksLayout': blocksLayout}
        getHeader(updateCtx)
        headerValues = updateCtx['header'][1:]
        sumAllValues = sum(headerValues)
        vehDossierCompDescrLen = len(compDescr) - updateCtx['headerLength']
    setVersion(updateCtx, 70)
    return (70, compDescr)


def __updateFromVehicleDossier70(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('potentialDamageReceived', 'I'), ('damageBlockedByArmor', 'I')]
    addRecords(updateCtx, 'a15x15_2', recordFormats, {})
    addRecords(updateCtx, 'company2', recordFormats, {})
    addRecords(updateCtx, 'clan2', recordFormats, {})
    addRecords(updateCtx, 'a7x7', recordFormats, {})
    setVersion(updateCtx, 71)
    return (71, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier71(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('battlesCountBefore9_0', 'I')]
    a15x15packing = {'battlesCount': (4, 'I')}
    a15x15defaults = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    addRecords(updateCtx, 'a15x15', recordFormats, {'battlesCountBefore9_0': a15x15defaults.get('battlesCount', 0)})
    companyPacking = {'battlesCount': (4, 'I')}
    companyDefaults = getStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking)
    addRecords(updateCtx, 'company', recordFormats, {'battlesCountBefore9_0': companyDefaults.get('battlesCount', 0)})
    clanPacking = {'battlesCount': (4, 'I')}
    clanDefaults = getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking)
    addRecords(updateCtx, 'clan', recordFormats, {'battlesCountBefore9_0': clanDefaults.get('battlesCount', 0)})
    a7x7packing = {'battlesCount': (4, 'I')}
    a7x7defaults = getStaticSizeBlockRecordValues(updateCtx, 'a7x7', a7x7packing)
    addRecords(updateCtx, 'a7x7', recordFormats, {'battlesCountBefore9_0': a7x7defaults.get('battlesCount', 0)})
    setVersion(updateCtx, 72)
    return (72, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier72(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    setVersion(updateCtx, 73)
    return (73, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier73(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'historical')
    addBlock(updateCtx, 'maxHistorical')
    setVersion(updateCtx, 74)
    return (74, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier74(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('godOfWar', 'H'),
     ('fightingReconnaissance', 'H'),
     ('fightingReconnaissanceMedal', 'H'),
     ('willToWinSpirit', 'H'),
     ('crucialShot', 'H'),
     ('crucialShotMedal', 'H'),
     ('forTacticalOperations', 'B')]
    defaultValues = {'godOfWar': 0,
     'fightingReconnaissance': 0,
     'fightingReconnaissanceMedal': 0,
     'willToWinSpirit': 0,
     'crucialShot': 0,
     'crucialShotMedal': 0,
     'forTacticalOperations': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 75)
    return (75, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier75(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('marksOnGun', 'B'), ('movingAvgDamage', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 76)
    return (76, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier76(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('medalMonolith', 'H'),
     ('medalAntiSpgFire', 'H'),
     ('medalGore', 'H'),
     ('medalCoolBlood', 'H'),
     ('medalStark', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 77)
    return (77, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier77(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'uniqueAchievements')
    setVersion(updateCtx, 78)
    return (78, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier78(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'fortBattles')
    addBlock(updateCtx, 'maxFortBattles')
    addBlock(updateCtx, 'fortSorties')
    addBlock(updateCtx, 'maxFortSorties')
    addBlock(updateCtx, 'fortAchievements')
    setVersion(updateCtx, 79)
    return (79, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier79(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('promisingFighter', 'H'),
     ('promisingFighterMedal', 'H'),
     ('heavyFire', 'H'),
     ('heavyFireMedal', 'H'),
     ('ranger', 'H'),
     ('rangerMedal', 'H'),
     ('fireAndSteel', 'H'),
     ('fireAndSteelMedal', 'H'),
     ('pyromaniac', 'H'),
     ('pyromaniacMedal', 'H'),
     ('noMansLand', 'H')]
    defaultValues = {'promisingFighter': 0,
     'promisingFighterMedal': 0,
     'heavyFire': 0,
     'heavyFireMedal': 0,
     'ranger': 0,
     'rangerMedal': 0,
     'fireAndSteel': 0,
     'fireAndSteelMedal': 0,
     'pyromaniac': 0,
     'pyromaniacMedal': 0,
     'noMansLand': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 80)
    return (80, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier80(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('damageRating', 'H')]
    addRecords(updateCtx, 'achievements', formats, {})
    setVersion(updateCtx, 81)
    return (81, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier81(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    awardCount = _count7x7awards(updateCtx)
    formats = [('guerrilla', 'H'),
     ('guerrillaMedal', 'H'),
     ('infiltrator', 'H'),
     ('infiltratorMedal', 'H'),
     ('sentinel', 'H'),
     ('sentinelMedal', 'H'),
     ('prematureDetonation', 'H'),
     ('prematureDetonationMedal', 'H'),
     ('bruteForce', 'H'),
     ('bruteForceMedal', 'H'),
     ('awardCount', 'I'),
     ('battleTested', 'B')]
    defaultValues = {'guerrilla': 0,
     'guerrillaMedal': 0,
     'infiltrator': 0,
     'infiltratorMedal': 0,
     'sentinel': 0,
     'sentinelMedal': 0,
     'prematureDetonation': 0,
     'prematureDetonationMedal': 0,
     'bruteForce': 0,
     'bruteForceMedal': 0,
     'awardCount': awardCount,
     'battleTested': 0}
    addRecords(updateCtx, 'achievements7x7', formats, defaultValues)
    setVersion(updateCtx, 82)
    return (82, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier82(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    layout = ['titleSniper',
     'invincible',
     'diehard',
     'handOfDeath',
     'armorPiercer',
     'tacticalBreakthrough']
    values = {}
    achievementsPacking = {'titleSniper': (88, 'B'),
     'invincible': (89, 'B'),
     'diehard': (90, 'B'),
     'handOfDeath': (93, 'B'),
     'armorPiercer': (94, 'B')}
    values.update(getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking))
    achievements7x7Packing = {'tacticalBreakthrough': (16, 'B')}
    values.update(getStaticSizeBlockRecordValues(updateCtx, 'achievements7x7', achievements7x7Packing))
    blockFormat, blockValues = getNewBinarySetBlockValues(layout, values)
    addBlock(updateCtx, 'singleAchievements', blockFormat, blockValues)
    removeRecords(updateCtx, 'achievements', achievementsPacking)
    removeRecords(updateCtx, 'achievements7x7', achievements7x7Packing)
    setVersion(updateCtx, 83)
    return (83, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier83(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    blockLayout = [('medalRotmistrov', 'B')]
    blockFormat, blockValues = getNewStaticSizeBlockValues(blockLayout, {'medalRotmistrov': 0})
    addBlock(updateCtx, 'clanAchievements', blockFormat, blockValues)
    setVersion(updateCtx, 84)
    return (84, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier84(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    a15x15packing = {'battlesCountBefore9_0': (68, 'I'),
     'battlesCountBefore8_8': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing)
    if values and values['battlesCountBefore8_8'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_8']
        setStaticSizeBlockRecordValues(updateCtx, 'a15x15', a15x15packing, values)
    clanPacking = {'battlesCountBefore9_0': (60, 'I'),
     'battlesCountBefore8_9': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking)
    if values and values['battlesCountBefore8_9'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_9']
        setStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking, values)
    companyPacking = {'battlesCountBefore9_0': (60, 'I'),
     'battlesCountBefore8_9': (56, 'I')}
    values = getStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking)
    if values and values['battlesCountBefore8_9'] > 0 and values['battlesCountBefore9_0'] == 0:
        values['battlesCountBefore9_0'] = values['battlesCountBefore8_9']
        setStaticSizeBlockRecordValues(updateCtx, 'company', companyPacking, values)
    setVersion(updateCtx, 85)
    return (85, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier85(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('impenetrable', 'H'),
     ('maxAimerSeries', 'B'),
     ('shootToKill', 'H'),
     ('fighter', 'H'),
     ('duelist', 'H'),
     ('demolition', 'H'),
     ('arsonist', 'H'),
     ('bonecrusher', 'H'),
     ('charmed', 'H'),
     ('even', 'H')]
    addRecords(updateCtx, 'achievements', recordFormats, {})
    setVersion(updateCtx, 86)
    return (86, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier86(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordFormats = [('wins', 'H'), ('capturedBasesInAttack', 'H'), ('capturedBasesInDefence', 'H')]
    addRecords(updateCtx, 'fortAchievements', recordFormats, {})
    setVersion(updateCtx, 87)
    return (87, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier87(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'rated7x7')
    addBlock(updateCtx, 'maxRated7x7')
    setVersion(updateCtx, 88)
    return (88, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier88(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    battleHeroes7x7Count = _countBattleHeroesBasedOn7x7Medals(updateCtx)
    if battleHeroes7x7Count > 0:
        achievementsPacking = {'battleHeroes': (20, 'H'),
         'medalKay': (38, 'B')}
        values = getStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking)
        if values:
            values['battleHeroes'] += battleHeroes7x7Count
            values['medalKay'] = _medalKayClass(values['battleHeroes'])
            setStaticSizeBlockRecordValues(updateCtx, 'achievements', achievementsPacking, values)
    setVersion(updateCtx, 89)
    return (89, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier89(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    gmDefaults = {}
    clanPacking = {'spotted': (32, 'I'),
     'damageDealt': (36, 'I'),
     'wins': (8, 'I'),
     'capturePoints': (44, 'I'),
     'losses': (12, 'I'),
     'survivedBattles': (16, 'I'),
     'droppedCapturePoints': (48, 'I'),
     'battlesCount': (4, 'I'),
     'damageReceived': (40, 'I'),
     'shots': (24, 'I'),
     'frags': (20, 'I'),
     'xp': (0, 'I'),
     'directHits': (28, 'I')}
    gmDefaults.update(getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking))
    clan2Packing = {'directHitsReceived': (12, 'I'),
     'damageAssistedTrack': (4, 'I'),
     'explosionHitsReceived': (24, 'I'),
     'potentialDamageReceived': (36, 'I'),
     'piercingsReceived': (20, 'I'),
     'originalXP': (0, 'I'),
     'damageAssistedRadio': (8, 'I'),
     'piercings': (32, 'I'),
     'explosionHits': (28, 'I'),
     'damageBlockedByArmor': (40, 'I'),
     'noDamageDirectHitsReceived': (16, 'I')}
    gmDefaults.update(getStaticSizeBlockRecordValues(updateCtx, 'clan2', clan2Packing))
    gmLayout = [('xp', 'I'),
     ('battlesCount', 'I'),
     ('wins', 'I'),
     ('losses', 'I'),
     ('survivedBattles', 'I'),
     ('frags', 'I'),
     ('shots', 'I'),
     ('directHits', 'I'),
     ('spotted', 'I'),
     ('damageDealt', 'I'),
     ('damageReceived', 'I'),
     ('capturePoints', 'I'),
     ('droppedCapturePoints', 'I'),
     ('originalXP', 'I'),
     ('damageAssistedTrack', 'I'),
     ('damageAssistedRadio', 'I'),
     ('directHitsReceived', 'I'),
     ('noDamageDirectHitsReceived', 'I'),
     ('piercingsReceived', 'I'),
     ('explosionHitsReceived', 'I'),
     ('explosionHits', 'I'),
     ('piercings', 'I'),
     ('winAndSurvived', 'I'),
     ('frags8p', 'I'),
     ('potentialDamageReceived', 'I'),
     ('damageBlockedByArmor', 'I')]
    blockFormat, blockValues = getNewStaticSizeBlockValues(gmLayout, gmDefaults)
    addBlock(updateCtx, 'globalMapCommon', blockFormat, blockValues)
    setVersion(updateCtx, 90)
    return (90, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier90(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    clanPacking = {'xpBefore8_9': (52, 'I'),
     'battlesCountBefore9_0': (60, 'I'),
     'battlesCountBefore8_9': (56, 'I')}
    clanValues = getStaticSizeBlockRecordValues(updateCtx, 'clan', clanPacking)
    recordFormats = [('xpBefore8_9', 'I'), ('battlesCountBefore8_9', 'I'), ('battlesCountBefore9_0', 'I')]
    addRecords(updateCtx, 'globalMapCommon', recordFormats, clanValues)
    setVersion(updateCtx, 91)
    return (91, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier91(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'maxGlobalMapCommon')
    setVersion(updateCtx, 92)
    return (92, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier92(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'fallout')
    addBlock(updateCtx, 'maxFallout')
    setVersion(updateCtx, 93)
    return (93, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier93(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'falloutAchievements')
    setVersion(updateCtx, 94)
    return (94, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier94(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    modes = ('a15x15_2', 'clan2', 'company2', 'a7x7', 'historical', 'fortBattles', 'fortSorties', 'rated7x7', 'globalMapCommon', 'fallout')
    for mode in modes:
        recordsFormat = [('battlesOnStunningVehicles', 'I'), ('stunNum', 'I'), ('damageAssistedStun', 'I')]
        addRecords(updateCtx, mode, recordsFormat, {})

    setVersion(updateCtx, 95)
    return (95, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier95(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    battlesOnStunningVehiclesOffsets = {'fortBattles': 104,
     'globalMapCommon': 116,
     'a15x15_2': 44,
     'fortSorties': 104,
     'historical': 104,
     'rated7x7': 104,
     'clan2': 44,
     'fallout': 128,
     'company2': 44,
     'a7x7': 108}
    for block, offset in battlesOnStunningVehiclesOffsets.iteritems():
        lastFieldKey = {'a7x7': 'battlesCountBefore9_0',
         'globalMapCommon': 'battlesCountBefore9_0',
         'fallout': 'deathCount'}.get(block, 'damageBlockedByArmor')
        packing = {lastFieldKey: (offset - 4, 'I'),
         'battlesOnStunningVehicles': (offset, 'I'),
         'stunNum': (offset + 4, 'I'),
         'damageAssistedStun': (offset + 8, 'I')}
        values = getStaticSizeBlockRecordValues(updateCtx, block, packing)
        if not values:
            continue
        lastField = values[lastFieldKey]
        stunNum = values['stunNum']
        damageAssistedStun = values['damageAssistedStun']
        if damageAssistedStun <= 65535:
            continue
        if 0 == stunNum:
            setStaticSizeBlockRecordValues(updateCtx, block, {lastFieldKey: (offset - 4, 'I'),
             'damageAssistedStun': (offset + 8, 'I')}, {lastFieldKey: lastField + (damageAssistedStun & 4294901760L),
             'damageAssistedStun': damageAssistedStun & 65535})
        if 0 != stunNum and damageAssistedStun > 65535:
            if 'a15x15_2' != block:
                continue
            else:
                piercingPacking = {'noDamageDirectHitsReceived': (16, 'I'),
                 'directHitsReceived': (12, 'I'),
                 'potentialDamageReceived': (36, 'I'),
                 'piercingsReceived': (20, 'I')}
                damageReceivedPacking = {'damageReceived': (40, 'I')}
                data = getStaticSizeBlockRecordValues(updateCtx, 'a15x15_2', piercingPacking)
                data.update(getStaticSizeBlockRecordValues(updateCtx, 'a15x15', damageReceivedPacking))
                if data['piercingsReceived'] < 50 or data['directHitsReceived'] < 50:
                    continue
                else:
                    potentialDamagePerHit = 1.0 * data['potentialDamageReceived'] / data['directHitsReceived']
                    aproxDamageBlockedByArmor = data['potentialDamageReceived'] - data['damageReceived']
                    if data['noDamageDirectHitsReceived'] < 50 or aproxDamageBlockedByArmor <= 65535:
                        continue
                    potentialDamagePerHitForBlockedDamage = 1.0 * lastField / data['noDamageDirectHitsReceived']
                    while 1:
                        aproxDamageBlockedByArmor >= lastField + (damageAssistedStun & 4294901760L) and potentialDamagePerHit > potentialDamagePerHitForBlockedDamage and lastField += 65536
                        damageAssistedStun -= 65536
                        potentialDamagePerHitForBlockedDamage = 1.0 * lastField / data['noDamageDirectHitsReceived']

                    if damageAssistedStun >= 0:
                        setStaticSizeBlockRecordValues(updateCtx, block, {lastFieldKey: (offset - 4, 'I'),
                         'damageAssistedStun': (offset + 8, 'I')}, {lastFieldKey: lastField,
                         'damageAssistedStun': damageAssistedStun})

    setVersion(updateCtx, 96)
    return (96, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier96(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'ranked')
    addBlock(updateCtx, 'maxRanked')
    addBlock(updateCtx, 'rankedSeasons')
    setVersion(updateCtx, 97)
    return (97, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier97(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    vehFortAchievementsPacking = {'wins': (8, 'H'),
     'capturedBasesInAttack': (10, 'H'),
     'capturedBasesInDefence': (12, 'H')}
    removeRecords(updateCtx, 'fortAchievements', vehFortAchievementsPacking)
    setVersion(updateCtx, 98)
    return (98, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier98(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'a30x30')
    addBlock(updateCtx, 'max30x30')
    setVersion(updateCtx, 99)
    return (99, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier99(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'epicBattle')
    addBlock(updateCtx, 'maxEpicBattle')
    addBlock(updateCtx, 'epicBattleAchievements')
    setVersion(updateCtx, 100)
    return (100, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier100(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsPacking = {'maxDamage': (3, 'H'),
     'maxFrags': (2, 'B'),
     'maxXP': (0, 'H')}
    oldValues = getStaticSizeBlockRecordValues(updateCtx, 'epicBattleAchievements', recordsPacking)
    if oldValues:
        newValues = getStaticSizeBlockRecordValues(updateCtx, 'max30x30', recordsPacking)
        if newValues:
            setStaticSizeBlockRecordValues(updateCtx, 'max30x30', recordsPacking, {name:max(oldValues.get(name, 0), newValues.get(name, 0)) for name in recordsPacking.iterkeys()})
        else:
            oldBlockCompDescr = getBlockCompDescr(updateCtx, 'epicBattleAchievements')
            setBlockCompDescr(updateCtx, 'max30x30', oldBlockCompDescr)
    setBlockCompDescr(updateCtx, 'epicBattleAchievements', '')
    setVersion(updateCtx, 101)
    return (101, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier101(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'maxRankedSeason1')
    addBlock(updateCtx, 'maxRankedSeason2')
    addBlock(updateCtx, 'maxRankedSeason3')
    setVersion(updateCtx, 102)
    return (102, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier102(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsFormat = [('marksOfMasteryCount1', 'H'),
     ('marksOfMasteryCount2', 'H'),
     ('marksOfMasteryCount3', 'H'),
     ('marksOfMasteryCount4', 'H')]
    addRecords(updateCtx, 'achievements', recordsFormat, {})
    setVersion(updateCtx, 103)
    return (103, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier103(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    recordsFormat = [('playedBonusBattles', 'I')]
    addRecords(updateCtx, 'ranked', recordsFormat, {})
    setVersion(updateCtx, 104)
    return (104, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier104(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'ranked_10x10')
    addBlock(updateCtx, 'maxRanked_10x10')
    setVersion(updateCtx, 105)
    return (105, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier105(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    rankedPacking = {'playedBonusBattles': (116, 'I')}
    rankedValues = getStaticSizeBlockRecordValues(updateCtx, 'ranked', rankedPacking)
    ranked10x10Values = getStaticSizeBlockRecordValues(updateCtx, 'ranked_10x10', rankedPacking)
    ranked10x10Values['playedBonusBattles'] = ranked10x10Values.get('playedBonusBattles', 0) + rankedValues.get('playedBonusBattles', 0)
    playedBonusBattlesRecords = [(116, 'I', ranked10x10Values['playedBonusBattles'])]
    updateStaticSizeBlockRecords(updateCtx, 'ranked_10x10', playedBonusBattlesRecords)
    setVersion(updateCtx, 106)
    return (106, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier106(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season1')
    addBlock(updateCtx, 'maxComp7Season1')
    setVersion(updateCtx, 107)
    return (107, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier107(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10',
     'comp7Season1',
     'maxComp7Season1']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season2')
    addBlock(updateCtx, 'maxComp7Season2')
    setVersion(updateCtx, 108)
    return (108, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier108(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10',
     'comp7Season1',
     'maxComp7Season1',
     'comp7Season2',
     'maxComp7Season2']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    formats = [('maxAssisted', 'H'), ('maxDamageBlockedByArmor', 'H')]
    addRecords(updateCtx, 'max15x15', formats, {})
    setVersion(updateCtx, 109)
    return (109, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier109(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10',
     'comp7Season1',
     'maxComp7Season1',
     'comp7Season2',
     'maxComp7Season2']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'comp7Season3')
    addBlock(updateCtx, 'maxComp7Season3')
    addBlock(updateCtx, 'comp7ArchiveGriffin')
    addBlock(updateCtx, 'maxComp7ArchiveGriffin')
    setVersion(updateCtx, 110)
    return (110, updateCtx['dossierCompDescr'])


def __updateFromVehicleDossier110(compDescr):
    blocksLayout = ['a15x15',
     'a15x15_2',
     'clan',
     'clan2',
     'company',
     'company2',
     'a7x7',
     'achievements',
     'vehTypeFrags',
     'total',
     'max15x15',
     'max7x7',
     'inscriptions',
     'emblems',
     'camouflages',
     'compensation',
     'achievements7x7',
     'historical',
     'maxHistorical',
     'uniqueAchievements',
     'fortBattles',
     'maxFortBattles',
     'fortSorties',
     'maxFortSorties',
     'fortAchievements',
     'singleAchievements',
     'clanAchievements',
     'rated7x7',
     'maxRated7x7',
     'globalMapCommon',
     'maxGlobalMapCommon',
     'fallout',
     'maxFallout',
     'falloutAchievements',
     'ranked',
     'maxRanked',
     'rankedSeasons',
     'a30x30',
     'max30x30',
     'epicBattle',
     'maxEpicBattle',
     'epicBattleAchievements',
     'maxRankedSeason1',
     'maxRankedSeason2',
     'maxRankedSeason3',
     'ranked_10x10',
     'maxRanked_10x10',
     'comp7Season1',
     'maxComp7Season1',
     'comp7Season2',
     'maxComp7Season2',
     'comp7Season3',
     'maxComp7Season3',
     'comp7ArchiveGriffin',
     'maxComp7ArchiveGriffin']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    comp7SeasonsPacking = {'spotted': (32, 'I'),
     'losses': (12, 'I'),
     'roleSkillUsed': (124, 'I'),
     'damageAssistedTrack': (56, 'I'),
     'damageReceived': (40, 'I'),
     'battlesOnStunningVehicles': (100, 'I'),
     'piercingsReceived': (72, 'I'),
     'originalXP': (52, 'I'),
     'damageAssistedRadio': (60, 'I'),
     'battlesCount': (4, 'I'),
     'survivedBattles': (16, 'I'),
     'winSeries': (112, 'I'),
     'piercings': (84, 'I'),
     'damageBlockedByArmor': (96, 'I'),
     'noDamageDirectHitsReceived': (68, 'I'),
     'xp': (0, 'I'),
     'droppedCapturePoints': (48, 'I'),
     'healthRepair': (128, 'I'),
     'directHitsReceived': (64, 'I'),
     'comp7PrestigePoints': (120, 'I'),
     'explosionHitsReceived': (76, 'I'),
     'winAndSurvived': (88, 'I'),
     'capturePoints': (44, 'I'),
     'potentialDamageReceived': (92, 'I'),
     'damageDealt': (36, 'I'),
     'damageAssistedStun': (108, 'I'),
     'squadWinSeries': (116, 'I'),
     'explosionHits': (80, 'I'),
     'wins': (8, 'I'),
     'poiCapturable': (132, 'I'),
     'frags': (20, 'I'),
     'stunNum': (104, 'I'),
     'shots': (24, 'I'),
     'directHits': (28, 'I')}
    comp7SeasonsNewPacking = {'spotted': (32, 'I'),
     'losses': (12, 'I'),
     'roleSkillUsed': (132, 'I'),
     'damageAssistedTrack': (56, 'I'),
     'damageReceived': (40, 'I'),
     'battlesOnStunningVehicles': (100, 'I'),
     'piercingsReceived': (72, 'I'),
     'originalXP': (52, 'I'),
     'damageAssistedRadio': (60, 'I'),
     'battlesCount': (4, 'I'),
     'survivedBattles': (16, 'I'),
     'winSeries': (112, 'I'),
     'piercings': (84, 'I'),
     'damageBlockedByArmor': (96, 'I'),
     'noDamageDirectHitsReceived': (68, 'I'),
     'xp': (0, 'I'),
     'droppedCapturePoints': (48, 'I'),
     'healthRepair': (136, 'I'),
     'comp7PrestigePoints': (128, 'I'),
     'directHitsReceived': (64, 'I'),
     'superSquadWins': (124, 'I'),
     'explosionHitsReceived': (76, 'I'),
     'winAndSurvived': (88, 'I'),
     'capturePoints': (44, 'I'),
     'potentialDamageReceived': (92, 'I'),
     'damageDealt': (36, 'I'),
     'superSquadBattlesCount': (120, 'I'),
     'damageAssistedStun': (108, 'I'),
     'squadWinSeries': (116, 'I'),
     'explosionHits': (80, 'I'),
     'wins': (8, 'I'),
     'poiCapturable': (140, 'I'),
     'frags': (20, 'I'),
     'stunNum': (104, 'I'),
     'shots': (24, 'I'),
     'directHits': (28, 'I')}
    seasonsNumber = 3
    archiveSeasonsGriffin(seasonsNumber, updateCtx, comp7SeasonsPacking, comp7SeasonsNewPacking)
    addRecords(updateCtx, 'comp7Season1', [('superSquadBattlesCount', 'I'), ('superSquadWins', 'I')], {})
    addRecords(updateCtx, 'comp7Season2', [('superSquadBattlesCount', 'I'), ('superSquadWins', 'I')], {})
    maxComp7SeasonsPacking = {'maxDamage': (3, 'H'),
     'maxXPVehicle': (5, 'I'),
     'maxDamageVehicle': (13, 'I'),
     'maxFrags': (2, 'B'),
     'maxXP': (0, 'H'),
     'maxHealthRepair': (29, 'H'),
     'maxComp7PrestigePointsVehicle': (19, 'I'),
     'maxEquipmentDamageDealt': (23, 'H'),
     'maxFragsVehicle': (9, 'I'),
     'maxSquadWinSeries': (37, 'H'),
     'maxComp7PrestigePoints': (17, 'H'),
     'maxWinSeries': (35, 'H'),
     'maxEquipmentDamageDealtVehicle': (25, 'I'),
     'maxHealthRepairVehicle': (31, 'I')}
    archiveMaxSeasonsGriffin(seasonsNumber, updateCtx, maxComp7SeasonsPacking)
    setVersion(updateCtx, 111)
    return (111, updateCtx['dossierCompDescr'])


def __bootstrapTankmanDossierFrom(ver, compDescr):
    return (ver, compDescr) if ver > 14 else (TANKMAN_DOSSIER_VERSION, dossiers2.custom.tankmen_dossier1_updater.updateDossierCompDescr(compDescr))


def __addTankmanDossierUpdaters(module, seq):
    for v in seq:
        updaterName = '__updateFromTankmanDossier%d' % (v,)
        if getattr(module, updaterName, None) is None:
            setattr(module, updaterName, partial(__bootstrapTankmanDossierFrom, v))
            getattr(module, updaterName).__name__ = updaterName

    return


__addTankmanDossierUpdaters(sys.modules[__name__], xrange(10, 64))

def __updateFromTankmanDossier64(compDescr):
    blocksLayout = ['total', 'achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements', [('huntsman', 'H')], {})
    setVersion(updateCtx, 65)
    return (65, updateCtx['dossierCompDescr'])


def __updateFromTankmanDossier65(compDescr):
    blocksLayout = ['total', 'achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'achievements', [('sniper2', 'H'), ('mainGun', 'H')], {})
    setVersion(updateCtx, 66)
    return (66, updateCtx['dossierCompDescr'])


def __updateFromClubDossier1(compDescr):
    blocksLayout = ['total',
     'clubBattles',
     'vehicles',
     'maps',
     'achievementsRated7x7']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addBlock(updateCtx, 'singleAchievementsRated7x7')
    setVersion(updateCtx, 2)
    return (2, updateCtx['dossierCompDescr'])


class DossierVersionUpdaterBase(VersionUpdaterBase):

    def __init__(self, logID, functionTemplate, latestVersion):
        super(DossierVersionUpdaterBase, self).__init__(functionTemplate, latestVersion)
        self.__logID = logID

    def updateVersion(self, currentVersion, compDescr):
        return self._updateToLatestVersion(currentVersion, lambda *args: False, self.__logID, compDescr)[0]


@singleton
class AccountDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Account dossier', ACCOUNT_DOSSIER_UPDATE_FUNCTION_TEMPLATE, ACCOUNT_DOSSIER_VERSION)


@singleton
class VehicleDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Vehicle dossier', VEHICLE_DOSSIER_UPDATE_FUNCTION_TEMPLATE, VEHICLE_DOSSIER_VERSION)


@singleton
class TankmanDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Tankman dossier', TANKMAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE, TANKMAN_DOSSIER_VERSION)


@singleton
class ClanDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Clan dossier', CLAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE, CLAN_DOSSIER_VERSION)


@singleton
class Rated7x7DossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Rated7x7 dossier', RATED7X7_DOSSIER_UPDATE_FUNCTION_TEMPLATE, RATED7X7_DOSSIER_VERSION)


@singleton
class ClubDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Club dossier', CLUB_DOSSIER_UPDATE_FUNCTION_TEMPLATE, CLUB_DOSSIER_VERSION)
