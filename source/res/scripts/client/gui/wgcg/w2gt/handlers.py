# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/w2gt/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class W2gtRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.W2GT_DATA: self.__getTips}
        return handlers

    def __getTips(self, ctx, callback):
        descriptor = 'w2gt'
        accessorMethod = 'get_w2gt_tips'
        return self._requester.doRequestEx(ctx, callback, (descriptor, accessorMethod), ctx.getHeaders(), ctx.getParams())
