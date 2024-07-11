# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/lootboxes_common.py
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from soft_exception import SoftException

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
