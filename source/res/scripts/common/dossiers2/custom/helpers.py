# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/helpers.py
import typing
from constants import INVOICE_EMITTER
from achievements20.cache import getCache as getAchievementsCache
from debug_utils import LOG_SENTRY
from dossiers2.custom.records import RECORDS, RECORD_INDICES, RECORD_DB_IDS, DB_ID_TO_RECORD
from dossiers2.custom.cache import getCache
from nations import ALL_NATIONS_INDEX
from optional_bonuses import BONUS_MERGERS

def getTankExpertRequirements(vehTypeFrags, nationID=ALL_NATIONS_INDEX):
    cache = getCache()
    killedVehTypes = set(vehTypeFrags.iterkeys())
    res = {'tankExpert': cache['vehiclesInTrees'] - killedVehTypes}
    if nationID == ALL_NATIONS_INDEX:
        nationIDs = cache['nationsWithVehiclesInTree']
    else:
        nationIDs = [nationID]
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    for nationIdx in nationIDs:
        res[''.join(['tankExpert', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - killedVehTypes

    return res


def getMechanicEngineerRequirements(defaultUnlocks, unlocks, nationID=ALL_NATIONS_INDEX):
    cache = getCache()
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    res = {'mechanicEngineer': cache['vehiclesInTrees'] - defaultUnlocks - unlocks}
    if nationID == ALL_NATIONS_INDEX:
        nationIDs = cache['nationsWithVehiclesInTree']
    else:
        nationIDs = [nationID]
    for nationIdx in nationIDs:
        res[''.join(['mechanicEngineer', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - defaultUnlocks - unlocks

    return res


def getVehicleCollectorRequirements(inventoryVehicles, nationID=ALL_NATIONS_INDEX):
    cache = getCache()
    collectorVehicles = getAllCollectorVehicles()
    res = {'collectorVehicle': collectorVehicles - inventoryVehicles}
    collectorVehiclesByNations = cache['collectorVehiclesByNations']
    nationIDs = collectorVehiclesByNations.keys() if nationID == ALL_NATIONS_INDEX else [nationID]
    for nationIdx in nationIDs:
        achievementName = ''.join(['collectorVehicle', str(nationIdx)])
        collectorVehiclesByNation = collectorVehiclesByNations.get(nationIdx, set())
        if collectorVehiclesByNation:
            res[achievementName] = collectorVehiclesByNation - inventoryVehicles

    return res


def getAllCollectorVehicles(nationID=ALL_NATIONS_INDEX):
    cache = getCache()
    collectorVehicles = set()
    collectorVehiclesByNations = cache['collectorVehiclesByNations']
    if nationID == ALL_NATIONS_INDEX:
        for collectorVehiclesInNation in collectorVehiclesByNations.itervalues():
            collectorVehicles.update(collectorVehiclesInNation)

    else:
        collectorVehicles.update(collectorVehiclesByNations.get(nationID, set()))
    return collectorVehicles


def getRecordMaxValue(block, record):
    recordPacking = RECORDS[RECORD_INDICES[block, record]]
    return 1 if recordPacking[2] == 'b' or recordPacking[2] == 'bs' else recordPacking[4]


def updateTankExpert(dossierDescr, vehTypeFrags, nationID):
    res = getTankExpertRequirements(vehTypeFrags, nationID)
    for record, value in res.iteritems():
        if len(value) == 0:
            if not dossierDescr['achievements'][record]:
                dossierDescr['achievements'][record] = True
                dossierDescr.addPopUp('achievements', record, True)


def updateMechanicEngineer(dossierDescr, defaultUnlocks, unlocks, nationID):
    res = getMechanicEngineerRequirements(defaultUnlocks, unlocks, nationID)
    for record, value in res.iteritems():
        if len(value) == 0:
            if not dossierDescr['achievements'][record]:
                dossierDescr['achievements'][record] = True
                dossierDescr.addPopUp('achievements', record, True)


def updateVehicleCollector(dossierDescr, inventoryVehicles, nationID):
    res = getVehicleCollectorRequirements(inventoryVehicles, nationID)
    for record, value in res.iteritems():
        if len(value) == 0:
            if not dossierDescr['achievements'][record]:
                dossierDescr['achievements'][record] = True
                dossierDescr.addPopUp('achievements', record, True)


def updateVehicleBoughtListAchievements(dossierDescr, vehDescr):
    if vehDescr.type.isCollectorVehicle or vehDescr.type.isPremium:
        return
    level = vehDescr.level
    if 5 <= level <= 10:
        medalName = 'steamGetTankLevel{0}Medal'.format(level)
        if not dossierDescr['steamAchievements'][medalName]:
            dossierDescr['steamAchievements'][medalName] = True


def updateRareAchievements(dossierDescr, achievements):
    block = dossierDescr['rareAchievements']
    for achievement in achievements:
        if achievement > 0:
            block.append(achievement)
        if achievement < 0:
            try:
                block.remove(abs(achievement))
            except:
                pass


def processAchievements20(dossierDescr, receivedItemCompDescrs, item, invoiceProcessor):
    achievementsCache = getAchievementsCache()
    achievements = achievementsCache.getAchievementsByItem(item, receivedItemCompDescrs)
    if not achievements:
        return
    else:
        achievementBlockBackups = {}
        for achievement in achievements:
            achievementType = achievement.type
            if achievementType not in achievementBlockBackups:
                achievementBlockBackups[achievementType] = dict(dossierDescr[achievementType])
            achievement.updateValueInDossier(dossierDescr)

        dossierChanges = dossierDescr.getChanges()
        rewards = {}
        for achievementType, blockBackup in achievementBlockBackups.iteritems():
            for achievementID in dossierChanges.get(achievementType, ()):
                achievement = achievementsCache.getAchievementByID(achievementType, achievementID)
                currentValue, currentStage, currentTimestamp = achievement.getCurrentDataFromDossier(dossierDescr)
                if blockBackup.get(achievementID, (0, 0))[1] != currentStage:
                    achievementRewards = achievement.getStageBonusByValue(currentStage)
                    if achievementRewards:
                        for key, value in achievementRewards.iteritems():
                            if key in BONUS_MERGERS:
                                BONUS_MERGERS[key](rewards, key, value, False, 1, None)

        if rewards:
            status, error, invoice = invoiceProcessor.processData(rewards, 0, 0, emitterID=INVOICE_EMITTER.DEVELOPMENT, needRunInvoiceUpdaters=False)
            if status < 0:
                LOG_SENTRY('Failed to add achievement rewards. Error - {}, invoice - {}, dossier changes - {}'.format(error, invoice, dossierChanges))
        return


def convertDossierPathToDBId(path):
    return RECORD_DB_IDS[path]


def convertDBIdToDossierPath(value):
    return DB_ID_TO_RECORD[value]
