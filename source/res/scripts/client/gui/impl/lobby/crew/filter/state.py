# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/state.py
from collections import defaultdict, Iterable
from Event import Event
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType

class FilterState(object):
    GROUPS = ToggleGroupType

    def __init__(self, initialState=None):
        self.onStateChanged = Event()
        self._state = defaultdict(set)
        self.__searchString = u''
        self._initialState = initialState or {}
        self.reinit()

    def __contains__(self, item):
        return item in self._state

    def __getitem__(self, item):
        return self._state[item]

    def __iter__(self):
        return iter(self._state)

    @property
    def searchString(self):
        return self.__searchString

    @searchString.setter
    def searchString(self, value):
        self.__searchString = unicode(value)
        self.onStateChanged()

    @property
    def state(self):
        return self._state

    def clear(self):
        self.__clear()
        self.onStateChanged()

    def update(self, groupID, fieldID):
        if fieldID in self._state[groupID]:
            self._state[groupID].remove(fieldID)
        else:
            self._state[groupID].add(fieldID)
        self.onStateChanged()

    def reinit(self, state=None):
        self.__clear()
        self._reinitState(initialState=state)
        self.onStateChanged()

    def _reinitState(self, initialState=None):
        if initialState is not None:
            self._initialState = initialState
        if not self._initialState:
            return
        else:
            for groupID, value in self._initialState.iteritems():
                if isinstance(value, Iterable) and not isinstance(value, basestring):
                    for item in value:
                        self._state[groupID].add(item)

                self._state[groupID].add(value)

            return

    def __clear(self):
        self._state = defaultdict(set)
        self.__searchString = u''
