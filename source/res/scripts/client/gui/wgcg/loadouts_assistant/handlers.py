# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/loadouts_assistant/handlers.py
from typing import Callable
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.loadouts_assistant.context import LoadoutsAssistantCtx
from gui.wgcg.settings import WebRequestDataType

class LoadoutsAssistantRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.WOTLDA_GET_LOADOUTS: self.__getLoadouts}
        return handlers

    def __getLoadouts(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('loadouts_assistant', 'get_loadouts'), ctx.getClientCacheUpdatedAt(), ctx.getLoadoutTypes())
