# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers/dossier_updaters.py
# Compiled at: 2011-11-02 13:49:22
import time
import fmt_storage
from itertools import chain
from config import RECORD_CONFIGS
from constants import DOSSIER_TYPE
from utils import unpackDossierCompDescr, RECORD_DEFAULT_VALUES

def getNewDossierData(version, recordsLayout, isExpanded, compDescr, unpackedData):
    data = {}
    for record in chain(*recordsLayout):
        data[record] = RECORD_DEFAULT_VALUES.get(record, 0)

    data['_version'] = version
    return (data, compDescr)


def getNewAccountDossierData(version, recordsLayout, isExpanded, compDescr, unpackedData):
    data, _ = getNewDossierData(version, recordsLayout, isExpanded, compDescr, unpackedData)
    data['creationTime'] = int(time.time())
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
        data = unpackDossierCompDescr(version, layout, record_packing, compDescr)
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
        record_packing = layout = None
        vehicle18 = fmt_storage.DOSSIER_FMTS['vehicle'][18]
        layout = vehicle18['layout']
        record_packing = vehicle18['record_packing']
        data = unpackDossierCompDescr(version, layout, record_packing, compDescr)
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
        data = unpackDossierCompDescr(version, layout, record_packing, compDescr)
    for record in ['company/xp',
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
     'clan/droppedCapturePoints']:
        data[record] = 0

    data['_version'] = version
    return (data, compDescr)
