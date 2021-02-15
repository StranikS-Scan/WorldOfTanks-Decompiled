# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/filters.py
import WWISE
from gui.sounds.sound_constants import SoundFilters
from shared_utils import CONST_CONTAINER

class StatesGroup(CONST_CONTAINER):
    HANGAR_FILTERED = 'STATE_hangar_filtered'
    BOOTCAMP_ARENA_FILTERED = 'STATE_bootcamp_arena_filtered'
    HANGAR_PLACE_BATTLE_PASS = 'STATE_hangar_place_battle_pass'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'
    VIDEO_OVERLAY = 'STATE_video_overlay'


_ON_PATTERN = '{}_on'
_OFF_PATTERN = '{}_off'

class States(CONST_CONTAINER):
    OVERLAY_HANGAR_GENERAL_ON = _ON_PATTERN.format(StatesGroup.OVERLAY_HANGAR_GENERAL)
    OVERLAY_HANGAR_GENERAL_OFF = _OFF_PATTERN.format(StatesGroup.OVERLAY_HANGAR_GENERAL)
    HANGAR_FILTERED_ON = _ON_PATTERN.format(StatesGroup.HANGAR_FILTERED)
    HANGAR_FILTERED_OFF = _OFF_PATTERN.format(StatesGroup.HANGAR_FILTERED)
    VIDEO_OVERLAY_ON = _ON_PATTERN.format(StatesGroup.VIDEO_OVERLAY)
    VIDEO_OVERLAY_OFF = _OFF_PATTERN.format(StatesGroup.VIDEO_OVERLAY)


def switchHangarFilteredFilter(on=True):
    _setState(StatesGroup.HANGAR_FILTERED, States.HANGAR_FILTERED_ON if on else States.HANGAR_FILTERED_OFF)


def switchHangarOverlaySoundFilter(on=True):
    _switchOverlaySoundFilter(StatesGroup.OVERLAY_HANGAR_GENERAL, States.OVERLAY_HANGAR_GENERAL_ON, States.OVERLAY_HANGAR_GENERAL_OFF, on)


def switchVideoOverlaySoundFilter(on=True):
    _switchOverlaySoundFilter(StatesGroup.VIDEO_OVERLAY, States.VIDEO_OVERLAY_ON, States.VIDEO_OVERLAY_OFF, on)


class _StateKeeper(object):
    __stateHoldersCounts = {}

    @classmethod
    def checkinHolder(cls, stateName):
        prevCount = cls.__stateHoldersCounts.get(stateName, 0)
        cls.__stateHoldersCounts[stateName] = prevCount + 1
        return prevCount

    @classmethod
    def checkoutHolder(cls, stateName):
        count = cls.__stateHoldersCounts.get(stateName, 0)
        if count > 0:
            count -= 1
        cls.__stateHoldersCounts[stateName] = count
        return count


class _SoundFilterAbstract(object):

    def start(self):
        pass

    def stop(self):
        pass

    def stopView(self, view):
        pass


class EmptySoundFilter(_SoundFilterAbstract):

    def __repr__(self):
        pass


class _WWISEStateAmbient(_SoundFilterAbstract):

    def __init__(self, stateID):
        self._stateID = stateID

    def start(self):
        _setState(self._stateID, self._getStartState())

    def stop(self):
        _setState(self._stateID, self._getStopState())

    def _getStartState(self):
        return '%s_on' % self._stateID

    def _getStopState(self):
        return '%s_off' % self._stateID

    def __repr__(self):
        return 'WWISE(%s)' % self._stateID


class WWISEFilteredHangarFilter(_WWISEStateAmbient):

    def __init__(self):
        _WWISEStateAmbient.__init__(self, StatesGroup.HANGAR_FILTERED)

    def stopView(self, view):
        view.soundManager.clear(stopPersistent=True)


class WWISEFilteredBootcampArenaFilter(_WWISEStateAmbient):

    def __init__(self):
        _WWISEStateAmbient.__init__(self, StatesGroup.BOOTCAMP_ARENA_FILTERED)


class WWISEBattlePassFilter(_WWISEStateAmbient):

    def __init__(self):
        super(WWISEBattlePassFilter, self).__init__(StatesGroup.HANGAR_PLACE_BATTLE_PASS)


def getEmptyFilter():
    return EmptySoundFilter()


def get(filterID):
    return _filters[filterID] if filterID in _filters else EmptySoundFilter()


def _selectFilter(wwise):
    return wwise if WWISE.enabled else EmptySoundFilter()


_filters = {SoundFilters.FILTERED_HANGAR: _selectFilter(WWISEFilteredHangarFilter()),
 SoundFilters.BATTLE_PASS_FILTER: _selectFilter(WWISEBattlePassFilter())}

def _setState(stateGroup, stateName):
    WWISE.WW_setState(stateGroup, stateName)


def _switchOverlaySoundFilter(group, stateOn, stateOff, on=True):
    if on:
        prevHolders = _StateKeeper.checkinHolder(group)
        if not prevHolders:
            _setState(group, stateOn)
    else:
        currHolders = _StateKeeper.checkoutHolder(group)
        if not currHolders:
            _setState(group, stateOff)
