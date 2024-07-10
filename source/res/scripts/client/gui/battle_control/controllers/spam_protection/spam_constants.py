# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/spam_protection/spam_constants.py
from enum import IntEnum
DEFAULT_COOLDOWN = 1.0

class SpamEvents(IntEnum):
    FULLSCREEN_EFFECT = 1
    ALLY_HIT_MESSAGE = 2
    MARKERS_HIT_STATE = 3
    AUTO_SHOOT_TRACER_SOUND = 4


SPAM_COOLDOWNS = {SpamEvents.FULLSCREEN_EFFECT: 1.0,
 SpamEvents.ALLY_HIT_MESSAGE: 3.0,
 SpamEvents.MARKERS_HIT_STATE: 1.0,
 SpamEvents.AUTO_SHOOT_TRACER_SOUND: 0.25}
