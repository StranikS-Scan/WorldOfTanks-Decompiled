# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/rank/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class RankRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.RANKED_LEAGUE_POSITION: self.__getRankedPosition,
         WebRequestDataType.RANKED_YEAR_POSITION: self.__getRankedYearPosition}
        return handlers

    def __getRankedPosition(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('rblb', 'user_ranked_position'))

    def __getRankedYearPosition(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('rblb', 'user_ranked_year_position'))
