# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/requester.py
from adisp import adisp_process
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.clientgw.ny_tamagotchi.contexts import NyTamagotchiGetPlayerInfoCtx, NyTamagotchiGetLeaderboardPageCtx, NyTamagotchiGetCurrentStateCtx, NyTamagotchiBuyItemsCtx, NyTamagotchiActivateItemCtx, NyTamagotchiTakeGiftCtx, NyTamagotchiGetPlayerStatsCtx
from helpers import dependency
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.skeletons.new_year import ITamagotchiDataProvider, ITamagotchiWebRequester
from skeletons.gui.web import IWebController

class TamagotchiWebRequester(ITamagotchiWebRequester):
    __slots__ = ()
    _RECALCULATION_CODE = 409
    _webController = dependency.descriptor(IWebController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    @adisp_process
    def requestPlayerInfo(self):
        notRecalc = getNewYearGeneralConfig().getEnableTamagotchiSimulation()
        if not self._dataProvider.isValidConfig or notRecalc:
            result = yield self._webController.sendRequest(ctx=NyTamagotchiGetCurrentStateCtx(notRecalc=notRecalc))
        else:
            result = yield self._webController.sendRequest(ctx=NyTamagotchiGetPlayerInfoCtx())
        if not result.isSuccess():
            LOG_ERROR('[Tamagotchi] Failed to request player info', result.getExtraCode())
            self._dataProvider.playerInfo = None
            return
        else:
            self._dataProvider.config = result.data.get('config')
            self._dataProvider.playerInfo = result.data
            return

    @adisp_process
    def requestLeaderboardPage(self, page=0, isUserPage=False):
        result = yield self._webController.sendRequest(ctx=NyTamagotchiGetLeaderboardPageCtx(page=page, isUserPage=isUserPage))
        if result.isSuccess():
            self._dataProvider.leaderboard = result.data
            return
        else:
            LOG_WARNING('[Tamagotchi] Failed to retrieve leaderboard info', result.getExtraCode())
            self._dataProvider.leaderboard = None
            return

    @adisp_process
    def requestPlayerStats(self):
        result = yield self._webController.sendRequest(ctx=NyTamagotchiGetPlayerStatsCtx())
        if result.isSuccess():
            self._dataProvider.playerStats = result.data
            return
        else:
            LOG_ERROR('[Tamagotchi] Failed to request player stats', result.getExtraCode())
            self._dataProvider.playerStats = None
            return

    @adisp_process
    def buyItems(self, itemsDict):
        result = yield self._webController.sendRequest(ctx=NyTamagotchiBuyItemsCtx(items=itemsDict))
        if not result.isSuccess():
            LOG_ERROR('[Tamagotchi] Failed to buy items', result.getExtraCode())
        self._dataProvider.onItemsPurchased(result.isSuccess(), itemsDict)

    @adisp_process
    def activateItem(self, itemId, count):
        self._dataProvider.onItemsActivateRequested(itemId, count)
        result = yield self._webController.sendRequest(ctx=NyTamagotchiActivateItemCtx(itemId=itemId, count=count))
        if not result.isSuccess():
            LOG_ERROR('[Tamagotchi] Failed to activate items', result.getExtraCode())
        else:
            self._dataProvider.playerInfo = result.data
        self._dataProvider.onItemsActivated(result.isSuccess(), itemId, count, result.getExtraCode() == self._RECALCULATION_CODE)

    @adisp_process
    def takeGift(self):
        initialCount = self._dataProvider.playerInfo.giftCollected
        result = yield self._webController.sendRequest(ctx=NyTamagotchiTakeGiftCtx())
        if not result.isSuccess():
            LOG_ERROR('[Tamagotchi] Failed to obtain gifts', result.getExtraCode())
            count = 0
            isSecret = False
        else:
            count = result.data['count']
            isSecret = result.data['secret']
            self._dataProvider.playerInfo = result.data.get('player_data')
        self._dataProvider.onGiftObtained(result.isSuccess(), initialCount, count, isSecret, result.getExtraCode() == self._RECALCULATION_CODE)
