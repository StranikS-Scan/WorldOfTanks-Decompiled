# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/navigation_presenter.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.page.header.navigation_bar_info_button import NavigationBarInfoButton, ButtonType
from gui.impl.gen.view_models.views.lobby.page.header.navigation_bar_model import NavigationBarModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared.utils.callable_delayer import CallableDelayer, delayUntilParentWindowReady
from gui.lobby_state_machine.states import LobbyStateFlags, LobbyStateDescription
from gui.shared.event_dispatcher import showHangar
from helpers.events_handler import EventsHandler
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
_logger = logging.getLogger(__name__)
_NAVIGATION_ACTION_TARGET_KEY = 'name'
_INFO_ACTION_INDEX_KEY = 'index'

class NavigationPresenter(ViewComponent[NavigationBarModel], EventsHandler):
    __DESC_TO_BUTTON_TYPE = {LobbyStateDescription.Info.Type.INFO: ButtonType.INFO,
     LobbyStateDescription.Info.Type.QUESTION: ButtonType.QUESTION,
     LobbyStateDescription.Info.Type.VIDEO: ButtonType.VIDEO}

    def __init__(self):
        super(NavigationPresenter, self).__init__(model=NavigationBarModel)
        self.__callableDelayer = CallableDelayer()
        self.__lsm = None
        self.__visibleState = None
        self.__infoActionHandlers = []
        return

    def _onLoading(self, *args, **kwargs):
        self.__lsm = getLobbyStateMachine()
        super(NavigationPresenter, self)._onLoading(args, kwargs)

    def _finalize(self):
        self.__callableDelayer.clear()
        self.__callableDelayer = None
        super(NavigationPresenter, self)._finalize()
        self.__infoActionHandlers = []
        self.__lsm = None
        return

    def _getEvents(self):
        model = self.getViewModel()
        events = ((model.onNavigate, self.__onNavigate), (model.onInfoAction, self.__onInfoAction))
        if self.__lsm:
            events += ((self.__lsm.onVisibleRouteChanged, self.__routeChanged),)
        return events

    def __routeChanged(self, routeInfo):
        self.__callableDelayer.clear()
        view = self.__lsm.getRelatedView(routeInfo.state)
        delayUntilParentWindowReady(self.__callableDelayer, view, partial(self.__processRouteChange, routeInfo))

    def __processRouteChange(self, routeInfo):
        backNavigationTargetsHangar = bool(routeInfo.visualBackNavigationTarget.getFlags() & LobbyStateFlags.HANGAR)
        self.__infoActionHandlers = []
        if routeInfo.currentDescription is not None:
            self.__infoActionHandlers = [ info.onMoreInfoRequested for info in routeInfo.currentDescription.infos ]
        self.__visibleState = routeInfo.state
        with self.getViewModel().transaction() as model:
            infoButtons = model.getInfoButtons()
            infoButtons.clear()
            if routeInfo.currentDescription is not None:
                model.setPageTitle(routeInfo.currentDescription.title)
                for info in routeInfo.currentDescription.infos:
                    infoButton = NavigationBarInfoButton()
                    infoButton.setType(self.__DESC_TO_BUTTON_TYPE.get(info.type, ButtonType.INFO))
                    infoButton.setLabel(info.label)
                    infoButton.setTooltipHeader(info.tooltipHeader)
                    infoButton.setTooltipBody(info.tooltipBody)
                    infoButtons.addViewModel(infoButton)

            else:
                model.setPageTitle('')
            allowBackNav = not backNavigationTargetsHangar and routeInfo.backDescription is not None
            model.setBackNavigationAllowed(allowBackNav)
            model.setBackNavigationDescription(routeInfo.backDescription or '')
            infoButtons.invalidate()
        return

    def __onNavigate(self, navigationAction):
        target = navigationAction[_NAVIGATION_ACTION_TARGET_KEY]
        if target == NavigationBarModel.BACK_NAVIGATION:
            self.__visibleState.goBack()
        elif target == NavigationBarModel.GARAGE_NAVIGATION:
            showHangar()
        else:
            _logger.warning('Unknown navigation target: %s', target)

    def __onInfoAction(self, infoAction):
        handlerCount = len(self.__infoActionHandlers)
        index = int(infoAction[_INFO_ACTION_INDEX_KEY])
        if handlerCount > index:
            self.__infoActionHandlers[index]()
        else:
            _logger.warning('Requested info action with index %d, but only %d actions exist!', handlerCount, index)
