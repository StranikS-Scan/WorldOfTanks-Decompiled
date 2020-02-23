# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/filters.py
import WWISE
from gui.sounds.sound_constants import SoundFilters
from shared_utils import CONST_CONTAINER

class StatesGroup(CONST_CONTAINER):
    HANGAR_FILTERED = 'STATE_hangar_filtered'
    BOOTCAMP_ARENA_FILTERED = 'STATE_bootcamp_arena_filtered'
    HANGAR_PLACE_BATTLE_PASS = 'STATE_hanger_place_battle_pass'
    OVERLAY_HANGAR_GENERAL = 'STATE_overlay_hangar_general'


class States(CONST_CONTAINER):
    OVERLAY_HANGAR_GENERAL_ON = 'STATE_overlay_hangar_general_on'
    OVERLAY_HANGAR_GENERAL_OFF = 'STATE_overlay_hangar_general_off'


def switchHangarOverlaySoundFilter(on=True):
    if on:
        prevHolders = _StateKeeper.checkinHolder(StatesGroup.OVERLAY_HANGAR_GENERAL)
        if not prevHolders:
            _setState(StatesGroup.OVERLAY_HANGAR_GENERAL, States.OVERLAY_HANGAR_GENERAL_ON)
    else:
        currHolders = _StateKeeper.checkoutHolder(StatesGroup.OVERLAY_HANGAR_GENERAL)
        if not currHolders:
            _setState(StatesGroup.OVERLAY_HANGAR_GENERAL, States.OVERLAY_HANGAR_GENERAL_OFF)


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


class _FortAmbientFilter(object):

    def getBuildNumberField(self):
        raise NotImplementedError

    def getTransportModeField(self):
        raise NotImplementedError

    def getDefencePeriodField(self):
        raise NotImplementedError


class WWISEFortAmbientFilter(_FortAmbientFilter, _WWISEStateAmbient):

    def __init__(self):
        _FortAmbientFilter.__init__(self)
        _WWISEStateAmbient.__init__(self, 'STATE_fortified_area')

    def getBuildNumberField(self):
        pass

    def getTransportModeField(self):
        pass

    def getDefencePeriodField(self):
        pass

    def __repr__(self):
        pass


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


_filters = {SoundFilters.FORT_FILTER: _selectFilter(WWISEFortAmbientFilter()),
 SoundFilters.FILTERED_HANGAR: _selectFilter(WWISEFilteredHangarFilter()),
 SoundFilters.BATTLE_PASS_FILTER: _selectFilter(WWISEBattlePassFilter())}

def _setState(stateGroup, stateName):
    WWISE.WW_setState(stateGroup, stateName)
