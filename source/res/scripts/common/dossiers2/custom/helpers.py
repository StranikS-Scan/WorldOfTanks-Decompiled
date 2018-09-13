# Embedded file name: scripts/common/dossiers2/custom/helpers.py
from dossiers2.custom.records import RECORDS, RECORD_INDICES
from dossiers2.custom.cache import getCache

def getTankExpertRequirements(vehTypeFrags, nationID = -1):
    cache = getCache()
    killedVehTypes = set(vehTypeFrags.iterkeys())
    res = {'tankExpert': cache['vehiclesInTrees'] - killedVehTypes}
    if nationID == -1:
        nationIDs = cache['nationsWithVehiclesInTree']
    else:
        nationIDs = [nationID]
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    for nationIdx in nationIDs:
        res[''.join(['tankExpert', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - killedVehTypes

    return res


def getMechanicEngineerRequirements(defaultUnlocks, unlocks, nationID = -1):
    cache = getCache()
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    res = {'mechanicEngineer': cache['vehiclesInTrees'] - defaultUnlocks - unlocks}
    if nationID == -1:
        nationIDs = cache['nationsWithVehiclesInTree']
    else:
        nationIDs = [nationID]
    for nationIdx in nationIDs:
        res[''.join(['mechanicEngineer', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - defaultUnlocks - unlocks

    return res


def getRecordMaxValue(block, record):
    recordPacking = RECORDS[RECORD_INDICES[block, record]]
    if recordPacking[2] == 'b' or recordPacking[2] == 'bs':
        return 1
    raise recordPacking[2] == 'p' or AssertionError
    return recordPacking[4]


def updateMechanicEngineer(dossierDescr, defaultUnlocks, unlocks, nationID):
    res = getMechanicEngineerRequirements(defaultUnlocks, unlocks, nationID)
    for record, value in res.iteritems():
        if len(value) == 0:
            dossierDescr['achievements'][record] = True
            dossierDescr.addPopUp('achievements', record, True)


def updateRareAchievements(dossierDescr, achievements):
    block = dossierDescr['rareAchievements']
    for achievement in achievements:
        if achievement > 0:
            block.append(achievement)
        elif achievement < 0:
            try:
                block.remove(abs(achievement))
            except:
                pass
