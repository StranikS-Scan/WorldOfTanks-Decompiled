# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_spam_ctrl/spam_constants.py
from enum import IntEnum
DEFAULT_COOLDOWN = 1.0

class SpamEvents(IntEnum):
    FULLSCREEN_EFFECT = 1
    MARKERS_HIT_STATE = 2
    TEAM_HEALTH_BAR_UPDATE = 3
    SHOT_RESULT_SOUND = 4


SPAM_COOLDOWNS = {SpamEvents.FULLSCREEN_EFFECT: 2.0,
 SpamEvents.MARKERS_HIT_STATE: 2.0,
 SpamEvents.TEAM_HEALTH_BAR_UPDATE: 1.0,
 SpamEvents.SHOT_RESULT_SOUND: 1.5}
