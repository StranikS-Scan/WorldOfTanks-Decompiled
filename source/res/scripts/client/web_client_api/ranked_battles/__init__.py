# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ranked_battles/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from web_client_api import w2capi, w2c, W2CSchema, webApiCollection, Field
from web_client_api.clans import ClansWebApi
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import NotificationWebApi, ContextMenuWebApi, OpenWindowWebApi, CloseWindowWebApi
VALID_RANKED_PAGES = (RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID)

class _OpenRankedBattlesScheme(W2CSchema):
    pageId = Field(required=True, type=basestring, validator=lambda v, _: v in VALID_RANKED_PAGES)


@w2capi(name='ranked_battles', key='action')
class RankedBattlesWebApi(object):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, browserViewContext=None):
        super(RankedBattlesWebApi, self).__init__()
        self.__browserViewContext = browserViewContext

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, cmd):
        ctx = self.__browserViewContext
        returnAlias = ctx.get('returnAlias', VIEW_ALIAS.LOBBY_HANGAR) if ctx else VIEW_ALIAS.LOBBY_HANGAR
        g_eventBus.handleEvent(events.LoadViewEvent(alias=returnAlias, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
        return {}

    @w2c(_OpenRankedBattlesScheme, name='open_ranked_page')
    def openRankedPage(self, cmd):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': cmd.pageId,
         'showedFromWeb': True})


def _createRankedBattlesWebApi(ctx=None):

    def _doCreate():
        return RankedBattlesWebApi(browserViewContext=ctx)

    return _doCreate


def createRankedBattlesWebHandlers(ctx):
    return webApiCollection(ClansWebApi, _createRankedBattlesWebApi(ctx), NotificationWebApi, ContextMenuWebApi, RequestWebApi, OpenWindowWebApi, CloseWindowWebApi, SoundWebApi)
