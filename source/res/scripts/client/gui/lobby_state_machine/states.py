# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/states.py
from __future__ import absolute_import
import itertools
import logging
import typing
import weakref
from enum import IntEnum
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import State, StateFlags
from frameworks.state_machine.transitions import TransitionType
from frameworks.state_machine.visitor import isDescendantOf, getLCA
from frameworks.wulf import WindowStatus
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.ScopeTemplates import SimpleScope
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams, GuiImplViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.lobby_state_machine.events import _NonViewClosingBackNavigationEvent, _BackNavigationEvent
from gui.lobby_state_machine.transitions import GuardTransition, NavigationTransition, _StopTransition
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NavigationEvent, LoadViewEvent, LoadGuiImplViewEvent
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
_logger = logging.getLogger(__name__)
UNTRACKED_STATE_ID_ENDING = 'untracked'
EMPTY_STATE_ID_ENDING = 'empty'

class LobbyStateFlags(StateFlags):
    HANGAR = StateFlags.MAX << 1
    MAX = HANGAR


class LobbyStateDescription(object):

    class Info(object):

        class Type(IntEnum):
            INFO = 0
            QUESTION = 1
            VIDEO = 2

        def __init__(self, label=u'', tooltipHeader=u'', tooltipBody=u'', type=Type.INFO, onMoreInfoRequested=lambda : None):
            self.label = label
            self.tooltipHeader = tooltipHeader
            self.tooltipBody = tooltipBody
            self.type = type
            self.onMoreInfoRequested = onMoreInfoRequested

    def __init__(self, title=u'', infos=()):
        self.title = title
        self.infos = infos


def getNavigationDescriptionSafe(state):
    try:
        return state.getNavigationDescription()
    except Exception as e:
        _logger.error('Unable to get a description for state: %r. Exception: %r', state, e)
        return LobbyStateDescription()


class LobbyState(State):
    STATE_ID = ''
    VIEW_KEY = None
    _PARENT_CLS = None

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LobbyState, self).__init__(stateID=self.STATE_ID, flags=flags)

    @classmethod
    def parentOf(cls, childStateCls):
        childStateCls.STATE_ID = cls.STATE_ID + '/' + childStateCls.STATE_ID
        setattr(childStateCls, '_PARENT_CLS', weakref.ref(cls))
        return childStateCls

    @classmethod
    def goTo(cls, **params):
        g_eventBus.handleEvent(NavigationEvent(cls.STATE_ID, params), EVENT_BUS_SCOPE.LOBBY)

    def goBack(self):
        if self.isEntered():
            g_eventBus.handleEvent(_BackNavigationEvent(self), EVENT_BUS_SCOPE.LOBBY)
        else:
            _logger.warning("State (%s) cannot navigate back, because it's not entered.", self.getStateID())

    def getMachine(self):
        return super(LobbyState, self).getMachine()

    def getNavigationDescription(self):
        return LobbyStateDescription()

    def getBackNavigationDescription(self, params):
        return self.getNavigationDescription().title

    def serializeParams(self):
        return {}

    def getViewKey(self, params=None):
        return self.VIEW_KEY

    def addNavigationTransition(self, targetViewState, transitionType=TransitionType.INTERNAL, record=False):
        self.addTransition(targetViewState.makeTransition(transitionType, record), targetViewState)
        if record:
            targetViewState.addTransition(self.makeTransition(transitionType, False), self)

    def addGuardTransition(self, targetViewState, condition, transitionType=TransitionType.INTERNAL, record=False):
        self.addTransition(GuardTransition(condition, transitionType, record), targetViewState)
        if record:
            targetViewState.addTransition(self.makeTransition(transitionType, False), target=self)

    def registerStates(self):
        pass

    def registerTransitions(self):
        pass

    def makeTransition(self, transitionType, record):
        return NavigationTransition(transitionType, record)

    def compareParams(self, params, otherParams):
        return params == otherParams

    def _onEntered(self, event):
        super(LobbyState, self)._onEntered(event)
        self.__subscribeToWindowChanges()

    def _onViewExternallyDestroyed(self):
        self.__unsubscribeFromWindowChanges()
        if self.isEntered():
            _logger.info('View (%s) killed. Navigating back.', self)
            g_eventBus.handleEvent(_NonViewClosingBackNavigationEvent(self), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            _logger.info('View (%s) killed. NOT navigating back -- state is not entered', self)

    def __subscribeToWindowChanges(self):
        if not self.getViewKey():
            return
        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def __unsubscribeFromWindowChanges(self):
        if not self.getViewKey():
            return
        uiLoader = dependency.instance(IGuiLoader)
        windowsManager = uiLoader.windowsManager
        windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def __shouldDisposeView(self, _):
        self._onViewExternallyDestroyed()

    def __onWindowStatusChanged(self, uniqueWindowId, status):
        if status != WindowStatus.DESTROYING:
            return
        uiLoader = dependency.instance(IGuiLoader)
        window = uiLoader.windowsManager.getWindow(uniqueWindowId)
        if not compareViewKeys(window.content, self.getViewKey()):
            return
        if isinstance(window.content, ViewImpl):
            self._onViewExternallyDestroyed()
        else:
            window.content.onDisposed += WeakMethodProxy(self.__shouldDisposeView)


class ViewLobbyState(LobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(ViewLobbyState, self).__init__(flags=flags)

    def _getViewLoadCtx(self, event):
        return event.params

    def _onEntered(self, event):
        super(ViewLobbyState, self)._onEntered(event)
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(self.getViewKey().alias, self.getViewKey().name), **self._getViewLoadCtx(event)), scope=EVENT_BUS_SCOPE.LOBBY)


