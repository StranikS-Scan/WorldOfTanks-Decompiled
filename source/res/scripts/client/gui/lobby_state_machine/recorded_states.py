# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/recorded_states.py
from __future__ import absolute_import
import logging
import typing
from frameworks.state_machine.visitor import isDescendantOf, getAncestors
from frameworks.wulf import WindowStatus
from gui.lobby_state_machine.states import LobbyState, compareViewKeys
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.transitions import NavigationTransition
_logger = logging.getLogger(__name__)

class _RecordedStates(EventsHandler):

    def __init__(self, onRecordedStatesExternallyChanged):
        self.removableStateSelectors = []
        self.__onRecordedStatesExternallyChanged = onRecordedStatesExternallyChanged
        self.__stateWithParamStack = []
        self._subscribe()

    def __repr__(self):
        return '{}'.format([ (s.getStateID(), p) for s, p in self.__stateWithParamStack ])

    def getStateWithParamStack(self):
        return self.__stateWithParamStack[:]

    def clear(self):
        self._unsubscribe()
        self.__stateWithParamStack = []
        self.__onRecordedStatesExternallyChanged = None
        self.removableStateSelectors = []
        return

    def push(self, state):
        self.__stateWithParamStack.append((state, buildSerializedParamsTopDown(state)))

    def peek(self):
        return self.__stateWithParamStack[-1] if self.hasEntries() else (None, None)

    def pop(self):
        return self.__stateWithParamStack.pop()

    def hasEntries(self):
        return bool(self.__stateWithParamStack)

    def pushRecordedTransitionSource(self, transition, isTransitioningByBackNavigation):
        sourceState = transition.getSource()
        for s, _ in self.__stateWithParamStack[::-1]:
            if s is None or not isDescendantOf(s, sourceState):
                break
            self.__stateWithParamStack.pop(len(self.__stateWithParamStack) - 1)

        if transition.record and not isTransitioningByBackNavigation:
            self.push(sourceState)
        return

    def clearCycles(self, lsm, state, params):
        if not self.hasEntries():
            return
        repeatingStateIndex = len(self.__stateWithParamStack)
        for i, (pastState, pastParams) in enumerate(self.__stateWithParamStack):
            if pastState.getStateID() == state.getStateID() and state.compareParams(params, pastParams):
                repeatingStateIndex = i
                break

        subtree = lsm.findOwningSubtree(state)
        entriesToRemove = []
        slicedStack = self.__stateWithParamStack[repeatingStateIndex:]
        for pastState, pastParams in slicedStack:
            if lsm.findOwningSubtree(pastState) == subtree:
                entriesToRemove.append((pastState, pastParams))

        self.__stateWithParamStack = self.__stateWithParamStack[:repeatingStateIndex] + [ (state, params) for state, params in slicedStack if (state, params) not in entriesToRemove ]

    def _getEvents(self):
        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        return ((windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged),)

    def __onWindowStatusChanged(self, uniqueWindowId, status):
        uiLoader = dependency.instance(IGuiLoader)
        window = uiLoader.windowsManager.getWindow(uniqueWindowId)
        if not window:
            return
        view = window.content
        if status != WindowStatus.DESTROYING or not view:
            return
        entriesToRemove = []
        for state, params in self.__stateWithParamStack:
            viewKeysMatch = state.getViewKey(params) and compareViewKeys(view, state.getViewKey(params))
            if viewKeysMatch and any((selector(state, params) for selector in self.removableStateSelectors)):
                entriesToRemove.append((state, params))

        if entriesToRemove:
            _logger.debug('Clearing entries in LSM recorded states because a %r was closed', view)
            _logger.debug('Recorded states before cleaning: %s', self)
            for entry in entriesToRemove:
                self.__stateWithParamStack.remove(entry)

            _logger.debug('Recorded states after cleaning: %s', self)
            self.__onRecordedStatesExternallyChanged()


def buildSerializedParamsTopDown(sourceState):
    params = []
    stateStack = [sourceState] + getAncestors(sourceState)
    while stateStack:
        state = stateStack.pop()
        if isinstance(state, LobbyState):
            params += state.serializeParams().items()

    return dict(params)


def getViewKeyAlias(view):
    if not view:
        return
    else:
        keyAlias = None
        if hasattr(view, 'key'):
            keyAlias = view.key.alias
        elif hasattr(view, 'layoutID'):
            keyAlias = view.layoutID
        return keyAlias
