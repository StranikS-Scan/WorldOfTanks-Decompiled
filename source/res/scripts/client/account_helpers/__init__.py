# Embedded file name: scripts/client/account_helpers/__init__.py
import datetime
import BigWorld
from account_helpers.AccountSettings import AccountSettings, GOLD_FISH_LAST_SHOW_TIME
import constants
from shared_utils.account_helpers import BattleResultsCache, ClientClubs
from shared_utils.account_helpers import ClientInvitations
from gui import GUI_SETTINGS
from helpers.time_utils import getCurrentTimestamp

def __checkAccountAttr(attrs, attrID):
    return attrs is not None and attrs & attrID != 0


def isPremiumAccount(attrs):
    return __checkAccountAttr(attrs, constants.ACCOUNT_ATTR.PREMIUM)


def isMoneyTransfer(attrs):
    return __checkAccountAttr(attrs, constants.ACCOUNT_ATTR.TRADING)


def isDemonstrator(attrs):
    return __checkAccountAttr(attrs, constants.ACCOUNT_ATTR.ARENA_CHANGE)


def isRoamingEnabled(attrs):
    return __checkAccountAttr(attrs, constants.ACCOUNT_ATTR.ROAMING)


def getPremiumExpiryDelta(expiryTime):
    check = datetime.datetime.utcfromtimestamp(expiryTime)
    now = datetime.datetime.utcnow()
    return check - now


def convertGold(gold):
    return gold


def getPlayerID():
    return getattr(BigWorld.player(), 'id', 0L)


def getAccountDatabaseID():
    return getattr(BigWorld.player(), 'databaseID', 0L)
