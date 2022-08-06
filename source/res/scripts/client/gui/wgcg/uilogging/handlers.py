# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/uilogging/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class UILoggingRequestHandlers(RequestHandlers):

    def get(self):
        return {WebRequestDataType.UI_LOGGING_SESSION: self.__getSession}

    def __getSession(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('uilogging', 'get_uilogging_session'))
