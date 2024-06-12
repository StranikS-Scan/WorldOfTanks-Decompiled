# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/renewable_subscription_common/rent.py
from enum import Enum

class RentEventTypes(Enum):
    START_RENT = 1
    END_RENT = 2


class RentLogInfo(Enum):
    ADD = 'excl_veh:add'
    START = 'excl_veh:on'
    END = 'excl_veh:off'


TEAM_SUBS_BONUS = 'subscription:team_bonus'
