# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodie_constants.py
MAX_ACTIVE_GOODIES = 3

class GOODIE_STATE:
    INACTIVE = 0
    ACTIVE = 1
    USED = 2


class GOODIE_VARIETY:
    DISCOUNT = 0
    BOOSTER = 1


class GOODIE_TARGET_TYPE:
    ON_BUY_PREMIUM = 1
    ON_BUY_SLOT = 2
    ON_POST_BATTLE = 3
    ON_BUY_GOLD_TANKMEN = 4
    ON_FREE_XP_CONVERSION = 5
    ON_BUY_VEHICLE = 6


class GOODIE_CONDITION_TYPE:
    MAX_VEHICLE_LEVEL = 1


class GOODIE_RESOURCE_TYPE:
    GOLD = 10
    CREDITS = 20
    XP = 30
    CREW_XP = 40
    FREE_XP = 50


class GOODIE_NOTIFICATION_TYPE:
    EMPTY = 1
    REMOVED = 3
    DISABLED = 4
