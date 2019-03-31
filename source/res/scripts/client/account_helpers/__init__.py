# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/__init__.py
# Compiled at: 2011-06-30 15:19:45
import BigWorld
import constants
import datetime

def isPremiumAccount(attrs):
    return attrs is not None and attrs & constants.ACCOUNT_ATTR.PREMIUM != 0


def getPremiumExpiryDelta(expiryTime):
    check = datetime.datetime.utcfromtimestamp(expiryTime)
    now = datetime.datetime.utcnow()
    return check - now


def isDemonstrator(attrs):
    return attrs is not None and attrs & constants.ACCOUNT_ATTR.ARENA_CHANGE != 0


def convertGold(gold):
    return gold
