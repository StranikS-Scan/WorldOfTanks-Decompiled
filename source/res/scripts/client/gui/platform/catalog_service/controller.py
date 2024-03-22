# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/catalog_service/controller.py
import json
import logging
from collections import namedtuple
import BigWorld
import adisp
from gui.macroses import getLanguageCode
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.lobby_context import ILobbyContext
from web.cache.web_downloader import WebDownloader
_logger = logging.getLogger(__name__)
_DEFAULT_SYNC_TIMEOUT = 180
_WORKERS_LIMIT = 2
TOKEN_ENTITLEMENT_PREFIX = 'token_'
_TokenDescriptor = namedtuple('_TokenDescriptor', 'imgSmall, imgBig, title, description')
_DisplayWays = namedtuple('_DisplayWays', 'showNotification, showAwardScreen')

def _getEmptyDescriptor():
    return _PurchaseDescriptor()


class _ProductExtraData(object):
    _MAX_ORDER_INDEX = 10000
    _SPECIAL_CURRENCIES = {'free_xp': 'freeXP',
     'equip_coin': 'equipCoin'}
    _EXTRA_ENTITLEMENTS = ('premium_plus',)

    def __init__(self, entitlements=None, currencies=None):
        super(_ProductExtraData, self).__init__()
        self.__items = []
        if currencies:
            for currency in currencies:
                entCode = self.__getField(currency, 'code', '')
                entOrder = self.__getField(currency, 'order', self._MAX_ORDER_INDEX)
                if entCode:
                    if entCode in Currency.ALL:
                        self.__addItem(entOrder, {entCode: self.__getField(currency, 'amount', 0)})
                    elif entCode in self._SPECIAL_CURRENCIES:
                        expectedInGUI = self._SPECIAL_CURRENCIES[entCode]
                        self.__addItem(entOrder, {expectedInGUI: self.__getField(currency, 'amount', 0)})
                    else:
                        _logger.warning('Unsupported currency format: %s', entCode)

        if entitlements:
            for eItem in entitlements:
                entCode = self.__getField(eItem, 'code', '')
                entOrder = self.__getField(eItem, 'order', self._MAX_ORDER_INDEX)
                if entCode in self._EXTRA_ENTITLEMENTS:
                    self.__addItem(entOrder, {entCode: self.__getField(eItem, 'amount', 0)})

    def iterItems(self):
        for i in self.__items:
            yield i

    def __addItem(self, incomeOrder, incomeItem):
        incomeOrder = incomeOrder - 1
        i = 0
        for sItem in self.__items:
            if sItem[0] > incomeOrder:
                break
            i = i + 1

        self.__items.insert(i, (incomeOrder, incomeItem))

    def __getField(self, target, key, default):
        value = target.get(key, None)
        if value is not None:
            return value
        else:
            _logger.warning("Couldn't find field '%s' in %s", key, target)
            return default


