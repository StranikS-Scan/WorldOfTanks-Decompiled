# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/hw_constants.py
from enum import IntEnum
from halloween_common.halloween_constants import HALLOWEEN_EVENT_PREFIX
HALLOWEEN_GROUP_PHASES_PREFIX = HALLOWEEN_EVENT_PREFIX + '_phases_halloween'
HALLOWEEN_GROUP_POST_PHASES_PREFIX = HALLOWEEN_EVENT_PREFIX + '_post_phases_halloween'
HALLOWEEN_GROUP_PHASES_SUFFIX = 'phase_{index}'
HALLOWEEN_BATTLE_QUEST_SUFFIX = 'hquest'
RANDOM_BATTLE_QUEST_SUFFIX = 'rquest'
HALLOWEEN_QUEST_PASSED_TOKEN_TPL = '^' + HALLOWEEN_EVENT_PREFIX + '_phase_[1-9]+:tankman_passed$'
HALLOWEEN_QUEST_TANKMAN_PASSED_TOKEN = HALLOWEEN_EVENT_PREFIX + '_phase_{index}:tankman_passed'
EVENT_ABILITY_QUEST_PREFIX = 'hquest_2'
GLOBAL_PROGRESS_TANKMAN_QUEST = HALLOWEEN_EVENT_PREFIX + '_global_progress:all_tankmen'
GLOBAL_PROGRESS_HW_XP_QUEST = HALLOWEEN_EVENT_PREFIX + '_global_progress:hw_xp'
INVALID_PHASE_INDEX = 0
FIRST_PHASE_INDEX = 1

class QuestType(IntEnum):
    NONE = 0
    HALLOWEEN = 1
    RANDOM = 2


QUEST_SUFFIX_TO_TYPE = {HALLOWEEN_BATTLE_QUEST_SUFFIX: QuestType.HALLOWEEN,
 RANDOM_BATTLE_QUEST_SUFFIX: QuestType.RANDOM}
PHASE_PATTERN = '^' + HALLOWEEN_EVENT_PREFIX + '_phase_([0-9]+):hquest_([0-9]+)$'

class PhaseType(object):
    NONE = 0
    REGULAR = 1
    POST = 2
    ALL = REGULAR | POST


GROUP_PREFIX_TO_PHASE_TYPE = {HALLOWEEN_GROUP_PHASES_PREFIX: PhaseType.REGULAR,
 HALLOWEEN_GROUP_POST_PHASES_PREFIX: PhaseType.POST}

class PhaseState(IntEnum):
    OUT_OF_DATE = 0
    ACTIVE = 1
    LOCK = 2


class AccountSettingsKeys(object):
    EVENT_KEY = 'hw_keys'
    META_INTRO_VIEW_SHOWED = 'metaIntroView'
    PREVIOUS_PHASE = 'previous_phase'
    VIEWED_WITHES_INTRO = 'viewed_withes_intro'
    VIEWED_WITHES_OUTRO = 'viewed_withes_outro'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.META_INTRO_VIEW_SHOWED: False,
                                 AccountSettingsKeys.PREVIOUS_PHASE: 0,
                                 AccountSettingsKeys.VIEWED_WITHES_INTRO: [],
                                 AccountSettingsKeys.VIEWED_WITHES_OUTRO: []}}

class HWBonusesType(object):
    TANKMAN = 'tankman'
    STYLE = 'style'
    DECAL = 'projection_decal'
    BADGE = 'playerBadges'
    MEDAL = 'singleAchievements'
    CRYSTAL = 'crystal'
    CREDITS = 'credits'
    EQUIPMENT = 'equipment'
    BATTLE_BOOSTER = 'battleBooster'
    LOOT_BOXES = 'lootBoxes'
    ORDERED_LIST = (TANKMAN,
     STYLE,
     DECAL,
     BADGE,
     MEDAL,
     CRYSTAL,
     CREDITS,
     EQUIPMENT,
     BATTLE_BOOSTER)
    EQUIPMENT_LIST = ('autoExtinguishers', 'largeRepairkit', 'largeMedkit', 'rammerBattleBooster', 'improvedVentilationBattleBooster', 'fireFightingBattleBooster', 'improvedSightsBattleBooster', 'additInvisibilityDeviceBattleBooster')


ORDERED_EQUIPMENT_LIST = ('hpRepairAndCrewHeal', 'hwVehicleFireArrow', 'damageShield', 'halloweenNitro', 'hwVehicleCurseArrow', 'hwVehicleFrozenArrow', 'hwVehicleHealingArrow')

class HWTooltips(object):
    HW_BADGE = 'HWTooltips_HW_BADGE'
    HW_LOBBY_SET = [HW_BADGE]
