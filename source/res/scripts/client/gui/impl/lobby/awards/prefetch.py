# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/prefetch.py
import logging
import typing
from adisp import async, process
from gui.impl.lobby.awards import SupportedTokenTypes
from helpers import dependency
from WebBrowser import getWebCache
from gui.impl.lobby.offers import getGfImagePath
from gui.wgnc.image_notification_helper import WebImageHelper
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
_LOCAL_FOLDER_NAME = 'multiple_awards'
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from gui.platform.catalog_service.controller import _PurchaseDescriptor

class _IPrefetcher(object):

    def __init__(self, productID):
        super(_IPrefetcher, self).__init__()
        self._productID = productID

    def prefetch(self, data):
        return True


class TokenDataPrefetcher(_IPrefetcher):
    __purchaseCache = dependency.descriptor(IPurchaseCache)

    @async
    @process
    def prefetch(self, bonus, callback):
        for tID in bonus.getTokens():
            iconSmallPath, iconBigPath = yield self.getImageData(tID)
            if not iconBigPath:
                _logger.warning("Couldn't add token award %s because big image has not been obtained!", tID)
                callback(False)
                return
            if not iconSmallPath:
                _logger.warning("Couldn't add token award %s because small image has not been obtained!", tID)
                callback(False)
                return

        callback(True)

    @async
    @process
    def getImageData(self, tID, callback=None):
        purchase = yield self.__purchaseCache.requestPurchaseByID(self._productID)
        tokenData = purchase.getTokenData(tID)
        iconSmallPath = ''
        if tokenData.imgSmall:
            smallImglocalPath = yield WebImageHelper(_LOCAL_FOLDER_NAME).getLocalPath(tokenData.imgSmall)
            if smallImglocalPath:
                iconSmallPath = getGfImagePath(getWebCache().getRelativeFromAbsolute(smallImglocalPath))
        iconBigPath = ''
        if tokenData.imgBig:
            bigImglocalPath = yield WebImageHelper(_LOCAL_FOLDER_NAME).getLocalPath(tokenData.imgBig)
            if bigImglocalPath:
                iconBigPath = getGfImagePath(getWebCache().getRelativeFromAbsolute(bigImglocalPath))
        callback((iconSmallPath, iconBigPath))


PREFETCHERS = {SupportedTokenTypes.BATTLE_TOKEN: TokenDataPrefetcher,
 SupportedTokenTypes.TOKENS: TokenDataPrefetcher,
 SupportedTokenTypes.PROGRESSION_XP_TOKEN: TokenDataPrefetcher}
