# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/settings_constants.py
from enum import Enum
RS_PDATA_KEY = 'renewableSub'
RS_EXPIRATION_TIME = 'expiry'
RS_BADGES = 'badges'
RS_TIER = 'tier'
PRO_BOOST_PDATA_KEY = 'wotPlusProBoost'
IDLE_CREW_XP_PDATA_KEY = 'idleCrewXP'
RS_SR_BACKGROUND = 'serviceRecordBackground'
RS_SR_RIBBON = 'serviceRecordRibbon'
IDLE_CREW_VEH_INV_ID = 'vehInvID'
LAST_XP_UPDATE_TIMESTAMP = 'lastXPUpdate'
PASSIVE_XP_CURRENCY = 'currency'
ISSUED_XP_CACHE = 'xpCache'
PRO_BOOSTED_VEHICLE = 'vehInvID'
PRO_BOOST_ACTIVATION_TIME = 'activationTime'
CLEAR_PRO_BOOST_VEHICLE_ID = None
PASSIVE_XP_ENTITLEMENT = 'subscription_passive_xp'
PASSIVE_XP_SECONDS = 'passive_xp_seconds'
WOTP_REQUESTER_NAME = 'wotPlus'
SUBSCRIPTION_DURATION_LENGTH = 2592000
PRO_THRESHOLD_DAYS = 270
DEFAULT_DEMOUNT_ACTION = 0
WOT_PLUS_DEMOUNT_ACTION = 1

class WotPlusState(Enum):
    INACTIVE = 0
    ACTIVE = 1
    CANCELLED = 2


class OptionalDevicesUsageConst(object):
    REMOVE = 'remove'
    UPDATE = 'update'
    COPY = 'copy'


class WotPlusTier(object):
    NONE = 0
    CORE = 1
    PRO = 2
    ALL = (CORE, PRO)
