# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/gift_system/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class GiftSystemRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.GIFT_SYSTEM_STATE: self.__getGiftSystemState,
         WebRequestDataType.GIFT_SYSTEM_POST_GIFT: self.__postGiftSystemGift,
         WebRequestDataType.GIFT_SYSTEM_SECRET_SANTA_POST: self.__postSecretSanta}
        return handlers

    def __getGiftSystemState(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('gifts', 'get_gift_system_state'), ctx.getReqEventIds())

    def __postGiftSystemGift(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('gifts', 'post_gift_system_gift'), ctx.getEntitlementCode(), ctx.getReceiverID(), ctx.getMetaInfo())

    def __postSecretSanta(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('gifts', 'post_secret_santa_gift'), ctx.getEntitlementCode(), ctx.getMetaInfo())
