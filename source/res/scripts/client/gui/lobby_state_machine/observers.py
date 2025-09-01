# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/observers.py
from __future__ import absolute_import
import logging
import weakref
from functools import partial
import typing
from frameworks.state_machine import BaseStateObserver, State
from frameworks.state_machine.visitor import isDescendantOf
from frameworks.wulf import WindowStatus
from frameworks.wulf.gui_constants import ShowingStatus
from gui.Scaleform.framework.entities.View import ViewKey
from gui.lobby_state_machine.events import _BackNavigationGeneratedNavigationEvent
from gui.lobby_state_machine.recorded_states import getViewKeyAlias
from gui.lobby_state_machine.states import SubScopeSubLayerState, SubScopeTopLayerState, _SubScopeTopLayerEmptyState, _TopScopeTopLayerEmptyState, LobbyState, UntrackedState, compareViewKeys
from gui.shared.events import NavigationEvent
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
_logger = logging.getLogger(__name__)

class _StateClosingObserver(BaseStateObserver):

    def __init__(self, lsm):
        super(_StateClosingObserver, self).__init__()
        self.__lsmRef = weakref.ref(lsm)

    def clear(self):
        self.__lsmRef = lambda : None

    def isObservingState(self, state):
        return isinstance(state, LobbyState)

    def onStateChanged(self, state, stateEntered, event=None):
        lsm = self.__lsmRef()
        if lsm is None:
            _logger.warning('LobbyStateMachine is None! State changes should not have happened. State: %r, stateEntered: %r, event: %r', state, stateEntered, event)
            return
        else:
            subTopEmpty = lsm.getStateByCls(_SubScopeTopLayerEmptyState)
            topTopEmpty = lsm.getStateByCls(_TopScopeTopLayerEmptyState)
            if isDescendantOf(state, lsm.getStateByCls(SubScopeTopLayerState)):
                if not topTopEmpty.isEntered():
                    lsm.post(NavigationEvent(topTopEmpty.getStateID()))
            elif isDescendantOf(state, lsm.getStateByCls(SubScopeSubLayerState)):
                if not subTopEmpty.isEntered():
                    lsm.post(NavigationEvent(subTopEmpty.getStateID()))
                if not topTopEmpty.isEntered():
                    lsm.post(NavigationEvent(topTopEmpty.getStateID()))
            return


class _ViewKillingObserver(BaseStateObserver, EventsHandler):

    def __init__(self, lsm):
        super(_ViewKillingObserver, self).__init__()
        self.__lsmRef = weakref.ref(lsm)
        self.__viewKeysToKill = set()
        self.__subTopsToKill = set()
        self._subscribe()

    def isObservingState(self, state):
        return isinstance(state, LobbyState)

    def clear(self):
        self.__lsmRef = lambda : None
        self.__viewKeysToKill = set()
        self._unsubscribe()

    def onStateChanged(self, state, stateEntered, event=None):
        if event is None:
            return
        else:
            super(_ViewKillingObserver, self).onStateChanged(state, stateEntered, event)
            return

    def onExitState(self, state, event):
        lsm = self.__lsmRef()
        if isinstance(state, UntrackedState) and state == lsm.getStateByID(event.targetStateID):
            viewKey = state.getViewKey(state.getParamsExitedWith())
        else:
            viewKey = state.getViewKey()
        if not viewKey:
            return
        if isinstance(event, _BackNavigationGeneratedNavigationEvent):
            if event.shouldKillView:
                self.__viewKeysToKill.add(viewKey)
        else:
            inSubTop = lsm.findOwningSubtree(state) is lsm.getStateByCls(SubScopeTopLayerState)
            emptySubtree = lsm.getEmptyStateInSubtreeOf(state).isEntered()
            if not inSubTop or emptySubtree:
                self.__viewKeysToKill.add(viewKey)
            if inSubTop:
                self.__subTopsToKill.add(viewKey)

    def onEnterState(self, state, event):
        lsm = self.__lsmRef()
        subtreeRoot = lsm.findOwningSubtree(state)
        if subtreeRoot == lsm.getStateByCls(SubScopeSubLayerState):
            return
        else:
            isInternalState = subtreeRoot is None or subtreeRoot is state
            if isInternalState:
                return
            if state is lsm.getEmptyStateInSubtreeOf(state):
                enteringSubTopEmpty = isinstance(state, _SubScopeTopLayerEmptyState)
                uiLoader = dependency.instance(IGuiLoader)
                windowsManager = uiLoader.windowsManager
                for window in windowsManager.findWindows(lambda _: True):
                    viewKey = ViewKey(getViewKeyAlias(window.content))
                    relatedState = lsm.getStateByViewKey(viewKey)
                    if relatedState is not None and isDescendantOf(relatedState, subtreeRoot):
                        self.__viewKeysToKill.add(viewKey)
                    if enteringSubTopEmpty and viewKey in self.__subTopsToKill:
                        self.__viewKeysToKill.add(viewKey)

                if enteringSubTopEmpty:
                    self.__subTopsToKill = set()
            viewKeys = [ s.getViewKey() for s in subtreeRoot.getRecursiveChildrenStates() if s.getViewKey() is not None and s.getViewKey() not in self.__viewKeysToKill ]
            hasWindows = False
            hasVisibleWindows = False
            for window in self.__windowsWithViewKeys(viewKeys):
                if window.windowStatus == WindowStatus.LOADED:
                    hasWindows = True
                    if window.showingStatus == ShowingStatus.SHOWN:
                        hasVisibleWindows = True
                        break

            isVirtualState = not state.getViewKey()
            if hasVisibleWindows or not hasWindows and isVirtualState:
                self.destroyViewsOfExitedStates()
            return

    def destroyViewsOfExitedStates(self):
        lsm = self.__lsmRef()
        if lsm is None:
            _logger.warning('LobbyStateMachine is None! Cannot destroy views of exited states.')
            return
        else:
            enteredStateViewKeys = [ s.getViewKey() for s in lsm.getNonEmptyEnteredStates(onlyLeaves=False) ]
            viewKeys = [ viewKey for viewKey in self.__viewKeysToKill if viewKey and viewKey not in enteredStateViewKeys ]
            for window in self.__windowsWithViewKeys(viewKeys):
                if window.windowStatus not in (WindowStatus.DESTROYING, WindowStatus.DESTROYED):
                    _logger.debug('Killing window: %s', window.content)
                    window.destroy()

            self.__viewKeysToKill = set()
            return

    def _getEvents(self):
        appLoader = dependency.instance(IAppLoader)
        loaderManager = appLoader.getApp().loaderManager
        return ((loaderManager.onViewLoaded, self.__onViewLoaded),)

    def __onViewLoaded(self, *args, **kwargs):
        self.destroyViewsOfExitedStates()

    def __windowsWithViewKeys(self, viewKeys):

        def windowFilter(viewKeys, w):
            return w.content and any((compareViewKeys(w.content, viewKey) for viewKey in viewKeys))

        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        windows = set(windowsManager.findWindows(partial(windowFilter, viewKeys)))
        return windows
