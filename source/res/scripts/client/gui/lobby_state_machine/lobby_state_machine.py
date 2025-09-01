# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/lobby_state_machine.py
from __future__ import absolute_import
import logging
from collections import deque
from functools import cmp_to_key
import typing
from future.utils import itervalues
from Event import Event, EventManager
from WeakMethod import WeakMethodProxy
from debug_utils import deprecated
from frameworks.state_machine import State, StateFlags, StateMachine
from frameworks.state_machine.exceptions import NodeError, StateMachineError, TransitionError
from frameworks.state_machine.transitions import TransitionType
from frameworks.state_machine.visitor import isDescendantOf
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.ScopeTemplates import SimpleScope
from gui.Scaleform.framework.entities.wulf_adapter import WulfPackageLayoutAdapter
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import NavigationEvent, BackNavigationEvent
from helpers import dependency
from helpers.events_handler import EventsHandler
from shared_utils import first
from skeletons.gui.impl import IGuiLoader
from .events import _NonViewClosingBackNavigationEvent, _StopEvent, _BackNavigationGeneratedNavigationEvent, _BackNavigationEvent
from .observers import _StateClosingObserver, _ViewKillingObserver
from .recorded_states import _RecordedStates, buildSerializedParamsTopDown
from .states import LobbyState, EmptyState, UntrackedState, _SubScopeState, SubScopeSubLayerState, _SubScopeSubLayerEmptyState, _SubScopeSubLayerFinalState, SubScopeTopLayerState, _SubScopeTopLayerEmptyState, _TopScopeState, TopScopeTopLayerState, _TopScopeTopLayerEmptyState, LobbyStateDescription, compareViewKeys, getNavigationDescriptionSafe
from .transitions import NavigationTransition, GuardTransition
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.entities import View
    from gui.impl.pub import ViewImpl
_logger = logging.getLogger(__name__)

class VisibleRouteInfo(object):

    def __init__(self, state=None, params=None, visualBackNavigationTarget=None, currentDescription=None, backDescription=None):
        self.state = state
        self.params = params
        self.visualBackNavigationTarget = visualBackNavigationTarget
        self.currentDescription = currentDescription
        self.backDescription = backDescription


