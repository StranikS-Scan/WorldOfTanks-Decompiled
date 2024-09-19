# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/selectable_reward/constants.py
from enum import Enum
from battle_pass_common import BATTLE_PASS_OFFER_TOKEN_PREFIX
from gui.ranked_battles.constants import YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX
from epic_constants import EPIC_OFFER_TOKEN_PREFIX
from comp7_common import COMP7_OFFER_PREFIX
from event_common import WT_PROGRESSION_TOKEN_PREFIX

class Features(Enum):
    UNDEFINED = 0
    BATTLE_PASS = 1
    RANKED = 2
    EPIC = 3
    COMP7 = 4
    EVENT = 5


FEATURE_TO_PREFIX = {Features.BATTLE_PASS: BATTLE_PASS_OFFER_TOKEN_PREFIX,
 Features.RANKED: YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX,
 Features.EPIC: EPIC_OFFER_TOKEN_PREFIX,
 Features.COMP7: COMP7_OFFER_PREFIX,
 Features.EVENT: WT_PROGRESSION_TOKEN_PREFIX}
SELECTABLE_BONUS_NAME = 'selectableBonus'
