# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/shop_helpers.py
import typing
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from helpers import dependency
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getUrl(urlName=None, lobbyContext=None):
    hostUrl = lobbyContext.getServerSettings().shop.hostUrl
    return hostUrl + ('' if urlName is None else GUI_SETTINGS.shop.get(urlName))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isSubscriptionEnabled(itemsCache=None):
    return itemsCache.items.stats.isSubscriptionEnabled


def getShopURL():
    return _getUrl()


def getShopRootUrl():
    return _getUrl('shopRootUrl')


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


def getBuyProductUrl():
    return _getUrl('buyProduct')


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


def getTradeOffOverlayUrl():
    return _getUrl('tradeOffOverlay')


def getPremiumVehiclesUrl():
    return _getUrl('premiumVehicles')


def getBuyBattlePassUrl():
    return _getUrl('buyBattlePass')


def getBattlePassCoinProductsUrl():
    return _getUrl('bpcoinProducts')


def getBattlePassPointsProductsUrl():
    return _getUrl('bpProducts')


def getBuyCollectibleVehiclesUrl():
    return _getUrl('buyCollectibleVehicle')


def getBlueprintsExchangeUrl():
    return _getUrl('blueprintsExchange')


def getPlayerSeniorityAwardsUrl():
    return _getUrl('seniorityAwardsProducts')


def getSplitPageUrl(params):
    url = _getUrl('splitUrl')
    return addParamsToUrlQuery(url, params, True)


def getRentVehicleUrl():
    return _getUrl('rentVehicle')


def getTelecomRentVehicleUrl():
    return _getUrl('telecomTankRental')


def getWotPlusShopUrl():
    return _getUrl('buyWotPlus')


def getIntegratedAuctionUrl():
    return _getUrl('integratedAuction')


def getEventLootBoxesUrl():
    return _getUrl('eventLootboxes')


def getShowcaseUrl():
    return _getUrl('showcase')


def getClientControlledCloseCtx():
    return {'browserParams': makeBrowserParams(isCloseBtnVisible=True),
     'forcedSkipEscape': True}


def getSteelHunterProductsUrl():
    return _getUrl('shProducts')
