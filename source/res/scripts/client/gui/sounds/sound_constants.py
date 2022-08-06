# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/sound_constants.py
from shared_utils import CONST_CONTAINER

class EnabledStatus(object):
    ENABLED_DEFAULT = 0
    ENABLED_BY_USER = 1
    DISABLED = 2

    @classmethod
    def isEnabled(cls, status):
        return status in (cls.ENABLED_DEFAULT, cls.ENABLED_BY_USER)


PLAYING_SOUND_CHECK_PERIOD = 1.0
IS_ADVANCED_LOGGING = False

class SoundSystems(CONST_CONTAINER):
    UNKNOWN = 0
    WWISE = 1

    @classmethod
    def getUserName(cls, sysID):
        return cls.getKeyByValue(sysID) or cls.UNKNOWN


class SoundFilters(CONST_CONTAINER):
    EMPTY = 1
    FILTERED_HANGAR = 2
    FORT_FILTER = 3
    BATTLE_PASS_FILTER = 4
    HANGAR_OVERLAY = 5
    MARATHON_FILTER = 6
    HANGAR_PLACE_TASKS_DAILY = 7
    HANGAR_PLACE_TASKS_MISSIONS = 8
    HANGAR_PLACE_TASKS_BATTLE_PASS = 9
    HANGAR_PLACE_TASKS_EVENTS = 10
    HANGAR_PLACE_TASKS_BATTLE_MATTERS = 11


class SPEAKERS_CONFIG(object):
    AUTO_DETECTION = 0
    SPEAKER_SETUP_2_0 = 2
    SPEAKER_SETUP_5_1 = 5
    SPEAKER_SETUP_7_1 = 7
    RANGE = (AUTO_DETECTION,
     SPEAKER_SETUP_2_0,
     SPEAKER_SETUP_5_1,
     SPEAKER_SETUP_7_1)
