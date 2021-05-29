# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/__init__.py
import datetime
import BigWorld
from constants import ACCOUNT_ATTR
from account_helpers.AccountSettings import AccountSettings, GOLD_FISH_LAST_SHOW_TIME
from shared_utils.account_helpers import BattleResultsCache
from shared_utils.account_helpers import ClientInvitations
from helpers.time_utils import getCurrentTimestamp

def __checkAccountAttr(attrs, attrID):
    return attrs is not None and attrs & attrID != 0


def isMoneyTransfer(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.TRADING)


def isDemonstrator(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.ARENA_CHANGE)


def isDemonstratorExpert(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.BATTLE_TYPE_CHANGE)


def isRoamingEnabled(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.ROAMING)


def isOutOfWallet(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.OUT_OF_SESSION_WALLET)


def isClanEnabled(attrs):
    return __checkAccountAttr(attrs, ACCOUNT_ATTR.CLAN)


def getPremiumExpiryDelta(expiryTime):
    check = datetime.datetime.utcfromtimestamp(expiryTime)
    now = datetime.datetime.utcnow()
    return check - now


def convertGold(gold):
    return gold


def getPlayerID():
    return getattr(BigWorld.player(), 'id', 0)


def getAccountDatabaseID():
    return getattr(BigWorld.player(), 'databaseID', 0)


def isLongDisconnectedFromCenter():
    return getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False)


def getAccountHelpersConfig(manager):
    from account_helpers import settings_core
    manager.addConfig(settings_core.getSettingsCoreConfig)