SFViewLobbyState = ViewLobbyState

class GuiImplViewLobbyState(LobbyState):

    def __init__(self, viewImplClass, scope, flags=StateFlags.UNDEFINED):
        super(GuiImplViewLobbyState, self).__init__(flags=flags)
        self._viewImplClass = viewImplClass
        self._scope = scope

    def _getViewLoadCtx(self, event):
        return event.params

    def _onEntered(self, event):
        super(GuiImplViewLobbyState, self)._onEntered(event)
        uiLoader = dependency.instance(IGuiLoader)
        view = uiLoader.windowsManager.getViewByLayoutID(self.VIEW_KEY.alias)
        if view is None:
            g_eventBus.handleEvent(LoadGuiImplViewEvent(GuiImplViewLoadParams(self.getViewKey().alias, self._viewImplClass, self._scope), **self._getViewLoadCtx(event)), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self._focusView(view, event)
        return

    def _focusView(self, view, event):
        parentWindow = view.getParentWindow()
        if not parentWindow.isFocused:
            parentWindow.tryFocus()


class EmptyState(LobbyState):
    pass


class UntrackedState(LobbyState):
    LOAD_PARAMS_KEY = 'loadParams'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(UntrackedState, self).__init__(flags)
        self._paramsEnteredWith = {}
        self._paramsExitedWith = {}

    def getViewKey(self, params=None):
        if params:
            return params[self.LOAD_PARAMS_KEY].loadParams.viewKey
        else:
            return self._paramsEnteredWith[self.LOAD_PARAMS_KEY].loadParams.viewKey if self._paramsEnteredWith and self.LOAD_PARAMS_KEY in self._paramsEnteredWith else None

    def serializeParams(self):
        return self._paramsEnteredWith

    def getParamsExitedWith(self):
        return dict(self._paramsExitedWith)

    def _onEntered(self, event):
        self._paramsEnteredWith = event.params
        super(UntrackedState, self)._onEntered(event)

    def _onExited(self):
        super(UntrackedState, self)._onExited()
        self._paramsExitedWith = self._paramsEnteredWith


class _SubScopeState(LobbyState):
    STATE_ID = 'subScope'

    def __init__(self, flags=StateFlags.PARALLEL):
        super(_SubScopeState, self).__init__(flags=flags)


@_SubScopeState.parentOf
class SubScopeSubLayerState(LobbyState):
    STATE_ID = 'subLayer'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(SubScopeSubLayerState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def registerStates(self):
        self.addChildState(_SubScopeSubLayerEmptyState(StateFlags.INITIAL))
        self.addChildState(_SubScopeSubLayerUntrackedState())
        self.addChildState(_SubScopeSubLayerFinalState(StateFlags.FINAL))

    def registerTransitions(self):
        machine = self.getMachine()
        self.addNavigationTransition(machine.getStateByCls(_SubScopeSubLayerUntrackedState), TransitionType.EXTERNAL)
        self.addNavigationTransition(machine.getStateByCls(_SubScopeSubLayerEmptyState))
        finalState = machine.getStateByCls(_SubScopeSubLayerFinalState)
        self.addTransition(_StopTransition(), finalState)
        self.addNavigationTransition(self, TransitionType.EXTERNAL)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.menu.headerButtons.hangar()))


