# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ItemRestore.py
from items.item_price import getComponentSellPrice, getOptionalDeviceRemovalCost

class RESTORE_VEHICLE_TYPE:
    PREMIUM = 0
    ACTION = 1


class RESTORE_OPT_DEV_REASON:
    SELL_FROM_VEHICLE = 0
    SELL_FROM_DEPOT = 1
    DESTROYED = 2
    ALL = (SELL_FROM_VEHICLE, SELL_FROM_DEPOT, DESTROYED)


def getVehicleRestorePrice(defaultBuyPrice, exchangeRate, sellPriceFactor, sellToRestoreFactor):
    credits = defaultBuyPrice[0] + defaultBuyPrice[1] * exchangeRate
    return (int(credits * sellPriceFactor * sellToRestoreFactor), 0)


def getVehicleRestorePriceShort(vehTypeCompDescr, gameParams):
    if 'defaults' in gameParams and 'items' in gameParams['defaults'] and 'itemPrices' in gameParams['defaults']['items'] and vehTypeCompDescr in gameParams['defaults']['items']['itemPrices']:
        defaultBuyPrice = gameParams['defaults']['items']['itemPrices'][vehTypeCompDescr]
    else:
        defaultBuyPrice = gameParams['items']['itemPrices'][vehTypeCompDescr]
    exchangeRate = gameParams['economics']['exchangeRate']
    sellPriceFactor = gameParams['sellPriceFactor']
    sellToRestore = gameParams['restore_config']['vehicles']['sellToRestoreFactor']
    return getVehicleRestorePrice(defaultBuyPrice, exchangeRate, sellPriceFactor, sellToRestore)


def getOptionalDeviceRestorePriceShort(optionalDeviceCD, reason, count, isModernized, gameParams):
    itemPrice = gameParams['items']['itemPrices'].getPrices(optionalDeviceCD)
    itemPrices = gameParams['defaults'].get('items', {}).get('itemPrices', {})
    if itemPrices and optionalDeviceCD in itemPrices:
        itemPrice = itemPrices.getPrices(optionalDeviceCD)
    sellPrice = getComponentSellPrice(gameParams, optionalDeviceCD, defaultPrice=True)
    removalCost = getOptionalDeviceRemovalCost(gameParams, optionalDeviceCD)
    restoreCost = gameParams['economics']['paidRemovalCost']
    return getOptionalDeviceRestorePrice(reason, count, isModernized, itemPrice, sellPrice, removalCost, restoreCost)


def getOptionalDeviceRestorePrice(reason, count, isModernized, itemPrice, sellPrice, removalCost, restoreCost):

    def updatePrice(currentPrice, priceToUpdate):
        for currency, amount in priceToUpdate.iteritems():
            currentPrice[currency] += amount

    restorePrice = {'credits': 0,
     'gold': 0,
     'equipCoin': 0,
     'crystal': 0}
    if reason == RESTORE_OPT_DEV_REASON.SELL_FROM_DEPOT:
        updatePrice(restorePrice, sellPrice)
        updatePrice(restorePrice, restoreCost)
    elif reason == RESTORE_OPT_DEV_REASON.DESTROYED:
        if isModernized:
            updatePrice(restorePrice, itemPrice)
        updatePrice(restorePrice, removalCost)
    elif reason == RESTORE_OPT_DEV_REASON.SELL_FROM_VEHICLE:
        updatePrice(restorePrice, sellPrice)
        updatePrice(restorePrice, removalCost)
    restorePrice = {currency:amount * count for currency, amount in restorePrice.iteritems()}
    return restorePrice
