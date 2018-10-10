# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ranked_battles/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from web_client_api import w2capi, w2c, W2CSchema, webApiCollection
from web_client_api.clans import ClansWebApi
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import NotificationWebApi, ContextMenuWebApi

@w2capi(name='ranked_battles', key='action')
class _RankedBattlesWebApi(object):

    def __init__(self, browserViewContext=None):
        super(_RankedBattlesWebApi, self).__init__()
        self.__browserViewContext = browserViewContext

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, cmd):
        ctx = self.__browserViewContext
        returnAlias = ctx.get('returnAlias', VIEW_ALIAS.LOBBY_HANGAR) if ctx else VIEW_ALIAS.LOBBY_HANGAR
        g_eventBus.handleEvent(events.LoadViewEvent(alias=returnAlias, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
        return {}


def _createRankedBattlesWebApi(ctx=None):

    def _doCreate():
        return _RankedBattlesWebApi(browserViewContext=ctx)

    return _doCreate


def createRankedBattlesWebHandlers(ctx):
    return webApiCollection(ClansWebApi, _createRankedBattlesWebApi(ctx), NotificationWebApi, ContextMenuWebApi, RequestWebApi, SoundWebApi)
