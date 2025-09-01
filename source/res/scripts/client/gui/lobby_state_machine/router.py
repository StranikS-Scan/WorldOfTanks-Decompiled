# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/router.py
from __future__ import absolute_import
import json
import logging
import typing
from frameworks.state_machine import BaseStateObserver, visitor
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.resource_mapping import resLayoutToStateId, stateIdToResLayout
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NavigationEvent
from helpers.events_handler import EventsHandler
from gui.lobby_state_machine.states import UntrackedState, LobbyState
if typing.TYPE_CHECKING:
    from frameworks.state_machine import State
    from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.lobby_state_machine.routable_view import IRoutableView
_logger = logging.getLogger(__name__)
_NAVIGATION_ROUTE_KEY = 'route'
_NAVIGATION_PARAMS_KEY = 'params'

class Router(EventsHandler):

    def __init__(self, routableView, routePrefix):
        self._routableView = routableView
        self._routePrefix = routePrefix
        self._route = ''
        self._params = {}

    def init(self):
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        self._params = {}
        self._route = ''
        self._routePrefix = ''
        self._routableView = None
        return

    @property
    def routePrefix(self):
        return self._routePrefix

    def setRoute(self, stateId, params):
        self._route = self._encodeRoute(stateId)
        self._params = self._encodeParams(params)
        self.__updateModel()

    def _getEvents(self):
        model = self._routableView.getRouterModel()
        events = ((model.navigateTo, self.__navigateTo), (model.navigateBack, self.__navigateBack))
        return events

    def _encodeRoute(self, stateId):
        resourceMappedRoute = stateIdToResLayout(stateId)
        if resourceMappedRoute:
            return resourceMappedRoute
        route = stateId
        if stateId.startswith(self._routePrefix):
            route = stateId[len(self._routePrefix):]
        else:
            _logger.warning('Entered state (%r) does not contain specified route prefix (%s)', stateId, self._routePrefix)
        return route

    def _encodeParams(self, params):
        encodedParams = ''
        if UntrackedState.LOAD_PARAMS_KEY in params:
            _logger.info('Marshalling _UntrackedStateForwardedParams into JSON is unsupported. Removing "%s" from params. Params pre-removal: %r', UntrackedState.LOAD_PARAMS_KEY, params)
            params = dict(params)
            del params[UntrackedState.LOAD_PARAMS_KEY]
        try:
            encodedParams = json.dumps(params)
        except (TypeError, UnicodeDecodeError) as e:
            _logger.info('Unable to marshall params into JSON: %r. Exception: %r', params, e)

        return encodedParams

    def _decodeStateId(self, route):
        resourceMappedRoute = resLayoutToStateId(route)
        return resourceMappedRoute if resourceMappedRoute else self._routePrefix + route

    def _decodeJsonParams(self, jsonParams):
        params = {}
        try:
            params = json.loads(jsonParams)
        except ValueError as e:
            _logger.warning('Failed unmarshalling malformed json: %s. Exception: %r', jsonParams, e)

        return params

    def __updateModel(self):
        _logger.debug('Encoded route: %r', self._route)
        _logger.debug('Encoded params: %r', self._params)
        with self._routableView.getRouterModel().transaction() as model:
            model.setRoute(self._route)
            model.setParams(self._params)

    def __navigateTo(self, navigationInfo):
        stateId = self._decodeStateId(navigationInfo.get(_NAVIGATION_ROUTE_KEY, ''))
        params = self._decodeJsonParams(navigationInfo.get(_NAVIGATION_PARAMS_KEY, '{}') or '{}')
        _logger.debug('Decoded stateId: %r', stateId)
        _logger.debug('Decoded params: %r', params)
        g_eventBus.handleEvent(NavigationEvent(stateId, params), EVENT_BUS_SCOPE.LOBBY)

    def __navigateBack(self):
        lsm = getLobbyStateMachine()
        if not lsm or not lsm.visibleState:
            return
        lsm.visibleState.goBack()


class SubstateRouter(BaseStateObserver):

    def __init__(self, lsm, routableView, rootState):
        super(SubstateRouter, self).__init__()
        self.__lsm = lsm
        if isinstance(rootState, LobbyState):
            self.__rootState = rootState
        elif issubclass(rootState, LobbyState):
            self.__rootState = self.__lsm.getStateByCls(rootState)
        self.__router = Router(routableView, self.__rootState.getParent().getStateID())
        if not self.__rootState.getStateID().startswith(self.__router.routePrefix):
            _logger.warning('Router prefix (%s) is not part of the state (%r) owning the router.', self.__router.routePrefix, self.__rootState)

    def init(self):
        self.__router.init()
        self.__lsm.connect(self)

    def fini(self):
        self.__router.fini()
        self.__lsm.disconnect(self)
        self.__lsm = None
        self.__rootState = None
        return

    def isObservingState(self, state):
        return visitor.isDescendantOf(state, self.__rootState)

    def onEnterState(self, state, event):
        stateId = state.getStateID()
        if self.__router.routePrefix not in stateId:
            _logger.warning('Entered state (%s) which is not a child of state (%r) where the router is rooted.', state, self.__rootState)
        self.__router.setRoute(stateId, event.params if event else {})
        super(SubstateRouter, self).onEnterState(state, event)
