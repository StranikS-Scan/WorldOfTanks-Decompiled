# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/filters.py
import WWISE
from gui.sounds.sound_constants import SoundFilters

class _SoundFilterAbstract(object):

    def start(self):
        pass

    def stop(self):
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
        _WWISEStateAmbient.__init__(self, 'STATE_hangar_filtered')


def getEmptyFilter():
    return EmptySoundFilter()


def get(filterID):
    return _filters.get(filterID, getEmptyFilter())


def _selectFilter(wwise):
    return wwise if WWISE.enabled else EmptySoundFilter()


_filters = {SoundFilters.FORT_FILTER: _selectFilter(WWISEFortAmbientFilter()),
 SoundFilters.FILTERED_HANGAR: _selectFilter(WWISEFilteredHangarFilter())}
