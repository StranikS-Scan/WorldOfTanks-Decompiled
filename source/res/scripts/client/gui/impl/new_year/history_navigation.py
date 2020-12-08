# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/history_navigation.py
from gui.impl.gen import R
from gui.impl.new_year.navigation import NewYearNavigation, ViewLoadingParams, ViewAliases

class _NavigationHistory(object):

    def __init__(self):
        self.__chain = []
        self.__states = {}
        self.__goingBack = False

    def addToHistory(self, alias, state):
        self.__chain.append(alias)
        self.__states[alias] = state

    def getLast(self, pop=False):
        if self.__chain:
            if pop:
                return self.__chain.pop()
            return self.__chain[-1]
        else:
            return None

    def pop(self):
        self.__chain.pop()

    def getState(self, viewAlias):
        return self.__states.get(viewAlias)

    def setGoingBack(self, value):
        self.__goingBack = value

    def getGoingBack(self):
        return self.__goingBack

    def invalidateViewState(self, viewAlias):
        if viewAlias not in self.__chain and viewAlias in self.__states:
            del self.__states[viewAlias]

    def remove(self, viewAlias):
        if viewAlias in self.__chain:
            self.__chain.remove(viewAlias)
            del self.__states[viewAlias]

    def clear(self):
        self.__chain = []
        self.__states = {}

    @property
    def isEmpty(self):
        return len(self.__chain) == 0


class NewYearHistoryNavigation(NewYearNavigation):
    __slots__ = ()
    _navigationHistory = _NavigationHistory()

    def __init__(self, *args, **kwargs):
        if self._isScopeWatcher:
            self._navigationHistory.remove(self.__getNavigationAlias())
        super(NewYearHistoryNavigation, self).__init__(*args, **kwargs)

    def _finalize(self):
        if self._isScopeWatcher:
            self._navigationHistory.invalidateViewState(self.__getNavigationAlias())
        super(NewYearHistoryNavigation, self)._finalize()

    def _goToMainView(self):
        self._switchToView(ViewAliases.GLADE_VIEW, saveHistory=False)
        self._navigationHistory.clear()

    def _switchToView(self, aliasName, *args, **kwargs):
        saveHistory = kwargs.pop('saveHistory', False)
        popHistory = kwargs.pop('popHistory', False)
        if popHistory:
            self._navigationHistory.pop()
        if saveHistory:
            self.__preserveHistory()
        super(NewYearHistoryNavigation, self)._switchToView(aliasName, *args, **kwargs)

    def _getBackPageName(self):
        lastViewed = self._navigationHistory.getLast()
        return R.strings.ny.backButton.dyn(lastViewed)() if lastViewed else R.invalid()

    def _restoreState(self, stateInfo):
        pass

    def _goBack(self):
        if self._navigationHistory.isEmpty:
            return
        backPageAlias = self._navigationHistory.getLast()
        loadingParams = ViewLoadingParams.get(backPageAlias)
        if loadingParams:
            self._navigationHistory.setGoingBack(True)
            self._switchToView(backPageAlias, saveHistory=False, popHistory=True, **self.__getStateFromHistory())

    def _getInfoForHistory(self):
        return None

    def __getNavigationAlias(self):
        return self._navigationAlias or self.__class__.__name__

    def __preserveHistory(self):
        viewInfo = self._getInfoForHistory()
        if viewInfo is not None:
            name = self.__getNavigationAlias()
            self._navigationHistory.addToHistory(name, viewInfo)
        return

    def __getStateFromHistory(self):
        lastAlias = self._navigationHistory.getLast()
        stateInfo = self._navigationHistory.getState(lastAlias)
        return {} if stateInfo is None else stateInfo
