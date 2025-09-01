# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/header_state_presenter.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.page.header.header_state_model import HeaderStateModel, HeaderType
from gui.impl.pub.view_component import ViewComponent
from gui.shared.utils.callable_delayer import CallableDelayer, delayUntilParentWindowReady
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import Router
from gui.lobby_state_machine.states import LobbyStateFlags
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
_logger = logging.getLogger(__name__)

class HeaderStatePresenter(ViewComponent[HeaderStateModel], IRoutableView):

    def __init__(self):
        super(HeaderStatePresenter, self).__init__(model=HeaderStateModel)
        self.__lsm = None
        self.__router = None
        self.__callableDelayer = CallableDelayer()
        return

    def getRouterModel(self):
        return self.getViewModel().router

    def _onLoading(self, *args, **kwargs):
        self.__lsm = getLobbyStateMachine()
        self.__router = Router(self, '')
        self.__router.init()
        visibleRouteInfo = self.__lsm.visibleRouteInfo
        if visibleRouteInfo:
            self.__onStateChanged(visibleRouteInfo)
        super(HeaderStatePresenter, self)._onLoading(args, kwargs)

    def _finalize(self):
        self.__callableDelayer.clear()
        self.__callableDelayer = None
        super(HeaderStatePresenter, self)._finalize()
        self.__router.fini()
        self.__router = None
        self.__lsm = None
        return

    def _getEvents(self):
        return ((self.__lsm.onVisibleRouteChanged, self.__onStateChanged),)

    def __onStateChanged(self, routeInfo):
        self.__callableDelayer.clear()
        view = self.__lsm.getRelatedView(routeInfo.state)
        delayUntilParentWindowReady(self.__callableDelayer, view, partial(self.__processRouteChange, routeInfo))

    def __processRouteChange(self, routeInfo):
        if routeInfo.state is None:
            return
        else:
            self.__router.setRoute(self.__lsm.removeSubtreePrefix(routeInfo.state.getStateID()), routeInfo.params)
            headerType = HeaderType.DEFAULT
            if routeInfo.state.getFlags() & LobbyStateFlags.HANGAR:
                headerType = HeaderType.HANGAR
            with self.getViewModel().transaction() as model:
                model.setType(headerType)
            return
