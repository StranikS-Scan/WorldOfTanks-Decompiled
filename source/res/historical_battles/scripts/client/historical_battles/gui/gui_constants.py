# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/gui_constants.py
from constants_utils import ConstInjector
from messenger import m_constants
SM_TYPE_HB_PROGRESSION = 'HBProgressionNotification'
HB_DISCOUNT_ENTITLEMENT_PREFIX = 'historical_battles_'

class SCH_CLIENT_MSG_TYPE(m_constants.SCH_CLIENT_MSG_TYPE, ConstInjector):
    HB_ARENA_BAN_NOTIFICATIONS = 460
    HB_ARENA_WARNING_NOTIFICATIONS = 461
    HB_PROGRESSION_NOTIFICATIONS = 451
    HB_STARTED_NOTIFICATION = 462
