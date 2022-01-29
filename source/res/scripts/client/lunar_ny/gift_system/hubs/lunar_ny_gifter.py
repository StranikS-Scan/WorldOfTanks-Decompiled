# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/gift_system/hubs/lunar_ny_gifter.py
from adisp import process, async
from gui.gift_system.constants import RANDOM_RECEIVER_ID, GifterResponseState, AccountErrorResponseTitle
from gui.gift_system.hubs.base.gifter import GiftEventBaseGifter
from gui.wgcg.gift_system.contexts import GiftSystemSendGiftToRandomUserCtx, GiftSystemSendGiftCtx

class LunarNYGifter(GiftEventBaseGifter):

    @async
    @process
    def sendGift(self, entitlementCode, receiverID, metaInfo, callback=None):
        if receiverID == RANDOM_RECEIVER_ID:
            requestCtx = GiftSystemSendGiftToRandomUserCtx(entitlementCode, metaInfo)
        else:
            requestCtx = GiftSystemSendGiftCtx(entitlementCode, receiverID, metaInfo)
        responseData = yield self._doExternalRequest(requestCtx)
        if callback is not None:
            callback(responseData)
        return

    def _getWebResultState(self, result):
        if result.isSuccess():
            return GifterResponseState.WEB_SUCCESS
        else:
            return GifterResponseState.WEB_ACCOUNT_FAILURE if result.data is not None and result.data.get('title', '') in AccountErrorResponseTitle.getAllValues() else GifterResponseState.WEB_FAILURE
