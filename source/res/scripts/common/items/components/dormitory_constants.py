# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/dormitory_constants.py
from enum import IntEnum

class DormitorySections(object):
    INITIAL = 'initial'
    NUMBER_ROOMS = 'number_rooms'
    PRICE_GROUP = 'price_group'
    ENABLED = 'enabled'
    CURRENCY = 'currency'
    PRICE = 'price'


class BuyDormitoryReason(IntEnum):
    GENERAL_BUY = 0
    RECRUIT_NEW_DETACHMENT = 1
    RECOVER_DETACHMENT = 2
