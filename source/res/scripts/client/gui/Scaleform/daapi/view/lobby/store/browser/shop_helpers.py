# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/shop_helpers.py
import typing
from crew2.sandbox import SANDBOX_CONSTANTS
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from helpers import dependency, getLanguageCode
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getUrl(urlName=None, lobbyContext=None):
    if SANDBOX_CONSTANTS.SHOP_PLACEHOLDER_ON:
        return getShopDummyUrl()
    else:
        hostUrl = lobbyContext.getServerSettings().shop.hostUrl
        return hostUrl + ('' if urlName is None else GUI_SETTINGS.shop.get(urlName))


def getShopDummyUrl():
    return 'wotdata://gui/html/shop_dummy/offlinePage.html' if getLanguageCode() == 'ru' else 'wotdata://gui/html/shop_dummy/offlinePage.en.html'


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getBackendUrl(urlName=None, lobbyContext=None):
    backendHostUrl = lobbyContext.getServerSettings().shop.backendHostUrl
    return backendHostUrl + ('' if urlName is None else GUI_SETTINGS.shopBackend.get(urlName))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isSubscriptionEnabled(itemsCache=None):
    return itemsCache.items.stats.isSubscriptionEnabled


def getShopBackendURL():
    return _getBackendUrl()


def getLoginUrl():
    return _getBackendUrl('loginUrl')


def getProductsUrl(productID):
    return '{}/{}'.format(_getBackendUrl('productsUrl'), productID)


def getShopURL():
    return _getUrl()


def getBuyMoreGoldUrl():
    return _getUrl('buyMoreGoldUrl')


def getBuyGoldUrl():
    return _getUrl('buyGoldUrl')


def getBuyPremiumUrl():
    return _getUrl('buyPremiumUrl')


def getBuyPersonalReservesUrl():
    return _getUrl('buyBoosters')


def getBuyCreditsBattleBoostersUrl():
    return _getUrl('buyCreditsBattleBoosters')


def getBuyBonBattleBoostersUrl():
    return _getUrl('buyBonBattleBoosters')


def getBuyEquipmentUrl():
    return _getUrl('buyEquipment')


def getBuyOptionalDevicesUrl():
    return _getUrl('buyOptionalDevices')


def getBuyVehiclesUrl():
    return _getUrl('buyVehiclesUrl')


def getVehicleUrl():
    return _getUrl('buyVehicle')


def getBonsUrl():
    return _getUrl('bonsUrl')


def getBonsDevicesUrl():
    return _getUrl('bonsDevicesUrl')


def getBonsVehiclesUrl():
    return _getUrl('bonsVehiclesUrl')


def getBonsInstructionsUrl():
    return _getUrl('bonsInstructionsUrl')


def getTradeInVehiclesUrl():
    return _getUrl('tradeIn')


def getPersonalTradeInVehiclesUrl():
    return _getUrl('trade_in_personal')


def getTradeOffOverlayUrl():
    return _getUrl('tradeOffOverlay')


def getPersonalTradeOffOverlayUrl():
    return _getUrl('personalTradeOffOverlay')


def getPremiumVehiclesUrl():
    return _getUrl('premiumVehicles')


def getBuyBattlePassUrl():
    return _getUrl('buyBattlePass')


def getBattlePassCoinProductsUrl():
    return _getUrl('bpcoinProducts')


def getBuyCollectibleVehiclesUrl():
    return _getUrl('buyCollectibleVehicle')


def getBlueprintsExchangeUrl():
    return _getUrl('blueprintsExchange')


def getSplitPageUrl(params):
    url = _getUrl('splitUrl')
    return addParamsToUrlQuery(url, params, True)


def getClientControlledCloseCtx():
    return {'browserParams': makeBrowserParams(isCloseBtnVisible=True),
     'forcedSkipEscape': True}
