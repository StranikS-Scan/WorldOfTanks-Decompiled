# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_shop.py
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.lobby.store.browser import ingameshop_helpers as helpers
from gui.Scaleform.locale.WAITING import WAITING
from gui.game_control.links import URLMacros
from gui.shared import events, g_eventBus
from gui.shared.economics import getGUIPrice
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache

def _getParams(reason, price, itemId=None):
    params = {'reason': reason,
     'goldPrice': price}
    if itemId is not None:
        params['itemId'] = itemId
    return params


def _makeBuyItemUrl(categoryUrl, itemId=None):
    return '{}/items/$PARAMS(web2client_{})'.format(categoryUrl, itemId) if itemId else categoryUrl


class _GoldPurchaseReason(object):
    VEHICLE = 'vehicle'
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
