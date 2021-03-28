# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/deprecated/bootcamp/validators.py
import operator
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, CHECK, LIMITS
__all__ = ('TimeValidator',)

class TimeValidator(object):
    limits = {BC_LOG_KEYS.BC_INTRO_VIDEO: [(CHECK.EQUAL, LIMITS.INVALID_MIN_LENGTH), (CHECK.GREATER_THAN, LIMITS.INTRO_VIDEO_MAX_LENGTH)],
     BC_LOG_KEYS.BC_OUTRO_VIDEO: [(CHECK.EQUAL, LIMITS.INVALID_MIN_LENGTH), (CHECK.GREATER_THAN, LIMITS.OUTRO_VIDEO_MAX_LENGTH)],
     BC_LOG_KEYS.BC_INTERLUDE_VIDEO: [(CHECK.EQUAL, LIMITS.INVALID_MIN_LENGTH), (CHECK.GREATER_THAN, LIMITS.INTERLUDE_VIDEO_MAX_LENGTH)],
     BC_LOG_KEYS.BC_HANGAR_MENU: [(CHECK.EQUAL, LIMITS.INVALID_MIN_LENGTH)]}

    @classmethod
    def isValid(cls, logKey, logValue, validate=True):
        if not validate:
            return True
        try:
            limitsForKey = cls.limits[logKey]
        except KeyError:
            return True

        for operatorName, limit in limitsForKey:
            if getattr(operator, operatorName)(logValue, limit):
                return False

        return True