@SubScopeSubLayerState.parentOf
class _SubScopeSubLayerUntrackedState(UntrackedState):
    STATE_ID = UNTRACKED_STATE_ID_ENDING

    def getNavigationDescription(self):
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.hangar())) if self.getViewKey().alias == VIEW_ALIAS.LOBBY_HANGAR else super(_SubScopeSubLayerUntrackedState, self).getNavigationDescription()


@SubScopeSubLayerState.parentOf
class _SubScopeSubLayerEmptyState(EmptyState):
    STATE_ID = EMPTY_STATE_ID_ENDING

    def _onEntered(self, event):
        if event is not None:
            from gui.shared.event_dispatcher import showHangar
            showHangar()
        return


@SubScopeSubLayerState.parentOf
class _SubScopeSubLayerFinalState(LobbyState):
    STATE_ID = 'FINAL'

    def _onEntered(self, event):
        pass

    def _onExited(self):
        pass

    def _onViewExternallyDestroyed(self):
        pass


@_SubScopeState.parentOf
class SubScopeTopLayerState(LobbyState):
    STATE_ID = 'topLayer'

    def registerStates(self):
        self.addChildState(_SubScopeTopLayerEmptyState(StateFlags.INITIAL))
        self.addChildState(_SubScopeTopLayerUntrackedState())

    def registerTransitions(self):
        machine = self.getMachine()
        untracked = machine.getStateByCls(_SubScopeTopLayerUntrackedState)
        self.addNavigationTransition(untracked, TransitionType.EXTERNAL)
        emptyState = machine.getStateByCls(_SubScopeTopLayerEmptyState)
        self.addNavigationTransition(emptyState)
        self.addTransition(_StopTransition(), emptyState)
        untracked.addNavigationTransition(untracked, TransitionType.EXTERNAL, True)
        self.addNavigationTransition(self, TransitionType.EXTERNAL)
        for childA, childB in itertools.combinations(self.getRecursiveChildrenStates(), 2):
            notInitial = not childA.isInitial() and not childB.isInitial()
            notDescendants = not isDescendantOf(childA, childB) and not isDescendantOf(childB, childA)
            notSiblingsOfSameParent = getLCA([childA, childB]) is self
            if notInitial and notDescendants and notSiblingsOfSameParent:
                childA.addTransition(NavigationTransition(record=True), childB)
                childB.addTransition(NavigationTransition(record=True), childA)


@SubScopeTopLayerState.parentOf
class _SubScopeTopLayerUntrackedState(UntrackedState):
    STATE_ID = UNTRACKED_STATE_ID_ENDING


@SubScopeTopLayerState.parentOf
class _SubScopeTopLayerEmptyState(EmptyState):
    STATE_ID = EMPTY_STATE_ID_ENDING


class _TopScopeState(LobbyState):
    STATE_ID = 'topScope'
    SCOPE = ScopeTemplates.LOBBY_TOP_SUB_SCOPE

    def __init__(self, flags=StateFlags.PARALLEL):
        super(_TopScopeState, self).__init__(flags=flags)


@_TopScopeState.parentOf
class TopScopeTopLayerState(LobbyState):
    STATE_ID = 'topLayer'

    def registerStates(self):
        self.addChildState(_TopScopeTopLayerEmptyState(StateFlags.INITIAL))
        self.addChildState(_TopScopeTopLayerUntrackedState())

    def registerTransitions(self):
        machine = self.getMachine()
        self.addNavigationTransition(machine.getStateByCls(_TopScopeTopLayerUntrackedState), TransitionType.EXTERNAL)
        emptyState = machine.getStateByCls(_TopScopeTopLayerEmptyState)
        self.addNavigationTransition(emptyState)
        self.addTransition(_StopTransition(), emptyState)
        self.addNavigationTransition(self, TransitionType.EXTERNAL)


@TopScopeTopLayerState.parentOf
class _TopScopeTopLayerUntrackedState(UntrackedState):
    STATE_ID = UNTRACKED_STATE_ID_ENDING


@TopScopeTopLayerState.parentOf
class _TopScopeTopLayerEmptyState(EmptyState):
    STATE_ID = EMPTY_STATE_ID_ENDING


def compareViewKeys(view, stateViewKey):
    if hasattr(view, 'key'):
        return stateViewKey == view.key
    return stateViewKey.alias == view.layoutID if hasattr(view, 'layoutID') else None
