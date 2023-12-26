# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/preview_bottom_panel_constants.py
import logging
from collections import namedtuple
from enum import Enum
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
ObtainingMethodInfo = namedtuple('ObtainingMethodInfo', ('confirmation_key', 'btn_label'))

class _Enum(Enum):

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


class ObtainingMethods(_Enum):
    BUY = 'buy'
    OBTAIN_FOR_COINS = 'obtain_for_coins'
    OBTAIN_FOR_FREE = 'obtain_for_free'


SHOWCASE_STYLE_OBTAINING_METHOD_INFO = {ObtainingMethods.BUY.value: ObtainingMethodInfo('buyConfirmation', R.strings.vehicle_preview.showcaseStyleBuying.actionBtn.label.buy()),
 ObtainingMethods.OBTAIN_FOR_COINS.value: ObtainingMethodInfo('forCoinsObtainConfirmation', R.strings.vehicle_preview.buyingPanel.buyBtn.label.forCoinsObtain()),
 ObtainingMethods.OBTAIN_FOR_FREE.value: ObtainingMethodInfo('freeObtainConfirmation', R.strings.vehicle_preview.buyingPanel.buyBtn.label.freeObtain())}
ITEM_PACK_OBTAINING_METHOD_INFO = {ObtainingMethods.BUY.value: ObtainingMethodInfo('buyConfirmation', R.strings.vehicle_preview.buyingPanel.buyBtn.label.buyItemPack()),
 ObtainingMethods.OBTAIN_FOR_FREE.value: ObtainingMethodInfo('freeObtainConfirmation', R.strings.vehicle_preview.buyingPanel.buyBtn.label.freeObtain())}

def getItemPackObtainingInfo(obtainingMethod=ObtainingMethods.BUY.value):
    return ITEM_PACK_OBTAINING_METHOD_INFO.get(obtainingMethod)


def getShowcaseStyleObtainingInfo(obtainingMethod=ObtainingMethods.BUY.value):
    return SHOWCASE_STYLE_OBTAINING_METHOD_INFO.get(obtainingMethod)
