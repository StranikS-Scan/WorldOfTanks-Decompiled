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
from gui.lobby_state_machine.events import _BackNavigationGeneratedNavigationEvent
from gui.lobby_state_machine.recorded_states import _RecordedStates
from gui.lobby_state_machine.states import SubScopeSubLayerState, SubScopeTopLayerState, _SubScopeTopLayerEmptyState, _TopScopeTopLayerEmptyState, LobbyState, UntrackedState, compareViewKeys
from gui.shared.events import NavigationEvent
from gui.shared.utils.callable_delayer import CallableDelayer, delayUntilParentWindowReady
from helpers import dependency
from shared_utils import first
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine, VisibleRouteInfo
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


class _ViewKillingObserver(BaseStateObserver):

    def __init__(self, lsm, recordedStates):
        super(_ViewKillingObserver, self).__init__()
        self.__lsmRef = weakref.ref(lsm)
        self.__recordedStates = recordedStates
        self.__viewKeysToKill = set()
        self.__subTopsToKill = set()
        self.__callableDelayer = CallableDelayer()
        lsm.onVisibleRouteChanged += self.__visibleRouteChanged

    def isObservingState(self, state):
        return isinstance(state, LobbyState)

    def clear(self):
        self.__lsmRef().onVisibleRouteChanged -= self.__visibleRouteChanged
        self.__callableDelayer.clear()
        self.__viewKeysToKill = set()
        self.__subTopsToKill = set()
        self.__recordedStates = None
        self.__lsmRef = lambda : None
        return

    def onExitState(self, state, event):
        if event is None:
            return
        else:
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
                if inSubTop:
                    self.__subTopsToKill.add(viewKey)
                else:
                    self.__viewKeysToKill.add(viewKey)
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

    def __visibleRouteChanged(self, routeInfo):
        lsm = self.__lsmRef()
        view = lsm.getRelatedView(routeInfo.state)
        if view is None:
            enteredStates = lsm.getNonEmptyEnteredStates(onlyLeaves=False)
            views = [ lsm.getRelatedView(state) for state in enteredStates if lsm.getRelatedView(state) ]
            view = first(views[::-1])
        if view is None:
            return
        else:
            subTopEmpty = lsm.getEmptyStateInSubtreeOf(lsm.getStateByCls(SubScopeTopLayerState)).isEntered()
            if subTopEmpty:
                self.__viewKeysToKill.update(self.__subTopsToKill)
                self.__subTopsToKill = set()
            else:
                for subTop in set(self.__subTopsToKill):
                    viewInStateHistory = self.__recordedStates.contains(lambda s, _: s.getViewKey() == subTop)
                    if not viewInStateHistory:
                        self.__viewKeysToKill.add(subTop)
                        self.__subTopsToKill.remove(subTop)

            delayUntilParentWindowReady(self.__callableDelayer, view, self.destroyViewsOfExitedStates)
            return

    def __windowsWithViewKeys(self, viewKeys):

        def windowFilter(viewKeys, w):
            return w.content and any((compareViewKeys(w.content, viewKey) for viewKey in viewKeys))

        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        windows = set(windowsManager.findWindows(partial(windowFilter, viewKeys)))
        return windows
