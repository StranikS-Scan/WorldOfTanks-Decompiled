# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/state.py
from collections import Iterable, defaultdict
from account_helpers.AccountSettings import AccountSettings, TANKMEN_LIST
from Event import Event
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType

class FilterState(object):
    GROUPS = ToggleGroupType

    def __init__(self, initialState=None, isWotPlus=False, persistor=None):
        self.onStateChanged = Event()
        self._state = defaultdict(set)
        self._initialState = initialState or {}
        self.__searchString = u''
        self._isWotPlus = isWotPlus
        self._persistor = persistor
        self.reinit()

    def __contains__(self, item):
        return item in self._state

    def __getitem__(self, item):
        return self._state[item]

    def __iter__(self):
        return iter(self._state)

    def __repr__(self):
        return '{0}<initialState={1!r}, state={2!r}, searchString={3!r}, isWotPlus={4!r}, persistor={5!r}>'.format(self.__class__.__name__, self._initialState, self._state, self.__searchString, self._isWotPlus, self._persistor)

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
        if self._isWotPlus:
            self.reinit()
            return
        else:
            self._clear()
            if self._persistor is not None:
                self._persistor.save(self._state)
            self.onStateChanged()
            return

    def update(self, groupID, fieldID):
        if fieldID in self._state[groupID]:
            self._state[groupID].remove(fieldID)
        else:
            self._state[groupID].add(fieldID)
        if self._persistor is not None:
            self._persistor.save(self._state)
        self.onStateChanged()
        return

    def reinit(self, state=None):
        self._clear()
        self._reinitState(initialState=state)
        if self._persistor is not None and not self._isWotPlus:
            self._persistor.load(self._state)
        self.onStateChanged()
        return

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

    def _clear(self):
        self._state = defaultdict(set)
        self.__searchString = u''


class Persistor(object):

    def __init__(self, storageKey, persistentGroups=None, excludeKeys=None, ignoreDefault=False):
        self.__key = storageKey
        self.__persistentGroups = persistentGroups or []
        self.__excludeKeys = excludeKeys or {}
        self.__ignoreDefault = ignoreDefault

    def __repr__(self):
        return '{0}<storageKey={1!r}, persistentGroups={2!r}, excludeKeys={3!r}>'.format(self.__class__.__name__, self.__key, self.__persistentGroups, self.__excludeKeys)

    def load(self, stateDict):
        stored = AccountSettings.getFilter(TANKMEN_LIST)
        persistedState = stored.get(self.__key, {})
        for groupID, items in persistedState.iteritems():
            if groupID in self.__persistentGroups:
                exclude = set(self.__excludeKeys.get(groupID, []))
                persistedValues = set(items) - exclude
                if self.__ignoreDefault:
                    stateDict[groupID] = persistedValues
                else:
                    stateDict[groupID].update(persistedValues)

    def save(self, stateDict):
        stored = AccountSettings.getFilter(TANKMEN_LIST)
        stored[self.__key] = self.__storableState(stateDict)
        AccountSettings.setFilter(TANKMEN_LIST, stored)

    def __storableState(self, stateDict):
        result = {}
        for groupID in self.__persistentGroups:
            exclude = set(self.__excludeKeys.get(groupID, []))
            items = stateDict.get(groupID, set()) - exclude
            result[groupID] = list(items)

        return result
