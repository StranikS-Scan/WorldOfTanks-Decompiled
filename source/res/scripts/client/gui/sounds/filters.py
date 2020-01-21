# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/filters.py
import WWISE
from gui.sounds.sound_constants import SoundFilters
STATE_HANGAR_FILTERED = 'STATE_hangar_filtered'
STATE_BOOTCAMP_ARENA_FILTERED = 'STATE_bootcamp_arena_filtered'

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
        WWISE.WW_setState(self._stateID, '%s_on' % self._stateID)

    def stop(self):
        WWISE.WW_setState(self._stateID, '%s_off' % self._stateID)

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
        _WWISEStateAmbient.__init__(self, STATE_HANGAR_FILTERED)

    def stopView(self, view):
        view.soundManager.clear(stopPersistent=True)


class WWISEFilteredBootcampArenaFilter(_WWISEStateAmbient):

    def __init__(self):
        _WWISEStateAmbient.__init__(self, STATE_BOOTCAMP_ARENA_FILTERED)


def getEmptyFilter():
    return EmptySoundFilter()


def get(filterID):
    return _filters[filterID] if filterID in _filters else EmptySoundFilter()


def _selectFilter(wwise):
    return wwise if WWISE.enabled else EmptySoundFilter()


_filters = {SoundFilters.FORT_FILTER: _selectFilter(WWISEFortAmbientFilter()),
 SoundFilters.FILTERED_HANGAR: _selectFilter(WWISEFilteredHangarFilter())}
