# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/destroy_times_mapping.py
import SoundGroups
from constants import VEHICLE_MISC_STATUS, DEATH_ZONES
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BATTLE_DESTROY_TIMER_STATES import BATTLE_DESTROY_TIMER_STATES
_TIMER_STATES = BATTLE_DESTROY_TIMER_STATES

def getDefaultMiscStatuses():
    return {VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING: _TIMER_STATES.DROWN,
     VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED: _TIMER_STATES.OVERTURNED}


def getDefaultDeathZonesCodes():
    return {DEATH_ZONES.STATIC: _TIMER_STATES.DEATH_ZONE}


def getTimerViewTypeID(level):
    if level == 'critical':
        typeID = _TIMER_STATES.CRITICAL_VIEW
    elif level == 'warning':
        typeID = _TIMER_STATES.WARNING_VIEW
    else:
        LOG_ERROR('Type of view is not found by level', level)
        typeID = _TIMER_STATES.WARNING_VIEW
    return typeID


class FrontendMapping(object):
    __slots__ = ('__miscStatuses', '__deathZonesCodes', '__deathZonesSounds')

    def __init__(self, miscStatuses=None, deathZonesCodes=None, deathZonesSoundIDs=None):
        super(FrontendMapping, self).__init__()
        self.__miscStatuses = miscStatuses or getDefaultMiscStatuses()
        self.__deathZonesCodes = deathZonesCodes or getDefaultDeathZonesCodes()
        self.__deathZonesSounds = self.__loadDeathZoneSounds(deathZonesSoundIDs or {})

    def clear(self):
        self.__miscStatuses.clear()
        self.__deathZonesCodes.clear()
        self.__deathZonesSounds.clear()

    def getTimerTypeIDByMiscCode(self, code):
        if code in self.__miscStatuses:
            return self.__miscStatuses[code]
        else:
            LOG_ERROR('Destroy timer is not found by code', code)
            return None
            return None

    def getTimerTypeIDByDeathZoneCode(self, code):
        if code in self.__deathZonesCodes:
            return self.__deathZonesCodes[code]
        else:
            LOG_ERROR('Death zone timer is not found by code', code)
            return None
            return None

    def getDestroyTimersTypesIDs(self):
        return self.__miscStatuses.values()

    def getDeathZoneTimersTypesIDs(self):
        return self.__deathZonesCodes.values()

    def getSoundByDeathZone(self, code, level):
        sound = None
        key = (code, level)
        if key in self.__deathZonesSounds:
            sound = self.__deathZonesSounds[code]
        return sound

    @staticmethod
    def __loadDeathZoneSounds(soundsIDs):
        sounds = {}
        assert isinstance(soundsIDs, dict), 'Value of soundsIDs must be dict'
        for key, soundID in soundsIDs.iteritems():
            assert len(key) == 2, 'Key is invalid'
            assert isinstance(soundID, str), 'Value is invalid'
            sounds[key] = SoundGroups.g_instance.getSound2D(soundID)

        return sounds