class LobbyStateMachine(StateMachine, EventsHandler):

    def __init__(self):
        super(LobbyStateMachine, self).__init__(flags=StateFlags.PARALLEL)
        self.__eventManager = EventManager()
        self.onVisibleRouteChanged = Event(self.__eventManager)
        self.__visibleRouteInfo = VisibleRouteInfo()
        self.__currentlyProcessedEvent = None
        self.__navigationQueue = []
        self.__viewAliasesToStates = {}
        self.__scopeToLayerToStateMap = {}
        self.__stateConfigurators = []
        self.__transitionConfigurators = []
        self.__removableStateSelectors = []
        self.__backNavigationDescription = u''
        self.__recordedStates = None
        self.__viewKillingObserver = None
        self.__stateClosingObserver = None
        self.__subtreePriorities = [TopScopeTopLayerState.STATE_ID, SubScopeTopLayerState.STATE_ID, SubScopeSubLayerState.STATE_ID]
        return

    @property
    def backNavigationDescription(self):
        return self.__backNavigationDescription

    @property
    def visibleState(self):
        return self.__visibleRouteInfo.state if self.__visibleRouteInfo else None

    @property
    def visibleRouteInfo(self):
        return self.__visibleRouteInfo

    def removeSubtreePrefix(self, stateID):
        for subtreePrefix in self.__subtreePriorities:
            if stateID.startswith(subtreePrefix):
                return stateID[len(subtreePrefix):]

    @deprecated
    def getStateByViewKey(self, viewKey):
        return self.__viewAliasesToStates.get(viewKey.alias)

    def getStateByCls(self, cls):
        if not issubclass(cls, LobbyState):
            raise StateMachineError('LobbyStateMachine cannot contain states of type {}.'.format(cls))
        return self.getStateByID(cls.STATE_ID)

    def getStateByID(self, stateID):
        stack = deque(self.getChildrenStates())
        while stack:
            child = stack.popleft()
            if child.getStateID() == stateID:
                return child
            stack.extend(child.getChildrenStates())

        return None

    def getUntrackedStateFor(self, scope, layer):
        state = self.__scopeToLayerToStateMap.get(scope, {}).get(layer, None)
        if not state:
            return
        else:
            untrackedStates = state.getChildren(lambda s: isinstance(s, UntrackedState))
            return first(untrackedStates)

    def getEmptyStateInSubtreeOf(self, state):
        owningSubtree = self.findOwningSubtree(state)
        if owningSubtree is None:
            return
        else:
            emptyStates = owningSubtree.getChildren(lambda s: isinstance(s, EmptyState))
            return first(emptyStates)

    def getNonEmptyEnteredStates(self, predicate=None, onlyLeaves=True, withNavigationDescription=False):
        return [ state for state in self._entered if not isinstance(state, EmptyState) and not state.getParent().isParallel() and (predicate is None or predicate(state)) and (not any(state.getEnteredChildrenStates()) if onlyLeaves else True) and (getNavigationDescriptionSafe(state) is not None if withNavigationDescription else True) ]

    def getRelatedView(self, state):
        if not isinstance(state, LobbyState):
            return
        elif not state.getViewKey():
            return self.getRelatedView(state.getParent())
        uiLoader = dependency.instance(IGuiLoader)
        if uiLoader is None or uiLoader.windowsManager is None:
            return
        windowsManager = uiLoader.windowsManager
        windows = windowsManager.findWindows(lambda w: compareViewKeys(w.content, state.getViewKey()))
        if windows:
            view = first(windows).content
            if isinstance(view, WulfPackageLayoutAdapter):
                return view.content
            return view
        else:
            return

    def getStateFromView(self, view):
        wulfWrappedView = None
        uiLoader = dependency.instance(IGuiLoader)
        if uiLoader and uiLoader.windowsManager:
            windowsManager = uiLoader.windowsManager
            matchingWindows = windowsManager.findWindows(lambda w: isinstance(w.content, WulfPackageLayoutAdapter) and w.content.content == view)
            wulfAdapter = first(matchingWindows)
            if wulfAdapter:
                wulfWrappedView = wulfAdapter.content
        for state in self.getRecursiveChildrenStates():
            stateViewKey = state.getViewKey()
            if not stateViewKey:
                continue
            viewKeyMatches = compareViewKeys(view, stateViewKey)
            wulfViewKeyMatches = wulfWrappedView and compareViewKeys(wulfWrappedView, stateViewKey)
            if viewKeyMatches or wulfViewKeyMatches:
                return state

        return

    def findOwningSubtree(self, state):
        for stateMap in itervalues(self.__scopeToLayerToStateMap):
            for subtreeState in stateMap.values():
                if isDescendantOf(state, subtreeState) or state is subtreeState:
                    return subtreeState

        return None

    def addState(self, state):
        inferredParent = self.getStateByCls(state._PARENT_CLS())
        inferredParent.addChildState(state)

    def addNavigationTransitionFromParent(self, state, transitionType=TransitionType.INTERNAL, record=False):
        inferredParent = self.getStateByCls(state._PARENT_CLS())
        inferredParent.addNavigationTransition(state, transitionType, record)

    def addHistoryRemovableStateSelector(self, selector):
        self.__removableStateSelectors.append(selector)

    def addStateConfigurator(self, fn):
        if fn not in self.__stateConfigurators:
            self.__stateConfigurators.append(fn)

    def addTransitionConfigurator(self, fn):
        if fn not in self.__transitionConfigurators:
            self.__transitionConfigurators.append(fn)

    def configure(self, *args, **kwargs):
        subScopeState = _SubScopeState()
        subScopeSubLayerState = SubScopeSubLayerState()
        subScopeTopLayerState = SubScopeTopLayerState()
        subScopeState.addChildState(subScopeSubLayerState)
        subScopeState.addChildState(subScopeTopLayerState)
        topScopeState = _TopScopeState()
        topScopeTopLayerState = TopScopeTopLayerState()
        topScopeState.addChildState(topScopeTopLayerState)
        self.addChildState(subScopeState)
        self.addChildState(topScopeState)
        self.__scopeToLayerToStateMap = {ScopeTemplates.LOBBY_SUB_SCOPE: {WindowLayer.SUB_VIEW: subScopeSubLayerState,
                                          WindowLayer.TOP_SUB_VIEW: subScopeTopLayerState},
         ScopeTemplates.LOBBY_TOP_SUB_SCOPE: {WindowLayer.TOP_SUB_VIEW: topScopeTopLayerState}}
        for fn in self.__stateConfigurators:
            fn(self, *args, **kwargs)

        for state in self.visitInOrder(lambda node: isinstance(node, LobbyState)):
            state.registerStates()

        for fn in self.__transitionConfigurators:
            fn(self, *args, **kwargs)

        for state in self.visitInOrder(lambda node: isinstance(node, LobbyState)):
            state.registerTransitions()

        stack = deque(self.getChildrenStates())
        while stack:
            s = stack.popleft()
            if isinstance(s, LobbyState) and s.getViewKey() is not None:
                self.__viewAliasesToStates[s.getViewKey().alias] = s
            stack.extend(s.getChildrenStates())

        return

    def start(self, doValidate=True):
        self.__recordedStates = _RecordedStates(WeakMethodProxy(self.__updateVisibleRoute))
        self.__recordedStates.removableStateSelectors.extend(self.__removableStateSelectors)
        self.__stateClosingObserver = _StateClosingObserver(self)
        self.connect(self.__stateClosingObserver)
        self.__viewKillingObserver = _ViewKillingObserver(self)
        self.connect(self.__viewKillingObserver)
        self._subscribe()
        if doValidate:
            for state in self.visitInOrder(lambda node: isinstance(node, LobbyState)):
                parentClsRef = getattr(type(state), '_PARENT_CLS', None)
                if parentClsRef is not None and not isinstance(state.getParent(), parentClsRef()):
                    raise NodeError('State %s declared as child of %s, but its parent is %s' % (state, parentClsRef(), state.getParent()))
                for transition in state.getChildren(lambda node: isinstance(node, NavigationTransition)):
                    targetState = first(transition.getTargets())
                    sameSubtree = self.findOwningSubtree(state) == self.findOwningSubtree(targetState)
                    if not sameSubtree and transition.record:
                        raise TransitionError('%s from %s to %s is a cross subtree transition with record flag set!Record flags on cross subtree transitions are not allowed.' % (type(transition), state.getStateID(), targetState.getStateID()))

        super(LobbyStateMachine, self).start(doValidate)
        return

    def stop(self):
        if self.isStateEntered(_SubScopeSubLayerFinalState.STATE_ID) or not self.isRunning():
            self.clear()
            _logger.debug('%r: Machine is not started', self)
            return
        else:
            self._unsubscribe()
            self.post(_StopEvent(_TopScopeTopLayerEmptyState.STATE_ID))
            self.post(_StopEvent(_SubScopeTopLayerEmptyState.STATE_ID))
            self.post(_StopEvent(_SubScopeSubLayerFinalState.STATE_ID))
            self.__currentlyProcessedEvent = None
            self.__navigationQueue = []
            self.__backNavigationDescription = u''
            self.__recordedStates.clear()
            self.__eventManager.clear()
            self.__viewAliasesToStates = {}
            self.__scopeToLayerToStateMap = {}
            self.__removableStateSelectors = []
            self.__visibleRouteInfo = VisibleRouteInfo()
            super(LobbyStateMachine, self).stop()
            self.__recordedStates = None
            self.__stateClosingObserver = None
            self.__viewKillingObserver = None
            return

    def post(self, event):
        if not isinstance(event, (NavigationEvent, BackNavigationEvent, _BackNavigationEvent)):
            raise StateMachineError('LobbyStateMachine only accepts events of NavigationEvent type. Invalid event: {}'.format(event))
        if not self.isRunning():
            _logger.info('State machine is not running. Ignoring navigation to %r', event)
            return
        else:
            if isinstance(event, (BackNavigationEvent, _BackNavigationEvent)):
                if event.requestingState is None:
                    event.requestingState = first(self.getNonEmptyEnteredStates()[::-1])
                    _logger.info('Navigating back requested by None, resolved to (%s)', event.requestingState.getStateID())
                else:
                    _logger.info('Navigating back requested by (%s)', event.requestingState.getStateID())
                shouldKillView = not isinstance(event, _NonViewClosingBackNavigationEvent)
                state, params = self.__getBackNavigationTargetAndParams(event.requestingState, False)
                event = _BackNavigationGeneratedNavigationEvent(state.getStateID(), params, shouldKillView)
            if self.__currentlyProcessedEvent:
                _logger.info('Queued navigation to %s', event.targetStateID)
                self.__navigationQueue.append(event)
                return
            _logger.info('Navigating to %s', event.targetStateID)
            self.__currentlyProcessedEvent = event
            try:
                super(LobbyStateMachine, self).post(event)
            except Exception as e:
                _logger.error('An exception was caught while processing event: %r.', event)
                _logger.exception(e)

            self.__currentlyProcessedEvent = None
            if self.__navigationQueue:
                queuedEvent = self.__navigationQueue.pop(0)
                _logger.info('Popping %s from navigation queue', queuedEvent)
                self.post(queuedEvent)
            return

    def _getListeners(self):
        return ((NavigationEvent.EVENT_ID, self.post, EVENT_BUS_SCOPE.LOBBY),
         (BackNavigationEvent.EVENT_ID, self.post, EVENT_BUS_SCOPE.LOBBY),
         (_BackNavigationEvent.EVENT_ID, self.post, EVENT_BUS_SCOPE.LOBBY),
         (_NonViewClosingBackNavigationEvent.EVENT_ID, self.post, EVENT_BUS_SCOPE.LOBBY))

    def _process(self, transitions, event):
        relevantTransition = self.__findRelevantTransition(transitions)
        isTransitioningByBackNavigation = isinstance(event, _BackNavigationGeneratedNavigationEvent)
        if isinstance(relevantTransition, GuardTransition) and isTransitioningByBackNavigation:
            self.__recordedStates.push(self.getStateByID(event.targetStateID))
        self.__recordedStates.pushRecordedTransitionSource(relevantTransition, isTransitioningByBackNavigation)
        super(LobbyStateMachine, self)._process(transitions, event)
        targetState = relevantTransition.getTargets()[0]
        self.__recordedStates.clearCycles(self, targetState, self.__currentlyProcessedEvent.params)
        if self.__navigationQueue:
            self.__currentlyProcessedEvent = None
            queuedEvent = self.__navigationQueue.pop(0)
            _logger.info('Popping %s from navigation queue', queuedEvent)
            self.post(queuedEvent)
            return
        else:
            self.__visibleRouteInfo.params = event.params
            self.__updateVisibleRoute()
            return

    def __updateVisibleRoute(self):
        enteredLeafStates = self.getNonEmptyEnteredStates()
        visibleState = first(enteredLeafStates[::-1])
        visibleStateWithDescription = first(self.getNonEmptyEnteredStates(withNavigationDescription=True)[::-1])
        currentNavigationDescription = None
        if visibleStateWithDescription:
            currentNavigationDescription = getNavigationDescriptionSafe(visibleStateWithDescription)
            if not isinstance(currentNavigationDescription, LobbyStateDescription):
                _logger.error('%r implements an old version of getNavigationDescription. Please update it to return LobbyStateDescription!', visibleStateWithDescription)
                currentNavigationDescription = LobbyStateDescription(title=currentNavigationDescription)
        visualBackNavigationTarget, recordedParams = self.__findPreviousVisibleState(visibleStateWithDescription)
        self.__backNavigationDescription = None
        if visualBackNavigationTarget:
            self.__backNavigationDescription = visualBackNavigationTarget.getBackNavigationDescription(recordedParams)
        _logger.debug('Visible route: %s', visibleState.getStateID() if visibleState else 'NO STATE VISIBLE')
        _logger.debug('Routes: [%s]', ', '.join((s.getStateID() for s in enteredLeafStates)))
        _logger.debug('Current state description: "%s" (state: %s)', currentNavigationDescription, visibleStateWithDescription.getStateID() if visibleStateWithDescription else None)
        if visibleStateWithDescription is not visibleState:
            _logger.debug('\tDescription derived from (%s) instead of visible state (%s) because it has no description', visibleStateWithDescription.getStateID() if visibleStateWithDescription else None, visibleState.getStateID() if visibleState else None)
        _logger.debug('Back navigation description: "%s" (state: %s)', self.__backNavigationDescription, visualBackNavigationTarget.getStateID())
        backNavigationTarget, _ = self.__getBackNavigationTargetAndParams(visibleState)
        _logger.debug('Back navigation would return to: %s', backNavigationTarget.getStateID())
        _logger.debug('Params of entered state: %s', self.__visibleRouteInfo.params)
        _logger.debug('Recorded states: %s', self.__recordedStates)
        _logger.info('Visible route changed to: %r', visibleState)
        self.__visibleRouteInfo = VisibleRouteInfo(visibleState, self.__visibleRouteInfo.params, visualBackNavigationTarget, currentNavigationDescription, self.__backNavigationDescription)
        self.onVisibleRouteChanged(self.__visibleRouteInfo)
        return

    def __findRelevantTransition(self, transitions):
        filteredTransitions = [ transition for transition in transitions if isinstance(transition, NavigationTransition) ]
        if len(filteredTransitions) <= 1:
            return first(filteredTransitions)
        recordTransitions = [ t for t in filteredTransitions if t.record ]
        if len(recordTransitions) == 1:
            return first(recordTransitions)
        if len(recordTransitions) > 1:
            raise TransitionError('Multiple record transitions are not allowed.')
        target = first(filteredTransitions).getTargets()[0]
        if any((target not in t.getTargets() for t in filteredTransitions)):
            raise TransitionError('Event {} caused multiple transitions with different targets'.format(self.__currentlyProcessedEvent))
        crossSubtreeTransitions = [ t for t in filteredTransitions if not any((self.findOwningSubtree(t.getSource()) is self.findOwningSubtree(target) for target in t.getTargets())) ]
        return first(crossSubtreeTransitions) if crossSubtreeTransitions else first(filteredTransitions)

    def __findPreviousVisibleState(self, state):
        defaultState = self.getStateByCls(SubScopeSubLayerState)
        if state is None:
            return (defaultState, buildSerializedParamsTopDown(defaultState))
        elif isinstance(state, EmptyState):
            state = first(self.getNonEmptyEnteredStates(lambda s: s is not state, withNavigationDescription=True)[::-1])
            return self.__findPreviousVisibleState(state)
        else:
            subtree = self.findOwningSubtree(state)
            recordedState, recordedParams = self.__recordedStates.peek()
            if recordedState and self.findOwningSubtree(recordedState) is subtree:
                return (recordedState, recordedParams)
            prevVisibleState = first(self.getNonEmptyEnteredStates(lambda s: s is not state and self.findOwningSubtree(s) is not subtree, withNavigationDescription=True)[::-1]) or defaultState
            return (prevVisibleState, buildSerializedParamsTopDown(prevVisibleState))

    def __sortNavigationQueue(self):

        def eventComparator(event, otherEvent):
            target = self.getStateByID(event.targetStateID)
            otherTarget = self.getStateByID(otherEvent.targetStateID)
            subtree = self.findOwningSubtree(target)
            otherSubtree = self.findOwningSubtree(otherTarget)
            eventSubtreePriority = self.__subtreePriorities.index(subtree.getStateID())
            otherSubtreePriority = self.__subtreePriorities.index(otherSubtree.getStateID())
            return int(isinstance(target, EmptyState)) - int(isinstance(otherTarget, EmptyState)) if eventSubtreePriority == otherSubtreePriority else eventSubtreePriority - otherSubtreePriority

        self.__navigationQueue.sort(key=cmp_to_key(eventComparator))

    def __getBackNavigationTargetAndParams(self, currentVisibleState, peekOnly=True):
        backNavigationTarget = self.getStateByCls(_SubScopeSubLayerEmptyState)
        params = {}
        takeRecordedState = currentVisibleState is None
        if currentVisibleState:
            visibleSubtree = self.findOwningSubtree(currentVisibleState)
            backNavigationTarget = visibleSubtree
            if self.__recordedStates.hasEntries():
                recordedState, _ = self.__recordedStates.peek()
                takeRecordedState = self.findOwningSubtree(recordedState) == backNavigationTarget
        if takeRecordedState and self.__recordedStates.hasEntries():
            backNavigationTarget, params = self.__recordedStates.peek() if peekOnly else self.__recordedStates.pop()
        return (backNavigationTarget, params)


def _getInitialLeaf(state):
    initialLeaf = None
    children = [state]
    while children:
        initialLeaf = children[0]
        children = initialLeaf.getChildren(lambda s: isinstance(s, State) and s.isInitial())

    return initialLeaf
