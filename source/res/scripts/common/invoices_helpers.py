# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/invoices_helpers.py
from constants import DOSSIER_TYPE
from dossiers2.custom.clan_layout import CLAN_DOSSIER_LIST_BLOCKS
from dossiers2.custom.account_layout import ACCOUNT_DOSSIER_STATIC_BLOCKS, ACCOUNT_DOSSIER_BINARY_SET_BLOCKS, ACCOUNT_DOSSIER_BLOCKS, ACCOUNT_DOSSIER_DICT_BLOCKS, ACCOUNT_DOSSIER_LIST_BLOCKS

def checkAccountDossierOperation(dossierType, blockName, recordName, opType):
    if dossierType not in (DOSSIER_TYPE.ACCOUNT,):
        return (False, 'Invalid dossier type')
    if not opType:
        return (False, 'Dossier operation param required')
    if blockName in ACCOUNT_DOSSIER_STATIC_BLOCKS or blockName in ACCOUNT_DOSSIER_BINARY_SET_BLOCKS:
        blockBuilder = ACCOUNT_DOSSIER_BLOCKS[blockName]
        if not (recordName in blockBuilder.recordsLayout or recordName.startswith('tankExpert') or recordName.startswith('mechanicEngineer')):
            return (False, 'Invalid dossier record')
        if opType not in ('add', 'set'):
            return (False, 'Invalid dossier operation')
    elif blockName in ACCOUNT_DOSSIER_DICT_BLOCKS:
        if opType not in ('set', 'append'):
            return (False, 'Invalid dossier operation')
    elif blockName in ACCOUNT_DOSSIER_LIST_BLOCKS:
        if opType not in ('append',):
            return (False, 'Invalid dossier operation')
    else:
        return (False, 'Dossier block invoice change not supported')
    return (True, '')


def checkClanDossierOperation(dossierType, blockName, recordName, opType):
    if dossierType not in (DOSSIER_TYPE.CLAN,):
        return (False, 'Invalid dossier type')
    if not opType:
        return (False, 'Dossier operation param required')
    if blockName in CLAN_DOSSIER_LIST_BLOCKS:
        if opType not in ('append',):
            return (False, 'Invalid dossier operation')
    else:
        return (False, 'Dossier block invoice change not supported')
    return (True, '')


def getLogDefaultsDossierOperation(finOpType, itemTypeIdx, partnerID=0, actionSetID=0):
    return {'opType': finOpType,
     'itemTypeIdx': itemTypeIdx,
     'partnerID': partnerID,
     'actionSetID': actionSetID,
     'valueTypeID': 0,
     'secValueTypeID': 0,
     'valueAmount': 0,
     'itemNumber': 0,
     'secValueAmount': 0,
     'vehTypeCompDescr': 0,
     'typeCompDescr': 0}
