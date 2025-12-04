# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/ny_tamagotchi/handlers.py
from gui.clientgw.base.handlers import RequestHandlers
from gui.clientgw.settings import WebRequestDataType

class NyTamagotchiRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.NY_TAMAGOTCHI_CURRENT_STATE: self.__getCurrentState,
         WebRequestDataType.NY_TAMAGOTCHI_PLAYER_INFO: self.__getPlayerInfo,
         WebRequestDataType.NY_TAMAGOTCHI_PLAYER_STATS: self.__getPlayerStats,
         WebRequestDataType.NY_TAMAGOTCHI_LEADERBOARD_PAGE: self.__getLeaderboardPage,
         WebRequestDataType.NY_TAMAGOTCHI_TAKE_GIFT: self.__takeGift,
         WebRequestDataType.NY_TAMAGOTCHI_BUY_ITEMS: self.__buyItems,
         WebRequestDataType.NY_TAMAGOTCHI_ACTIVATE_ITEMS: self.__activateItems}
        return handlers

    def __getCurrentState(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'get_current_state'), notRecalc=ctx.notRecalc)

    def __getPlayerInfo(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'get_player_info'))

    def __getPlayerStats(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'get_player_stats'))

    def __getLeaderboardPage(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'get_leaderboard_page'), page=ctx.page, isUserPage=ctx.isUserPage)

    def __takeGift(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'take_gift'))

    def __buyItems(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'buy_items'), data=ctx.getData())

    def __activateItems(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('ny_tamagotchi', 'activate_items'), data=ctx.getData())
