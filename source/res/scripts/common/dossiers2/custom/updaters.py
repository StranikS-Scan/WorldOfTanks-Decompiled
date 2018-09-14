# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/updaters.py
import sys
import struct
from functools import partial
from dossiers2.common.updater_utils import getNewStaticSizeBlockValues, getStaticSizeBlockRecordValues
from dossiers2.common.updater_utils import getNewBinarySetBlockValues, setStaticSizeBlockRecordValues
from dossiers2.common.updater_utils import addBlock, removeBlock, addRecords, removeRecords
from dossiers2.common.updater_utils import setVersion, getHeader, getBlockSize
import dossiers2.custom.tankmen_dossier1_updater
from VersionUpdater import VersionUpdaterBase
from wotdecorators import singleton
ACCOUNT_DOSSIER_VERSION = 105
ACCOUNT_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromAccountDossier%d'
VEHICLE_DOSSIER_VERSION = 97
VEHICLE_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromVehicleDossier%d'
TANKMAN_DOSSIER_VERSION = 66
TANKMAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromTankmanDossier%d'
FORT_DOSSIER_VERSION = 3
FORT_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromFortDossier%d'
CLAN_DOSSIER_VERSION = 1
CLAN_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromClanDossier%d'
RATED7X7_DOSSIER_VERSION = 1
RATED7X7_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromRated7x7Dossier%d'
CLUB_DOSSIER_VERSION = 2
CLUB_DOSSIER_UPDATE_FUNCTION_TEMPLATE = '__updateFromClubDossier%d'

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
    addBlock(updateCtx, 'rankedCuts')
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
        assert vehDossierCompDescrLen == sumAllValues
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
     'maxFallout']
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


def __updateFromFortDossier1(compDescr):
    blocksLayout = ['total',
     'fortBattles',
     'fortSorties',
     'achievements']
    fortBattlesPacking = {'reservedInt32': (4, 'I'),
     'ownBaseLossCount': (24, 'I'),
     'enemyBaseCaptureCountInAttack': (28, 'I')}
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    removeRecords(updateCtx, 'fortBattles', fortBattlesPacking)
    addRecords(updateCtx, 'fortBattles', [('combatCount', 'I'),
     ('combatWins', 'I'),
     ('successDefenceCount', 'I'),
     ('successAttackCount', 'I'),
     ('captureEnemyBuildingTotalCount', 'I'),
     ('lossOwnBuildingTotalCount', 'I'),
     ('resourceCaptureCount', 'I'),
     ('resourceLossCount', 'I')], {})
    addRecords(updateCtx, 'total', [('reservedInt32', 'I')], {})
    setVersion(updateCtx, 2)
    return (2, updateCtx['dossierCompDescr'])


def __updateFromFortDossier2(compDescr):
    blocksLayout = ['total',
     'fortBattles',
     'fortSorties',
     'achievements']
    updateCtx = {'dossierCompDescr': compDescr,
     'blockSizeFormat': 'H',
     'versionFormat': 'H',
     'blocksLayout': blocksLayout}
    getHeader(updateCtx)
    addRecords(updateCtx, 'fortSorties', [('middleWins', 'I'), ('championWins', 'I'), ('absoluteWins', 'I')], {})
    setVersion(updateCtx, 3)
    return (3, updateCtx['dossierCompDescr'])


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
        return self._updateToLatestVersion(currentVersion, self.__logID, compDescr)[0]


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
class FortDossierVersionUpdater(DossierVersionUpdaterBase):

    def __init__(self):
        super(self.__class__, self).__init__('Fort dossier', FORT_DOSSIER_UPDATE_FUNCTION_TEMPLATE, FORT_DOSSIER_VERSION)


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
