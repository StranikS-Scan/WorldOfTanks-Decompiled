# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/battle_royale.py
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from web_client_api import w2c, W2CSchema, Field
VALID_BATTLE_ROYALE_PAGES = (BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID, BATTLEROYALE_CONSTS.BATTLE_ROYALE_AWARDS_ID, BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID)

class _OpenBattleRoyaleScheme(W2CSchema):
    page_id = Field(required=True, type=basestring, validator=lambda v, _: v in VALID_BATTLE_ROYALE_PAGES)


class BattleRoyaleWebApiMixin(object):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)

    @w2c(_OpenBattleRoyaleScheme, 'battle_royale_page')
    def openBattleRoyalePage(self, cmd):
        self.__battleRoyale.showBattleRoyalePage(ctx={'selectedItemID': cmd.page_id,
         'showedFromWeb': True})
