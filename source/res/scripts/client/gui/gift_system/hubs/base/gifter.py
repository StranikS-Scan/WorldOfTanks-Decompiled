# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/base/gifter.py
import typing
from account_helpers import isLongDisconnectedFromCenter
from adisp import async, process
from gui.gift_system.constants import GifterResponseState
from gui.gift_system.hubs.subsystems import BaseHubSubsystem
from gui.wgcg.gift_system.contexts import GiftSystemSendGiftCtx
from helpers import dependency
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from helpers.server_settings import GiftEventConfig

class IGiftEventGifter(BaseHubSubsystem):

    def getActiveRequest(self):
        raise NotImplementedError

    def getRequestRestriction(self):
        raise NotImplementedError

    @async
    @process
    def sendGift(self, entitlementCode, receiverID, metaInfo, callback):
        raise NotImplementedError


class GiftEventBaseGifter(IGiftEventGifter):
    __slots__ = ('__requestCtx', '__responseCallback')
    __webController = dependency.descriptor(IWebController)

    def __init__(self, eventSettings, responseCallback):
        super(GiftEventBaseGifter, self).__init__(eventSettings)
        self.__responseCallback = responseCallback
        self.__requestCtx = None
        return

    def destroy(self):
        self.__responseCallback = None
        super(GiftEventBaseGifter, self).destroy()
        return

    def getActiveRequest(self):
        return self.__requestCtx

    def getRequestRestriction(self):
        if not self._isRequestsEnabled():
            return GifterResponseState.REQUESTS_DISABLED
        elif isLongDisconnectedFromCenter():
            return GifterResponseState.CENTER_DISCONNECTED
        elif not self.__webController.isAvailable():
            return GifterResponseState.WGCG_NOT_AVAILABLE
        else:
            return GifterResponseState.REQUEST_IN_PROGRESS if self.__requestCtx is not None else None

    @async
    @process
    def sendGift(self, entitlementCode, receiverID, metaInfo, callback=None):
        requestCtx = GiftSystemSendGiftCtx(entitlementCode, receiverID, metaInfo)
        responseData = yield self._doExternalRequest(requestCtx)
        if callback is not None:
            callback(responseData)
        return

    def _isRequestsEnabled(self):
        return self._settings.isEnabled

    def _getWebResultState(self, result):
        return GifterResponseState.WEB_SUCCESS if result.isSuccess() else GifterResponseState.WEB_FAILURE

    @async
    @process
    def _doExternalRequest(self, requestCtx, callback):
        clientRestriction = self.getRequestRestriction()
        if clientRestriction is not None:
            callback(requestCtx.getDataObj(clientRestriction))
            return
        else:
            self.__requestCtx = requestCtx
            result = yield self.__webController.sendRequest(requestCtx)
            resultState = self._getWebResultState(result)
            resultData = requestCtx.getDataObj(resultState, result.data)
            self.__requestCtx = None
            callback(resultData)
            if self.__responseCallback is not None:
                self.__responseCallback(resultData)
            return
