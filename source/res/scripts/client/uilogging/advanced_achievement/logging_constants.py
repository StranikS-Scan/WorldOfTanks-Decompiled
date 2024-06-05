# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/advanced_achievement/logging_constants.py
from enum import Enum
FEATURE = 'advanced_achievement'

class AdvancedAchievementActions(Enum):
    CLICK = 'click'
    DISPLAY = 'display'


class AdvancedAchievementViewKey(Enum):
    HANGAR = 'hangar'
    NOTIFICATION_CENTER = 'notification_center'
    PLAYER_COLLECTION = 'player_collection'
    CATALOG = 'catalog'
    REWARD_SCREEN = 'reward_screen'
    EARNING = 'earning_notification_view'


class AdvancedAchievementButtons(Enum):
    TO_ACHIEVEMENT = 'go_to_achievement_button'
    TO_RECEIVED = 'go_to_received_button'
    MORE_REWARDS = 'more_rewards_button'
    GOBLET = 'goblet_button'
    DOG_TAG_PREVIEW = 'dog_tag_preview_button'
    CATALOG = 'catalog_button'


class AdvancedAchievementKeys(Enum):
    SUBCATEGORY = 'subcategory'
    UPCOMING = 'upcoming_achievement'
    EARNING_NOTIFICATION = 'earning_notification'
    ACHIEVEMENT_CARD = 'achievement_card'
    ANOTHER_PLAYER = 'another_player_click'


class AdvancedAchievementSubcategory(Enum):
    VEHICLE = 'vehicle'
    NATIONS = 'nations'
    CUSTOMIZATION = 'customization'
    TROPHY = 'trophy'


class AdvancedAchievementInfoKeys(Enum):
    MULTIPLE = 'multiple'
    SINGLE = 'single'
    PLAYER = 'player'
    ANOTHER_PLAYER = 'another_player'


class AdvancedAchievementStates(Enum):
    IN_PROGRESS = 'in_progress'
    NO_PROGRESS = 'no_progress'
    COMPLETED = 'completed'
