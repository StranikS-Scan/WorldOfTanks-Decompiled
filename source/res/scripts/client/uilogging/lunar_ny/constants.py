# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/lunar_ny/constants.py
import typing
from enum import Enum
from lunar_ny.lunar_ny_constants import EnvelopeTypes
FEATURE = 'lunar_ny22'

class LogGroups(Enum):
    MAIN_WIDGET = 'main_widget'
    SELECTABLE_OBJECT_3D = '3d_selectable_object'
    POPOVER_BUY_BUTTON = 'popover_buy_button'
    POPOVER_SEND_BUTTON = 'popover_send_button'
    BUY_BUTTON = 'buy_button'
    BUY_ADDITIONAL_BUTTON = 'buy_additional_button'
    SIDE_BAR_TAB = 'side_bar_tab'
    OPEN_COMMON_BUTTON = 'open_common_button'
    HISTORY_BUTTON = 'history_button'
    OPEN_ENVELOPE_BUTTON = 'open_envelope_button'
    SEND_BUTTON = 'send_button'


class LogActions(Enum):
    CLICK = 'click'


class ParentSreen(Enum):
    HANGAR = 'hangar'
    SEND_ENVELOPES_VIEW = 'send_envelopes_view'
    LUNAR_NY_LOBBY = 'lunar_ny_lobby'
    STORAGE_VIEW = 'storage_view'


class AdditionalInfo(Enum):
    FREE = 'free'
    PAID = 'paid'
    PREMIUM_PAID = 'premium_paid'
    STORAGE_VIEW = 'storage_view'
    ALL = 'all'
    LACK_OF_ENVELOPES = 'lack_of_envelopes'
    POP_UP_NOTIFICATION = 'pop_up_notification'
    NOTIFICATION_CENTER = 'notification_center'
    OPEN_1 = 'open_1'
    OPEN_5 = 'open_5'
    OPEN_20 = 'open_20'
    OPEN_REMAINDER = 'open_remainder'


ENVELOPE_ADDITIONAL_INFO_BY_TYPE = {EnvelopeTypes.FREE: AdditionalInfo.FREE,
 EnvelopeTypes.PAID: AdditionalInfo.PAID,
 EnvelopeTypes.PREMIUM_PAID: AdditionalInfo.PREMIUM_PAID}
OPEN_INFO_BY_COUNT = {1: AdditionalInfo.OPEN_1,
 5: AdditionalInfo.OPEN_5,
 20: AdditionalInfo.OPEN_20}

def getAdditionalInfoByEnvelopeType(envelopeType):
    return ENVELOPE_ADDITIONAL_INFO_BY_TYPE.get(envelopeType)
