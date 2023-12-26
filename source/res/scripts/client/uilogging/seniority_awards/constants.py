# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/seniority_awards/constants.py
from enum import Enum

class SeniorityAwardsFeatures(str, Enum):
    FEATURE = 'seniority_awards'
    VEHICLE_SELECTION_FEATURE = 'seniority_awards_vehicle_selection'


class SeniorityAwardsLogKeys(str, Enum):
    COINS_NOTIFICATION = 'coins_notification'
    REWARD_NOTIFICATION = 'reward_notification'
    VEHICLE_SELECTION_NOTIFICATION = 'vehicle_selection_notification'
    MULTIPLE_TOKENS_NOTIFICATION_ERROR = 'multiple_tokens_notification_error'
    TIMEOUT_NOTIFICATION_ERROR = 'timeout_notification_error'


class SeniorityAwardsLogSpaces(str, Enum):
    HANGAR = 'hangar'
    NOTIFICATION_CENTER = 'notification_center'


class SeniorityAwardsLogButtons(str, Enum):
    SHOP_BUTTON = 'shop_button'
    CLAIM_BUTTON = 'claim_button'
    SELECT_BUTTON = 'select_button'


class SeniorityAwardsLogActions(str, Enum):
    CLICK = 'click'
    DISPLAYED = 'displayed'
