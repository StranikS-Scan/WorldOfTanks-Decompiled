# Embedded file name: scripts/common/dossiers1/dossier_updaters.py
import time
import nations
import fmt_storage
from itertools import chain
from config import RECORD_CONFIGS
from constants import DOSSIER_TYPE
from utils import unpackDossierCompDescr, RECORD_DEFAULT_VALUES
from dependences import updateSinai, updatePattonValley, updateMedalKay

def getNewDossierData(version, recordsLayout, isExpanded, compDescr, unpackedData):
    data = {}
    for record in chain(*recordsLayout):
        data[record] = RECORD_DEFAULT_VALUES.get(record, 0)

    if 'creationTime' in data:
        data['creationTime'] = int(time.time())
    data['_version'] = version
    return (data, compDescr)


def updateDossier1(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.TANKMAN:
            tankman10 = fmt_storage.DOSSIER_FMTS['tankman'][10]
            layout = tankman10['layout']
            record_packing = tankman10['record_packing']
        elif dossierType == DOSSIER_TYPE.ACCOUNT:
            account19 = fmt_storage.DOSSIER_FMTS['account'][19]
            layout = account19['layout']
            record_packing = account19['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle17 = fmt_storage.DOSSIER_FMTS['vehicle'][17]
            layout = vehicle17['layout']
            record_packing = vehicle17['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    if dossierType == DOSSIER_TYPE.ACCOUNT or dossierType == DOSSIER_TYPE.VEHICLE:
        minFrags = RECORD_CONFIGS['beasthunter']
        beastFrags = data['fragsBeast']
        medals, series = divmod(beastFrags, minFrags)
        data['beasthunter'] = medals
    for medals in ['evileye',
     'medalHeroesOfRassenai',
     'medalDeLaglanda',
     'medalTamadaYoshio',
     'medalErohin',
     'medalHoroshilov',
     'medalLister']:
        data[medals] = 0

    data['_version'] = version
    return (data, compDescr)


def updateDossier2(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        vehicle18 = fmt_storage.DOSSIER_FMTS['vehicle'][18]
        layout = vehicle18['layout']
        record_packing = vehicle18['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['markOfMastery'] = 0
    data['_version'] = version
    return (data, compDescr)


def updateDossier3(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account20 = fmt_storage.DOSSIER_FMTS['account'][20]
            layout = account20['layout']
            record_packing = account20['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle19 = fmt_storage.DOSSIER_FMTS['vehicle'][19]
            layout = vehicle19['layout']
            record_packing = vehicle19['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    for record in ['company/xp',
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
     'clan/droppedCapturePoints']:
        data[record] = 0

    data['_version'] = version
    return (data, compDescr)


def updateDossier4(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account21 = fmt_storage.DOSSIER_FMTS['account'][21]
            layout = account21['layout']
            record_packing = account21['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    newA15x15Cut = {}
    for vehTypeCompDescr, (battlesCount, wins) in data['a15x15Cut'].iteritems():
        newA15x15Cut[vehTypeCompDescr] = (battlesCount, wins, 0)

    data['a15x15Cut'] = newA15x15Cut
    data['_version'] = version
    return (data, compDescr)


def updateDossier5(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.TANKMAN:
            tankman11 = fmt_storage.DOSSIER_FMTS['tankman'][11]
            layout = tankman11['layout']
            record_packing = tankman11['record_packing']
        elif dossierType == DOSSIER_TYPE.ACCOUNT:
            account22 = fmt_storage.DOSSIER_FMTS['account'][22]
            layout = account22['layout']
            record_packing = account22['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle20 = fmt_storage.DOSSIER_FMTS['vehicle'][20]
            layout = vehicle20['layout']
            record_packing = vehicle20['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    for medals in ['medalRadleyWalters',
     'medalLafayettePool',
     'medalBrunoPietro',
     'medalTarczay',
     'medalPascucci',
     'medalDumitru',
     'medalLehvaslaiho',
     'medalNikolas']:
        data[medals] = 0

    data['_version'] = version
    return (data, compDescr)


def updateDossier6(version, dossierType, cache, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.TANKMAN:
            tankman12 = fmt_storage.DOSSIER_FMTS['tankman'][12]
            layout = tankman12['layout']
            record_packing = tankman12['record_packing']
        elif dossierType == DOSSIER_TYPE.ACCOUNT:
            account23 = fmt_storage.DOSSIER_FMTS['account'][23]
            layout = account23['layout']
            record_packing = account23['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle21 = fmt_storage.DOSSIER_FMTS['vehicle'][21]
            layout = vehicle21['layout']
            record_packing = vehicle21['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    if dossierType == DOSSIER_TYPE.ACCOUNT or dossierType == DOSSIER_TYPE.VEHICLE:
        tankExpert = data['tankExpert']
        data['tankExpertStrg'] = 0
        killedVehTypes = set(data['vehTypeFrags'].iterkeys())
        data['tankExpertStrg'] = 1 if len(cache['vehiclesInTrees'] - killedVehTypes) == 0 or tankExpert else 0
        vehiclesInTreesByNation = cache['vehiclesInTreesByNation']
        for nationIdx in xrange(len(nations.NAMES)):
            if len(vehiclesInTreesByNation[nationIdx]) == 0:
                continue
            if len(vehiclesInTreesByNation[nationIdx] - killedVehTypes) == 0:
                data['tankExpertStrg'] |= 1 << nationIdx + 1

        sinaiVehicles = cache['sinaiVehicles']
        data['fragsSinai'] = 0
        for vehCompDescr, frags in data['vehTypeFrags'].iteritems():
            if vehCompDescr in sinaiVehicles:
                data['fragsSinai'] += frags

        data['sinai'] = 0
        updateSinai(data, None, None, None)
        data['heroesOfRassenay'] = 1 if data['maxFrags'] == 15 else 0
    if dossierType == DOSSIER_TYPE.ACCOUNT:
        data['mechanicEngineerStrg'] = 0
        data['mechanicEngineer'] = 0
    if dossierType == DOSSIER_TYPE.TANKMAN:
        data['heroesOfRassenay'] = 0
    data['_version'] = version
    return (data, compDescr)


def updateDossier7(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account24 = fmt_storage.DOSSIER_FMTS['account'][24]
            layout = account24['layout']
            record_packing = account24['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['_dynRecPos_account'] = (0, 0, 0)
    data['rareAchievements'] = list()
    data['_version'] = version
    return (data, compDescr)


def updateDossier8(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account25 = fmt_storage.DOSSIER_FMTS['account'][25]
            layout = account25['layout']
            record_packing = account25['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle22 = fmt_storage.DOSSIER_FMTS['vehicle'][22]
            layout = vehicle22['layout']
            record_packing = vehicle22['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['medalCrucialContribution'] = 0
    data['medalBrothersInArms'] = 0
    data['_version'] = version
    return (data, compDescr)


def updateDossier9(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.TANKMAN:
            tankman13 = fmt_storage.DOSSIER_FMTS['tankman'][13]
            layout = tankman13['layout']
            record_packing = tankman13['record_packing']
        elif dossierType == DOSSIER_TYPE.ACCOUNT:
            account26 = fmt_storage.DOSSIER_FMTS['account'][26]
            layout = account26['layout']
            record_packing = account26['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle23 = fmt_storage.DOSSIER_FMTS['vehicle'][23]
            layout = vehicle23['layout']
            record_packing = vehicle23['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['medalDeLanglade'] = 0
    data['medalTamadaYoshio'] = 0
    if dossierType == DOSSIER_TYPE.ACCOUNT or dossierType == DOSSIER_TYPE.VEHICLE:
        data['bombardier'] = 0
        data['huntsman'] = 0
        data['alaric'] = 0
        data['sturdy'] = 0
        data['ironMan'] = 0
        data['luckyDevil'] = 0
    data['_version'] = version
    return (data, compDescr)


def updateDossier10(version, dossierType, cache, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account27 = fmt_storage.DOSSIER_FMTS['account'][27]
            layout = account27['layout']
            record_packing = account27['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle24 = fmt_storage.DOSSIER_FMTS['vehicle'][24]
            layout = vehicle24['layout']
            record_packing = vehicle24['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    pattonVehicles = cache['pattonVehicles']
    data['fragsPatton'] = 0
    for vehCompDescr, frags in data['vehTypeFrags'].iteritems():
        if vehCompDescr in pattonVehicles:
            data['fragsPatton'] += frags

    data['pattonValley'] = 0
    updatePattonValley(data, None, None, None)
    data['_version'] = version
    return (data, compDescr)


def updateDossier11(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account28 = fmt_storage.DOSSIER_FMTS['account'][28]
            layout = account28['layout']
            record_packing = account28['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle25 = fmt_storage.DOSSIER_FMTS['vehicle'][25]
            layout = vehicle25['layout']
            record_packing = vehicle25['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['battleHeroes'] += data['evileye']
    updateMedalKay(data, None, None, None)
    data['_version'] = version
    return (data, compDescr)


def updateDossier12(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        if dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle26 = fmt_storage.DOSSIER_FMTS['vehicle'][26]
            layout = vehicle26['layout']
            record_packing = vehicle26['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['creationTime'] = 1356998400
    data['_version'] = version
    return (data, compDescr)


def updateDossier13(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account29 = fmt_storage.DOSSIER_FMTS['account'][29]
            layout = account29['layout']
            record_packing = account29['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle27 = fmt_storage.DOSSIER_FMTS['vehicle'][27]
            layout = vehicle27['layout']
            record_packing = vehicle27['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    data['lumberjack'] = 0
    data['_version'] = version
    return (data, compDescr)


def updateDossier14(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        record_packing = layout = None
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account30 = fmt_storage.DOSSIER_FMTS['account'][30]
            layout = account30['layout']
            record_packing = account30['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    newA15x15Cut = {}
    for vehTypeCompDescr, (battlesCount, wins, markOfMastery) in data['a15x15Cut'].iteritems():
        newA15x15Cut[vehTypeCompDescr] = (battlesCount,
         wins,
         markOfMastery,
         0)

    data['a15x15Cut'] = newA15x15Cut
    data['_version'] = version
    return (data, compDescr)


def updateDossier15(version, dossierType, isExpaned, compDescr, unpackedData):
    data = unpackedData
    if not isExpaned:
        if dossierType == DOSSIER_TYPE.ACCOUNT:
            account31 = fmt_storage.DOSSIER_FMTS['account'][31]
            layout = account31['layout']
            record_packing = account31['record_packing']
        elif dossierType == DOSSIER_TYPE.VEHICLE:
            vehicle28 = fmt_storage.DOSSIER_FMTS['vehicle'][28]
            layout = vehicle28['layout']
            record_packing = vehicle28['record_packing']
        data = unpackDossierCompDescr(layout, record_packing, compDescr)
    for record in ('treesCut', 'originalXP', 'damageAssistedTrack', 'damageAssistedRadio', 'mileage', 'directHitsReceived', 'noDamageDirectHitsReceived', 'piercingsReceived', 'explosionHitsReceived', 'explosionHits', 'piercings'):
        data[record] = 0

    data['xpBefore8_8'] = data['xp']
    data['battlesCountBefore8_8'] = data['battlesCount']
    data['_version'] = version
    return (data, compDescr)
