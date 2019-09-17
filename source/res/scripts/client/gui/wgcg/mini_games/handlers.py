# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/mini_games/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class FestivalMiniGameRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.FESTIVAL_MINI_GAMES_DATA: self.__getAccountData}
        return handlers

    def __getAccountData(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wotmg', 'account_data'))
