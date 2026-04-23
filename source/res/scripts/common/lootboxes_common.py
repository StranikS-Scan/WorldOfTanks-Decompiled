# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/lootboxes_common.py
from string import lower
from typing import TYPE_CHECKING
from constants import LOOTBOX_KEY_PREFIX, LOOTBOX_TOKEN_PREFIX, VERY_BIG_TIME
from items import makeIntCompactDescrByID, parseIntCompactDescr
from items.components.c11n_constants import CustomizationNamesToTypes, CustomizationTypeNames
from optional_bonuses import BONUS_MERGERS
from soft_exception import SoftException
AVAILABLE_STATISTICS_STORAGE = ('pdata', 'webservice')
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Union

class _LootboxTokenPrefix(object):
    LB_COMP = 'lb_comp:'
    LB_LIMIT_ITEM = 'lb_limit_item:'


class _TokenPostfix(object):
    HIDDEN_FROM_CLIENT = '_srv'
    NO_LOG = '_no_log'


def makeLootboxTokenID(boxID):
    return LOOTBOX_TOKEN_PREFIX + str(boxID)


def makeLBKeyTokenID(keyID):
    return LOOTBOX_KEY_PREFIX + str(keyID)


def makeLootboxID(tokenName):
    try:
        if tokenName.startswith(LOOTBOX_TOKEN_PREFIX):
            strID = tokenName[len(LOOTBOX_TOKEN_PREFIX):]
            return int(strID)
    except Exception:
        pass

    raise SoftException('Invalid tokenName: {}'.format(tokenName))


def makeLBKeyID(tokenName):
    try:
        if tokenName.startswith(LOOTBOX_KEY_PREFIX):
            strID = tokenName[len(LOOTBOX_KEY_PREFIX):]
            return int(strID)
    except Exception:
        pass

    raise SoftException('Invalid tokenName: {}'.format(tokenName))


def isLootboxToken(tokenName):
    try:
        makeLootboxID(tokenName)
        return True
    except Exception:
        return False


def __pruneVehicles(rewards):
    result = []
    for vehiclesDict in rewards:
        newVehiclesDict = {}
        for vehCD, vehicleData in vehiclesDict.iteritems():
            if 'rentCompensation' in vehicleData:
                continue
            if 'customCompensation' in vehicleData:
                continue
            newVehiclesDict[vehCD] = vehicleData

        if newVehiclesDict:
            result.append(newVehiclesDict)

    return result


def __pruneTokens(rewards):
    result = {}
    for tokenID, data in rewards.iteritems():
        maySendToClient = not any({tokenID.endswith(_TokenPostfix.NO_LOG),
         tokenID.endswith(_TokenPostfix.HIDDEN_FROM_CLIENT),
         tokenID.startswith(_LootboxTokenPrefix.LB_COMP),
         tokenID.startswith(_LootboxTokenPrefix.LB_LIMIT_ITEM),
         data.get('count', 0) < 0})
        if not maySendToClient:
            continue
        result[tokenID] = data

    return result


def __pruneCustomizations(rewards):
    result = []
    for customization in rewards:
        if customization.get('boundToCurrentVehicle', False):
            continue
        if customization.get('customCompensation'):
            continue
        result.append(customization)

    return result


_PRUNE_MERGERS = {'vehicles': __pruneVehicles,
 'tokens': __pruneTokens,
 'customizations': __pruneCustomizations,
 'meta': lambda v: None}

def mergeDiffStat(storage, diff):
    for key, value in diff.iteritems():
        if key in _PRUNE_MERGERS:
            value = _PRUNE_MERGERS[key](value)
            if not value:
                continue
        if key in BONUS_MERGERS:
            BONUS_MERGERS[key](storage, key, value, False, 1, None)

    return


REWARD_ITEM_IDS = {'freeXP': 1,
 'credits': 2,
 'gold': 3,
 'crystal': 4,
 'eventCoin': 5,
 'bpcoin': 6,
 'equipCoin': 7,
 'premium_plus': 8,
 'slots': 9,
 'berths': 10,
 'items': 11,
 'vehicles': 12,
 'tankmen': 13,
 'crewSkins': 14,
 'tokens': 15,
 'goodies': 16,
 'customizations': 17,
 'dossier': 18,
 'blueprints': 19,
 'entitlements': 20,
 'currencies': 21,
 'dogTagComponents': 22}
