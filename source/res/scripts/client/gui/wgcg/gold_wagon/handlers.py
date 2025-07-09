# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/gold_wagon/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class GoldWagonRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.GOLD_WAGON_INFO: self.__fetchGoldWagonInfo}
        return handlers

    def __fetchGoldWagonInfo(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('gold_wagon_info', 'gold_wagon_fetch_info'))
        return reqCtx
