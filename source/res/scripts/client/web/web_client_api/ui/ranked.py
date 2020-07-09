# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/ranked.py
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from web.web_client_api import w2c, W2CSchema, Field
VALID_RANKED_PAGES = (RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_REWARDS_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_SHOP_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID,
 RANKEDBATTLES_CONSTS.RANKED_BATTLES_INFO_ID)

class _OpenRankedBattlesScheme(W2CSchema):
    pageId = Field(required=True, type=basestring, validator=lambda v, _: v in VALID_RANKED_PAGES)
    pageParams = Field(required=False, type=basestring, default='')


class _OpenBrowserOverlaySchema(W2CSchema):
    url = Field(required=True, type=basestring)


class OpenRankedPagesMixin(object):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @w2c(_OpenRankedBattlesScheme, name='open_ranked_page')
    def openRankedPage(self, cmd):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': cmd.pageId,
         'showedFromWeb': True,
         'webParams': cmd.pageParams})

    @w2c(_OpenBrowserOverlaySchema, name='open_ranked_overlay')
    def openRankedOverlay(self, cmd):
        showBrowserOverlayView(cmd.url, alias=RANKEDBATTLES_ALIASES.RANKED_WEB_OVERLAY, forcedSkipEscape=True)