class _PurchaseDescriptor(object):
    __slots__ = ('__entitlements', '__metadataWot', '__currencies', '__isEntitlementsInvalid', '__tokens', '__titleID', '__productExtraData', '__iconID', '__productName', '__mainAmount', '__displayWays')

    def __init__(self, entitlements=None, currencies=None, metadataWot=None):
        super(_PurchaseDescriptor, self).__init__()
        self.__isEntitlementsInvalid = not bool(entitlements) or not bool(metadataWot)
        self.__entitlements = entitlements if entitlements is not None else []
        self.__metadataWot = metadataWot if metadataWot is not None else {}
        self.__currencies = currencies
        self.__titleID = self.__getMetadataValueByName('title', '')
        self.__productName = self.__getMetadataValueByName('name', '')
        self.__iconID = self.__getMetadataValueByName('icon', '')
        self.__mainAmount = self.__getMetadataValueByName('main', 0)
        self.__productExtraData = _ProductExtraData(entitlements, currencies)
        self.__tokens = {}
        self.__displayWays = self.__getMetadataDisplayWays()
        return

    def destroy(self):
        self.__productExtraData = None
        self.__entitlements = None
        self.__currencies = None
        self.__metadataWot = None
        self.__displayWays = None
        self.__tokens = None
        return

    def getDisplayWays(self):
        return self.__displayWays

    def getExtraData(self):
        return self.__productExtraData

    def getProductName(self):
        return self.__productName

    def getIconID(self):
        return self.__iconID

    def getTitleID(self):
        return self.__titleID

    def getMainAmount(self):
        return self.__mainAmount

    def getEntitlements(self):
        return self.__entitlements

    def getTokenData(self, tID):
        if not self.__isEntitlementsInvalid:
            if tID not in self.__tokens:
                imgSmall = ''
                imgBig = ''
                title = ''
                description = ''
                for entitlement in self.__entitlements:
                    entCode = entitlement.get('code', '')
                    if entCode.startswith(TOKEN_ENTITLEMENT_PREFIX):
                        if entCode[len(TOKEN_ENTITLEMENT_PREFIX):] == tID:
                            dataIndex = entitlement.get('order', 1) - 1
                            metadataPrefix = 'entitlements_{}'.format(dataIndex)
                            title = self.__getMetadataValueByName('{}_title'.format(metadataPrefix))
                            description = self.__getMetadataValueByName('{}_description'.format(metadataPrefix))
                            imgBig = self.__extractValue(self.__metadataWot.get('{}_image_large'.format(metadataPrefix), {}).get('data', {}).get('url', {}))
                            imgSmall = self.__extractValue(self.__metadataWot.get('{}_icon_url_big'.format(metadataPrefix), {}).get('data', {}).get('url', {}))

                self.__tokens[tID] = _TokenDescriptor(imgSmall, imgBig, title, description)
            return self.__tokens[tID]
        return _TokenDescriptor('', '', '', '')

    def __getMetadataValueByName(self, name, default=None):
        return self.__getDataValueByName(name, self.__metadataWot, default)

    def __getDataValueByName(self, name, targetSection, default=None):
        if not targetSection:
            _logger.warning('Provided section for obtaining %s is empty!', name)
            return default
        value = default
        if name in targetSection:
            dataSection = targetSection.get(name, {}).get('data', {})
            if not dataSection:
                _logger.warning('"%s" has no "data" attribute inside!', name)
            elif isinstance(dataSection, dict):
                value = self.__extractValue(dataSection)
            else:
                value = dataSection
        if not value:
            _logger.warning('Could not obtain "%s" property from provided section!', name)
        return value

    def __extractValue(self, section):
        value = section.get(getLanguageCode())
        if not value:
            value = section.get('value')
        return value

    def __getMetadataDisplayWays(self):
        params = self.__metadataWot.get('params', {})
        return _DisplayWays(params.get('show_nc', False), params.get('show_award', False))


