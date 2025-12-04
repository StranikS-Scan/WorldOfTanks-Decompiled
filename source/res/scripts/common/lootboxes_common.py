# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/lootboxes_common.py
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from soft_exception import SoftException
from optional_bonuses import BONUS_MERGERS
AVAILABLE_STATISTICS_STORAGE = ('pdata',)

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
            result.append(vehiclesDict)

    return result


def __pruneTokens(rewards):
    result = {}
    for tokenID, data in rewards.iteritems():
        if tokenID.startswith('lb_comp:'):
            continue
        if data.get('count', 0) < 0:
            continue
        result[tokenID] = data

    return result


def __pruneCustomizations(rewards):
    result = []
    for customization in rewards:
        if customization.get('boundToCurrentVehicle', False):
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
