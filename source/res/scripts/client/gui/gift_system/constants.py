# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/constants.py
import typing
from enum import unique, Enum, IntEnum
DEV_STAMP_CODE = 'giftSystem_1_devStamp'
NY_STAMP_CODE = 'giftSystem_2_nyStamp'
GIFTS_STORAGE_KEY = 'giftsStorage'
RANDOM_RECEIVER_ID = -1

@unique
class GifterResponseState(Enum):
    WEB_FAILURE = 'webFailure'
    WEB_SUCCESS = 'webSuccess'
    WEB_ACCOUNT_FAILURE = 'webAccountFailure'
    REQUESTS_DISABLED = 'requestsDisabled'
    WGCG_NOT_AVAILABLE = 'wgcgNotAvailable'
    REQUEST_IN_PROGRESS = 'requestInProgress'
    CENTER_DISCONNECTED = 'centerDisconnected'


class AccountErrorResponseTitle(Enum):
    BANNED = 'AccountBannedException'
    NOT_FRIEND = 'NotFriendException'

    @staticmethod
    def getAllValues():
        items = AccountErrorResponseTitle.__members__.values()
        return [ x.value for x in items ]


@unique
class GiftMessageType(IntEnum):
    INCOME = 0
    OUTCOME = 1
    HISTORY = 2
    LIMITS = 4


@unique
class HubUpdateReason(IntEnum):
    HISTORY = 0
    SETTINGS = 1
    WEB_STATE = 2
    INCOME_GIFT = 3
    OUTCOME_GIFT = 4
    KEEPER_CLEAR = 5
    STAMPER_UPDATE = 6
