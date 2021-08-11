# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgnc/image_notification_helper.py
import logging
from adisp import process, async
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.image_helper import getTextureLinkByID
from helpers.CallbackDelayer import CallbackDelayer
from WebBrowser import getWebCache
_logger = logging.getLogger(__name__)

class WebImageHelper(object):
    __slots__ = ('__callbackMethod', '__imageUrl', '__callbackDelayer', '__webCache', '__defLocalDirPath')
    __DEFAULT_TIMEOUT = 10.0

    def __init__(self, defLocalDirPath='notifications'):
        self.__callbackMethod = None
        self.__imageUrl = ''
        self.__callbackDelayer = CallbackDelayer()
        self.__webCache = None
        self.__defLocalDirPath = defLocalDirPath
        return

    @async
    def getLocalPath(self, imageUrl, callback=lambda x: None):
        self.__imageUrl = imageUrl
        self.__callbackMethod = callback
        self.__webCache = getWebCache()
        if self.__webCache is None:
            _logger.error('Failed to get web cache. Using empty image path.')
            self.__callbackDelayer.destroy()
            self.__callMethod('')
            return
        else:
            localPath = self.__webCache.get(self.__imageUrl)
            if localPath is not None:
                _logger.debug('Got image path %s for url %s', localPath, self.__imageUrl)
                self.__callbackDelayer.destroy()
                self.__webCache = None
                self.__callMethod(str(localPath))
                return
            _logger.debug('Failed to get image from web cache by url %s. Downloading initialized.', self.__imageUrl)
            self.__webCache.loadCustomUrls([self.__imageUrl], self.__defLocalDirPath)
            self.__webCache.onDownloadFinished += self.__stop
            self.__callbackDelayer.delayCallback(self.__DEFAULT_TIMEOUT, self.__stop)
            return

    def __stop(self):
        self.__callbackDelayer.destroy()
        self.__webCache.onDownloadFinished -= self.__stop
        localPath = self.__webCache.get(self.__imageUrl) or ''
        _logger.debug('Got image path %s for url %s', localPath, self.__imageUrl)
        self.__webCache = None
        self.__callMethod(str(localPath))
        return

    def __onTimer(self):
        _logger.warning('Web Cache download timed out. Failed to load image from url: %s', self.__imageUrl)
        self.__stop()

    def __callMethod(self, localPath):
        callback = self.__callbackMethod
        self.__callbackMethod = None
        if callback is not None and callable(callback):
            callback(localPath)
        return


@process
def showPaymentMethodLinkNotification(method, imageUrl):
    helper = WebImageHelper()
    localPath = yield helper.getLocalPath(imageUrl)
    SystemMessages.pushMessage(text=backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.titles.paymentMethodLink(), method=method), type=SystemMessages.SM_TYPE.PaymentMethodLinkWgnc, messageData={'imageBlock': _packImageBlock(localPath)})


@process
def showPaymentMethodUnlinkNotification(method, imageUrl):
    helper = WebImageHelper()
    localPath = yield helper.getLocalPath(imageUrl)
    SystemMessages.pushMessage(text=backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.titles.paymentMethodUnlink(), method=method), type=SystemMessages.SM_TYPE.PaymentMethodUnlinkWgnc, messageData={'imageBlock': _packImageBlock(localPath)})


def _packImageBlock(imagePath):
    return '' if not imagePath else "<br/><br/><img src='{path}'/>".format(path=getTextureLinkByID(imagePath))
