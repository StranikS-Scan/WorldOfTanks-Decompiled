# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/live_ops_web_events/browser_view.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.Scaleform.daapi.view.meta.LiveOpsWebEventsViewMeta import LiveOpsWebEventsViewMeta
from helpers import dependency
from skeletons.gui.game_control import ILiveOpsWebEventsController
from skeletons.gui.server_events import IEventsCache
from web.web_client_api import webApiCollection
from web.web_client_api.request import RequestWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi

def createWebHandlers():
    return webApiCollection(CloseWindowWebApi, RequestWebApi, UtilWebApi)


class LiveOpsWebEventsInjectView(InjectComponentAdaptor, LiveOpsWebEventsViewMeta):

    @staticmethod
    def markVisited():
        dependency.instance(IEventsCache).onEventsVisited()

    def _makeInjectView(self):
        return LiveOpsWebEventsBrowserView()


class LiveOpsWebEventsBrowserView(BrowserView):
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)

    def __init__(self):
        super(LiveOpsWebEventsBrowserView, self).__init__(R.views.lobby.common.BrowserView(), settings=makeSettings(url=self.__liveOpsWebEventsController.eventUrl, webHandlers=createWebHandlers(), viewFlags=ViewFlags.VIEW, returnClb=self.__returnCallback))

    def _onLoading(self, *args, **kwargs):
        super(LiveOpsWebEventsBrowserView, self)._onLoading(*args, **kwargs)
        self.__markVisited()

    def __markVisited(self):
        self.__liveOpsWebEventsController.markEventTabVisited()

    @staticmethod
    def __returnCallback(*args, **kwargs):
        if kwargs.pop('forceClosed', False):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)
