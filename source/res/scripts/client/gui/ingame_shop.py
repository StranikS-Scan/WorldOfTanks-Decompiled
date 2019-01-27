# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_shop.py
import logging
import json
import urllib2
import uuid
from adisp import async, process
from constants import RentType, GameSeasonType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.lobby.store.browser import ingameshop_helpers as helpers
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getLoginUrl, getProductsUrl
from gui.Scaleform.locale.WAITING import WAITING
from gui.game_control.links import URLMacros
from gui.shared import events, g_eventBus
from gui.shared.economics import getGUIPrice
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.shared.utils import decorators
from helpers import dependency, getClientLanguage
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
_logger = logging.getLogger(__name__)
SHOP_RENT_TYPE_MAP = {RentType.NO_RENT: 'none',
 RentType.TIME_RENT: 'time',
 RentType.BATTLES_RENT: 'battles',
 RentType.WINS_RENT: 'wins',
 RentType.SEASON_RENT: 'season',
 RentType.SEASON_CYCLE_RENT: 'cycle'}
SHOP_RENT_SEASON_TYPE_MAP = {GameSeasonType.NONE: 'none',
 GameSeasonType.RANKED: 'ranked',
 GameSeasonType.EPIC: 'frontline'}

def generateShopRentRenewProductID(intCD, rentType, num=0, seasonType=GameSeasonType.NONE):
    rentType = SHOP_RENT_TYPE_MAP[rentType]
    seasonType = SHOP_RENT_SEASON_TYPE_MAP[seasonType]
    return '{seasonType}_{intCD}_{type}_{num}_renew'.format(seasonType=str(seasonType) or 'none', intCD=str(intCD), type=rentType, num=str(num))


class _GoldPurchaseReason(object):
    VEHICLE = 'vehicle'
    RENT = 'rent'
    XP = 'experience'
    SLOT = 'slot'
    BERTH = 'barracks'
    CREW = 'crew'
    EQUIPMENT = 'equipment'
    CUSTOMIZATION = 'customization'
    BUNDLE = 'bundle'


class Source(object):
    EXTERNAL = 'external'


class Origin(object):
    STORAGE = 'storage'


def _getParams(reason, price, itemId=None):
    params = {'reason': reason,
     'goldPrice': price,
     'source': Source.EXTERNAL}
    if itemId is not None:
        params['itemId'] = itemId
    return params


def _makeBuyItemUrl(categoryUrl, itemId=None):
    return '{}/items/$PARAMS(web2client_{})'.format(categoryUrl, itemId) if itemId else categoryUrl


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def canBuyGoldForItemThroughWeb(itemID, itemsCache=None):
    item = itemsCache.items.getItemByCD(itemID)
    return canBuyGoldForVehicleThroughWeb(item) if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else False


@dependency.replace_none_kwargs(itemsCache=IItemsCache, tradeIn=ITradeInController)
def canBuyGoldForVehicleThroughWeb(vehicle, itemsCache=None, tradeIn=None):
    if helpers.isIngameShopEnabled() and vehicle.isUnlocked:
        money = itemsCache.items.stats.money
        money = tradeIn.addTradeInPriceIfNeeded(vehicle, money)
        exchangeRate = itemsCache.items.shop.exchangeRate
        price = getGUIPrice(vehicle, money, exchangeRate)
        currency = price.getCurrency(byWeight=True)
        mayObtainForMoney = vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
        isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
        if currency == Currency.GOLD:
            if not mayObtainForMoney:
                if isBuyingAvailable:
                    return True
    return False


def showBuyBoosterOverlay(itemId, source=None, origin=None):
    _showBuyItemWebOverlay(helpers.getBuyBoostersUrl(), itemId, source, origin)


def showBuyBattleBoosterOverlay(itemId, source=None, origin=None):
    _showBuyItemWebOverlay(helpers.getBuyBattleBoostersUrl(), itemId, source, origin)


def showBuyEquipmentOverlay(itemId, source=None, origin=None):
    _showBuyItemWebOverlay(helpers.getBuyEquipmentUrl(), itemId, source, origin)


