# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ranked_battles/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2capi, w2c, W2CSchema, webApiCollection, Field
from web.web_client_api.clans import ClansWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi
from web.web_client_api.ui import NotificationWebApi, ContextMenuWebApi, OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi
VALID_RANKED_PAGES = (RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID)

class _OpenRankedBattlesScheme(W2CSchema):
    pageId = Field(required=True, type=basestring, validator=lambda v, _: v in VALID_RANKED_PAGES)
    pageParams = Field(required=False, type=basestring, default='')


@w2capi(name='ranked_battles', key='action')
class RankedBattlesWebApi(object):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(W2CSchema, name='close_browser')
    def closeBrowser(self, cmd):
        g_eventBus.handleEvent(events.LoadViewEvent(alias=VIEW_ALIAS.LOBBY_HANGAR), EVENT_BUS_SCOPE.LOBBY)

    @w2c(_OpenRankedBattlesScheme, name='open_ranked_page')
    def openRankedPage(self, cmd):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': cmd.pageId,
         'showedFromWeb': True,
         'webParams': cmd.pageParams})


def createRankedBattlesWebHandlers():
    return webApiCollection(ClansWebApi, RankedBattlesWebApi, NotificationWebApi, ContextMenuWebApi, RequestWebApi, OpenTabWebApi, OpenWindowWebApi, CloseWindowWebApi, SoundWebApi, SoundStateWebApi)
