# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/hb_constants.py
from enum import Enum, IntEnum
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderType
MultiplierToOrderType = {1: OrderType.SMALL,
 2: OrderType.SMALL,
 3: OrderType.MEDIUM,
 5: OrderType.BIG}
ORDER_TOKEN_NAME_TO_ORDER_TYPE = {'hb_front_coupon_x2': OrderType.SMALL,
 'hb_front_coupon_x3': OrderType.MEDIUM,
 'hb_front_coupon_x5': OrderType.BIG}

class InfoViewKeys(Enum):
    ORDER_INFO_X10_VIEW = 'OrderInfoX10View'


class FrontsOpenStates(IntEnum):
    EVENT_STARTED = 1
    EVENT_ENDED = 2
