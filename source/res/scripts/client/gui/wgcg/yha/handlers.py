# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/yha/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class YhaRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.YHA_VIDEO: self.__getYhaVideo}
        return handlers

    def __getYhaVideo(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('yha', 'get_yha_video'))
