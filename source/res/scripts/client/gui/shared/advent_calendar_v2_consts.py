# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/advent_calendar_v2_consts.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_reward_item_view_model import RewardType
ADVENT_CALENDAR_PREFIX = 'advent'
ADVENT_CALENDAR_OPEN_DOOR_TOKEN_PREFIX = ADVENT_CALENDAR_PREFIX + ':open'
ADVENT_CALENDAR_QUEST_POSTFIX = ':open'
ADVENT_CALENDAR_TOKEN = ADVENT_CALENDAR_PREFIX + ':points'
ADVENT_CALENDAR_QUEST_PREFIX = ADVENT_CALENDAR_PREFIX + ':day:'
ADVENT_CALENDAR_QUEST_RE_PATTERN = ADVENT_CALENDAR_QUEST_PREFIX + '\\d+' + ADVENT_CALENDAR_QUEST_POSTFIX
ADVENT_CALENDAR_DAY_TOKEN_PREFIX = ADVENT_CALENDAR_PREFIX + ':day:'
ADVENT_CALENDAR_PROGRESSION_QUEST = ADVENT_CALENDAR_PREFIX + ':progression:'
ADVENT_CALENDAR_PROGRESSION_QUEST_PREFIX = ADVENT_CALENDAR_PROGRESSION_QUEST + '{id}'
PROGRESSION_REWARD_TYPE_TO_ICON = {RewardType.GIFT_MACHINE_TOKEN.value: 'nyCoin',
 RewardType.CREW_MEMBER.value: 'tankwoman',
 RewardType.BIG_LOOTBOX.value: 'lootBox'}
MIN_AVAILABLE_DOORS_REQUIRED_FOR_NOTIFICATION = 2
GUARANTEED_REWARD_GROUP_NAME = 'guaranteed'
LOOTBOX_TOKEN_PREFIX = 'lootBox:'

class GraphicsPresetSystemSettings(Enum):
    ULTRA = 0
    MAX = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MIN = 5


ADVENT_PRESETS_WITH_DISABLED_ANIMATION = (GraphicsPresetSystemSettings.MIN.value, GraphicsPresetSystemSettings.LOW.value)
