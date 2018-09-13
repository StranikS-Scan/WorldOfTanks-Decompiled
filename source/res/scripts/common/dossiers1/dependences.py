# Embedded file name: scripts/common/dossiers1/dependences.py
import nations
import collections
from config import RECORD_CONFIGS

def getTankExpertRequirements(cache, vehTypeFrags):
    res = {}
    killedVehTypes = set(vehTypeFrags.iterkeys())
    res['tankExpert'] = cache['vehiclesInTrees'] - killedVehTypes
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    for nationIdx in xrange(len(nations.NAMES)):
        if len(vehiclesInTreesByNation[nationIdx]) == 0:
            continue
        res[''.join(['tankExpert', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - killedVehTypes

    return res


def getMechanicEngineerRequirements(cache, defaultUnlocks, unlocks, nationID = -1):
    res = {}
    res['mechanicEngineer'] = cache['vehiclesInTrees'] - defaultUnlocks - unlocks
    vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
    if nationID == -1:
        nationIDs = range(len(nations.NAMES))
    else:
        nationIDs = [nationID]
    for nationIdx in nationIDs:
        if len(vehiclesInTreesByNation[nationIdx]) == 0:
            continue
        res[''.join(['mechanicEngineer', str(nationIdx)])] = vehiclesInTreesByNation[nationIdx] - defaultUnlocks - unlocks

    return res


def buildDependencies2(dependencies):
    dependencies2 = collections.defaultdict(list)
    for record, (affectingRecords, updater) in dependencies.iteritems():
        for affectingRecord in affectingRecords:
            dependencies2[affectingRecord].append(updater)

    return dependencies2


def updateBattleHeroes(dossierDescr, affectingRecord, value, prevValue):
    dossierDescr['battleHeroes'] = dossierDescr['battleHeroes'] + value - prevValue


def updateMedalKay(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalCarius(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalKnispel(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalPoppel(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalAbrams(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalLeClerc(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalLavrinenko(dossierDescr, affectingRecord, value, prevValue):
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


def updateMedalEkins(dossierDescr, affectingRecord, value, prevValue):
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


def updateBeasthunter(dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['beasthunter']
    beastFrags = dossierDescr['fragsBeast']
    medals, series = divmod(beastFrags, minFrags)
    if dossierDescr['beasthunter'] != medals:
        dossierDescr['beasthunter'] = medals


def updateSinai(dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['sinai']
    sinaiFrags = dossierDescr['fragsSinai']
    medals, series = divmod(sinaiFrags, minFrags)
    if dossierDescr['sinai'] != medals:
        dossierDescr['sinai'] = medals


def updatePattonValley(dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['pattonValley']
    fragsPatton = dossierDescr['fragsPatton']
    medals, series = divmod(fragsPatton, minFrags)
    if dossierDescr['pattonValley'] != medals:
        dossierDescr['pattonValley'] = medals


def updateMousebane(cache, dossierDescr, affectingRecord, value, prevValue):
    minFrags = RECORD_CONFIGS['mousebane']
    mausFrags = dossierDescr['vehTypeFrags'].get(cache['mausTypeCompDescr'], 0)
    medals, series = divmod(mausFrags, minFrags)
    if dossierDescr['mousebane'] != medals:
        dossierDescr['mousebane'] = medals


def updateTankExpert(cache, dossierDescr, affectingRecord, vehTypeFrags, prevValue):
    res = getTankExpertRequirements(cache, vehTypeFrags)
    resOld = getTankExpertRequirements(cache, prevValue)
    tankExperts = set()
    for record, value in res.iteritems():
        if len(value) == 0:
            tankExperts.add(record)

    for record, value in resOld.iteritems():
        if len(value) == 0:
            tankExperts.discard(record)

    for record in tankExperts:
        dossierDescr[record] = True


def updateMechanicEngineer(dossierDescr, cache, defaultUnlocks, unlocks, nationID):
    res = getMechanicEngineerRequirements(cache, defaultUnlocks, unlocks, nationID)
    for record, value in res.iteritems():
        if len(value) == 0:
            dossierDescr[record] = True


def updateMaxSniperSeries(dossierDescr, affectingRecord, value, prevValue):
    maxSniperSeries = dossierDescr['maxSniperSeries']
    if dossierDescr['sniperSeries'] > maxSniperSeries:
        dossierDescr['maxSniperSeries'] = dossierDescr['sniperSeries']


def updateTitleSniper(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['titleSniper']
    if dossierDescr['maxSniperSeries'] >= minLength:
        dossierDescr['titleSniper'] = 1


def updateMaxInvincibleSeries(dossierDescr, affectingRecord, value, prevValue):
    maxInvincibleSeries = dossierDescr['maxInvincibleSeries']
    if dossierDescr['invincibleSeries'] > maxInvincibleSeries:
        dossierDescr['maxInvincibleSeries'] = dossierDescr['invincibleSeries']


def updateInvincible(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['invincible']
    if dossierDescr['maxInvincibleSeries'] >= minLength:
        dossierDescr['invincible'] = 1


def updateMaxDiehardSeries(dossierDescr, affectingRecord, value, prevValue):
    maxDiehardSeries = dossierDescr['maxDiehardSeries']
    if dossierDescr['diehardSeries'] > maxDiehardSeries:
        dossierDescr['maxDiehardSeries'] = dossierDescr['diehardSeries']


def updateDiehard(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['diehard']
    if dossierDescr['maxDiehardSeries'] >= minLength:
        dossierDescr['diehard'] = 1


def updateMaxKillingSeries(dossierDescr, affectingRecord, value, prevValue):
    maxKillingSeries = dossierDescr['maxKillingSeries']
    if dossierDescr['killingSeries'] > maxKillingSeries:
        dossierDescr['maxKillingSeries'] = dossierDescr['killingSeries']


def updateHandOfDeath(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['handOfDeath']
    if dossierDescr['maxKillingSeries'] >= minLength:
        dossierDescr['handOfDeath'] = 1


def updateMaxPiercingSeries(dossierDescr, affectingRecord, value, prevValue):
    maxPiercingSeries = dossierDescr['maxPiercingSeries']
    if dossierDescr['piercingSeries'] > maxPiercingSeries:
        dossierDescr['maxPiercingSeries'] = dossierDescr['piercingSeries']


def updateArmorPiercer(dossierDescr, affectingRecord, value, prevValue):
    minLength = RECORD_CONFIGS['armorPiercer']
    if dossierDescr['maxPiercingSeries'] >= minLength:
        dossierDescr['armorPiercer'] = 1


def updateRareAchievements(dossierDescr, achievements):
    newAchievements = list(dossierDescr['rareAchievements'])
    for achievement in achievements:
        if achievement > 0:
            newAchievements.append(achievement)
        elif achievement < 0:
            try:
                newAchievements.remove(abs(achievement))
            except:
                pass

    dossierDescr['rareAchievements'] = newAchievements