ID_TO_NAME = dict(((v, k) for k, v in REWARD_ITEM_IDS.iteritems()))
EXTENSIONS_CONVERTER_PROCESSOR = {}
EXTENSIONS_UNPACK_PROCESSOR = {}

def __convertVehicles(_, rewards):
    result = []
    for vehiclesDict in rewards:
        for vehCD in vehiclesDict.iterkeys():
            convertVehicleDict = {'item_type_id': REWARD_ITEM_IDS['vehicles'],
             'item_type_cd': vehCD,
             'amount': 1}
            result.append(convertVehicleDict)

    return result


def __convertTokens(_, rewards):
    result = []
    for tokenName, tokenData in rewards.iteritems():
        convertTokenDict = {'value_type_id': REWARD_ITEM_IDS['tokens'],
         'amount': tokenData['count'],
         'ext_info': tokenName}
        result.append(convertTokenDict)

    return result


def __convertGoodies(_, rewards):
    result = []
    for goodieID, goodieData in rewards.iteritems():
        convertGoodieDict = {'item_type_id': REWARD_ITEM_IDS['goodies'],
         'amount': goodieData['count'],
         'item_type_cd': goodieID}
        result.append(convertGoodieDict)

    return result


def __convertDossier(_, rewards):
    result = []
    for dossierType, changes in rewards.iteritems():
        for _ in changes.iteritems():
            convertDossierDict = {'item_type_id': REWARD_ITEM_IDS['dossier']}
            result.append(convertDossierDict)

    return result


def __convertItems(_, rewards):
    result = []
    for itemCompDescr, itemCount in rewards.iteritems():
        convertItemDict = {'item_type_id': REWARD_ITEM_IDS['items'],
         'amount': itemCount,
         'item_type_cd': itemCompDescr}
        result.append(convertItemDict)

    return result


def __convertCustomizations(_, rewards):
    result = []
    for customizationData in rewards:
        custType = CustomizationNamesToTypes[customizationData['custType'].upper()]
        cid = customizationData['id']
        convertCustomizationDict = {'item_type_id': REWARD_ITEM_IDS['customizations'],
         'amount': customizationData['value'],
         'item_type_cd': makeIntCompactDescrByID('customizationItem', custType, cid)}
        result.append(convertCustomizationDict)

    return result


def __convertBlueprints(_, rewards):
    result = []
    for fragmentID, count in rewards.iteritems():
        convertBlueprintDict = {'item_type_id': REWARD_ITEM_IDS['blueprints'],
         'amount': count,
         'item_type_cd': fragmentID}
        result.append(convertBlueprintDict)

    return result


def __convertEntitlements(_, rewards):
    result = []
    for entitlementCode, entitlementData in rewards.iteritems():
        convertEntitlementDict = {'value_type_id': REWARD_ITEM_IDS['entitlements'],
         'amount': entitlementData['count'],
         'ext_info': entitlementCode}
        result.append(convertEntitlementDict)

    return result


def __convertCrewSkins(_, rewards):
    result = []
    for crewSkinData in rewards:
        convertCrewSkinDict = {'item_type_id': REWARD_ITEM_IDS['crewSkins'],
         'amount': crewSkinData['count'],
         'item_type_cd': crewSkinData['id']}
        result.append(convertCrewSkinDict)

    return result


def __convertEntitlementList(_, rewards):
    result = []
    for entitlementData in rewards:
        convertEntitlementDict = {'value_type_id': REWARD_ITEM_IDS['entitlements'],
         'amount': entitlementData['count'],
         'ext_info': entitlementData['id']}
        result.append(convertEntitlementDict)

    return result


def __convertCurrencies(_, rewards):
    result = []
    for currencyCode, currencyData in rewards.iteritems():
        convertCurrencyDict = {'value_type_id': REWARD_ITEM_IDS['currencies'],
         'amount': currencyData['count'],
         'ext_info': currencyCode}
        result.append(convertCurrencyDict)

    return result


def __defaultConverter(bonusName, rewards):
    result = []
    if isinstance(rewards, int):
        convertDict = {'value_type_id': REWARD_ITEM_IDS[bonusName],
         'amount': rewards}
        result.append(convertDict)
    return result