def showBuyOptionalDeviceOverlay(itemId, source=None, origin=None):
    _showBuyItemWebOverlay(helpers.getBuyOptionalDevicesUrl(), itemId, source, origin)


def showBuyGoldForVehicleWebOverlay(fullPrice, intCD):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.VEHICLE, fullPrice, intCD))


def showBuyGoldForRentWebOverlay(fullPrice, intCD):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.RENT, fullPrice, intCD))


def showBuyGoldForXpWebOverlay(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.XP, fullPrice))


def showBuyGoldForSlot(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.SLOT, fullPrice))


def showBuyGoldForBerth(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.BERTH, fullPrice))


def showBuyGoldForCrew(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.CREW, fullPrice))


def showBuyGoldForEquipment(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.EQUIPMENT, fullPrice))


def showBuyGoldForCustomization(fullPrice):
    showBuyGoldWebOverlay(_getParams(_GoldPurchaseReason.CUSTOMIZATION, fullPrice))


def showBuyGoldForBundle(fullPrice, params=None):
    params = dict(params) or {}
    params.update(_getParams(_GoldPurchaseReason.BUNDLE, fullPrice))
    showBuyGoldWebOverlay(params)


@process
def _showBuyItemWebOverlay(url, itemId, source=None, origin=None):
    url = yield URLMacros().parse(url)
    params = {}
    if source:
        params['source'] = source
    if origin:
        params['origin'] = origin
    url = yield URLMacros().parse(url=_makeBuyItemUrl(url, itemId), params=params)
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.OVERLAY_WEB_STORE, ctx={'url': url}), EVENT_BUS_SCOPE.LOBBY)


@process
def showBuyGoldWebOverlay(params=None):
    url = helpers.getBuyMoreGoldUrl()
    if url:
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.OVERLAY_WEB_STORE, ctx={'url': url}), EVENT_BUS_SCOPE.LOBBY)


@process
def showBuyVehicleOverlay(params=None):
    url = helpers.getVehicleUrl()
    if url:
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.OVERLAY_WEB_STORE, ctx={'url': url,
         'browserParams': makeBrowserParams(WAITING.BUYITEM, True)}), EVENT_BUS_SCOPE.LOBBY)


@async
@decorators.process('loadingData')
@dependency.replace_none_kwargs(webCtrl=IWebController)
def getShopProductInfo(productID, callback=None, webCtrl=None):
    productInfo = {}
    accessTokenData = yield webCtrl.getAccessTokenData(force=False)
    if accessTokenData is not None:
        loginUrl = yield URLMacros().parse(url=getLoginUrl())
        authRequest = urllib2.Request(url=loginUrl, data='')
        authHeader = {'key': 'AUTHORIZATION',
         'val': 'Basic {}'.format(str(accessTokenData.accessToken))}
        authRequest.add_header(**authHeader)
        try:
            authResponse = urllib2.urlopen(authRequest)
            cookie = authResponse.headers.get('Set-Cookie')
            productsUrl = yield URLMacros().parse(url=getProductsUrl())
            productUrl = '{}/{}'.format(productsUrl, productID)
            productRequest = urllib2.Request(productUrl)
            productRequest.add_header(**authHeader)
            productRequest.add_header('cookie', cookie)
            productRequest.add_header('ACCEPT-LANGUAGE', getClientLanguage())
            productResponse = urllib2.urlopen(productRequest)
            productInfo = json.load(productResponse)
        except urllib2.HTTPError as e:
            _logger.debug('%s: %s', e, e.url)

    if callback:
        callback(productInfo)
    return


def makeBuyParamsByProductInfo(productInfo):
    data = productInfo['data']
    priceSection = data['price']
    buySection = data['links']['buy']
    return {'transactionID': str(uuid.uuid4()),
     'priceCode': priceSection['currency'],
     'priceAmount': int(priceSection['value']),
     'buyLinkHref': buySection['href'],
     'buyLinkMethod': buySection['method']}