class _PurchasePackage(object):

    def __init__(self, descriptorURL):
        super(_PurchasePackage, self).__init__()
        self.__descriptorUrl = descriptorURL
        self.__descriptor = None
        self.__downloader = None
        self.__pendingCallbacks = []
        self.__timeoutBwCbId = None
        return

    def requestDescriptor(self, callback, timeout=_DEFAULT_SYNC_TIMEOUT):
        if self.__descriptor is None:
            self.__pendingCallbacks.append(callback)
            if not self.__downloader:
                if timeout <= 0:
                    _logger.warning('Cache wrong sync timeout: %s. Using default: %s, URL=%s', timeout, _DEFAULT_SYNC_TIMEOUT, self.__descriptorUrl)
                    timeout = _DEFAULT_SYNC_TIMEOUT
                self.__timeoutBwCbId = BigWorld.callback(timeout, self.__onTimeout)
                self.__downloader = WebDownloader(_WORKERS_LIMIT)
                self.__downloader.download(self.__descriptorUrl, self.__onDescriptorLoaded)
        else:
            callback(self.__descriptor or _getEmptyDescriptor())
        return

    def getDescriptor(self):
        return self.__descriptor

    def destroy(self):
        self.__clearDownloader()
        self.__clearTimeoutBwCbId()
        self.__pendingCallbacks = None
        if self.__descriptor:
            self.__descriptor.destroy()
        return

    def _initDescriptor(self, dataDict):
        metadataWot = dataDict.get('metadata', {}).get('wot')
        if not metadataWot:
            _logger.error('Could not find "metadata/wot" section in the obtained product descriptor!')
        entitlements = dataDict.get('entitlements')
        if not entitlements:
            _logger.error('Could not find "entitlements" section in the obtained product descriptor!')
        return _PurchaseDescriptor(entitlements, dataDict.get('currencies'), metadataWot)

    def __onDescriptorLoaded(self, url, data):
        descrData = None
        _logger.info('Descriptor is downloaded: %s', self.__descriptorUrl)
        try:
            descrData = json.loads(data)
        except StandardError:
            _logger.error('Could not parse descriptor data')

        if descrData:
            self.__descriptor = self._initDescriptor(descrData)
        self.__clearDownloader()
        self.__clearTimeoutBwCbId()
        self.__notifyListeners()
        return

    def __notifyListeners(self):
        descr = self.__descriptor or _getEmptyDescriptor()
        for cb in self.__pendingCallbacks:
            cb(descr)

        self.__pendingCallbacks = []

    def __onTimeout(self):
        _logger.warning('Request failed by timeout, URL=%s', self.__descriptorUrl)
        self.__timeoutBwCbId = None
        self.__clearDownloader()
        self.__notifyListeners()
        return

    def __clearDownloader(self):
        if self.__downloader:
            self.__downloader.close()
            self.__downloader = None
        return

    def __clearTimeoutBwCbId(self):
        if self.__timeoutBwCbId is not None:
            BigWorld.cancelCallback(self.__timeoutBwCbId)
        self.__timeoutBwCbId = None
        return


class PurchaseCache(IPurchaseCache):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(PurchaseCache, self).__init__()
        self.__purchaseById = None
        return

    def init(self):
        self.__purchaseById = {}

    def fini(self):
        for k, purchasePackage in self.__purchaseById.items():
            purchasePackage.destroy()
            del k

    @adisp.adisp_async
    def requestPurchaseByID(self, productCode, callback=None):
        if productCode:
            pUrl = self.__constructFullUrl(productCode)
            if pUrl is None:
                _logger.error('Could not construct proper URL!')
                callback(_getEmptyDescriptor())
            else:
                if productCode not in self.__purchaseById:
                    self.__purchaseById[productCode] = _PurchasePackage(pUrl)
                self.__purchaseById[productCode].requestDescriptor(callback)
        else:
            _logger.error('Invalid product id provided!')
            callback(_getEmptyDescriptor())
        return

    def getCachedPurchase(self, productCode):
        descr = None
        if productCode and productCode in self.__purchaseById:
            descr = self.__purchaseById[productCode].getDescriptor()
        if descr is None:
            _logger.warning('Cached purchase has not been found, try to request this data first. URL=%s', productCode)
        return descr or _getEmptyDescriptor()

    def getProductCode(self, metaData):
        if metaData:
            productUrl = metaData.get('product_id')
            if productUrl:
                return productUrl
            _logger.error('Could not find product_code in meta section of invoice!')
        return None

    def canBeRequestedFromProduct(self, data):
        metaSection = data.get('meta', {})
        return 'scenario' in metaSection.get('tags', []) if metaSection else False

    def __constructFullUrl(self, productCode):
        urlTemplate = self.__lobbyContext.getServerSettings().productCatalog.url
        if urlTemplate:
            return urlTemplate.format(id=productCode, language=getLanguageCode())
        else:
            _logger.error("Couldn't get productCatalog.url from the server settings")
            return None