def getDefaultConverterProcessor():
    default = {'freeXP': __defaultConverter,
     'credits': __defaultConverter,
     'gold': __defaultConverter,
     'crystal': __defaultConverter,
     'eventCoin': __defaultConverter,
     'bpcoin': __defaultConverter,
     'equipCoin': __defaultConverter,
     'premium_plus': __defaultConverter,
     'slots': __defaultConverter,
     'berths': __defaultConverter,
     'vehicles': __convertVehicles,
     'items': __convertItems,
     'tokens': __convertTokens,
     'goodies': __convertGoodies,
     'dossier': lambda n, v: [],
     'tankmen': lambda n, v: [],
     'customizations': __convertCustomizations,
     'crewSkins': __convertCrewSkins,
     'blueprints': __convertBlueprints,
     'entitlements': __convertEntitlements,
     'entitlementList': __convertEntitlementList,
     'currencies': __convertCurrencies,
     'dogTagComponents': lambda n, v: []}
    default.update(EXTENSIONS_CONVERTER_PROCESSOR)
    return default


def __defaultUnpacker(item):
    return {ID_TO_NAME[item['value_type_id']]: item['amount']}


def __unpackVehicles(item):
    return {'vehicles': [{item['item_type_cd']: {}}]}


def __unpackItems(item):
    return {'items': {item['item_type_cd']: item['amount']}}


def __unpackTokens(item):
    return {'tokens': {item['ext_info']: {'count': item['amount'],
                                   'expires': {'at': VERY_BIG_TIME}}}}


def __unpackGoodies(item):
    return {'goodies': {item['item_type_cd']: {'count': item['amount']}}}


def __unpackCustomizations(item):
    _, ctype, cid = parseIntCompactDescr(item['item_type_cd'])
    return {'customizations': [{'custType': lower(CustomizationTypeNames[ctype]),
                         'id': cid,
                         'value': item['amount'],
                         'isPermanent': True}]}


def __unpackCrewSkins(item):
    return {'crewSkins': [{'count': item['amount'],
                    'id': item['item_type_cd']}]}


def __unpackBlueprints(item):
    return {'blueprints': {item['item_type_cd']: item['amount']}}


def __unpackCurrencies(item):
    return {'currencies': {item['ext_info']: {'count': item['amount']}}}


def __unpackEntitlements(item):
    return {'entitlements': {item['ext_info']: {'count': item['amount']}}}


def getDefaultUnpackProcessor():
    default = {'freeXP': __defaultUnpacker,
     'credits': __defaultUnpacker,
     'gold': __defaultUnpacker,
     'crystal': __defaultUnpacker,
     'eventCoin': __defaultUnpacker,
     'bpcoin': __defaultUnpacker,
     'equipCoin': __defaultUnpacker,
     'premium_plus': __defaultUnpacker,
     'slots': __defaultUnpacker,
     'berths': __defaultUnpacker,
     'vehicles': __unpackVehicles,
     'items': __unpackItems,
     'tokens': __unpackTokens,
     'goodies': __unpackGoodies,
     'dossier': lambda i: {},
     'tankmen': lambda i: {},
     'customizations': __unpackCustomizations,
     'crewSkins': __unpackCrewSkins,
     'blueprints': __unpackBlueprints,
     'entitlements': __unpackEntitlements,
     'entitlementList': lambda i: {},
     'currencies': __unpackCurrencies,
     'dogTagComponents': lambda i: {}}
    default.update(EXTENSIONS_UNPACK_PROCESSOR)
    return default


def packLootboxResultToKafka(appliedResult):
    kafkaLog = []
    converterProcess = getDefaultConverterProcessor()
    for bonusName, bonus in appliedResult.iteritems():
        if bonusName in _PRUNE_MERGERS:
            bonus = _PRUNE_MERGERS[bonusName](bonus)
            if not bonus:
                continue
        if bonusName in converterProcess:
            result = converterProcess[bonusName](bonusName, bonus)
            kafkaLog.extend(result)

    return kafkaLog


def unpackLootboxStatistic(statistic):
    result = {}
    unpackProcessor = getDefaultUnpackProcessor()
    for item in statistic:
        rewardItemID = item.get('value_type_id') or item.get('item_type_id')
        bonusName = ID_TO_NAME[rewardItemID]
        if bonusName in unpackProcessor:
            unpackRes = unpackProcessor[bonusName](item)
            mergeDiffStat(result, unpackRes)

    return result
