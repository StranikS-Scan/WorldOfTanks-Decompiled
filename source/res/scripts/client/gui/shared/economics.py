# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/economics.py
from ItemRestore import getVehicleRestorePrice
from gui.shared.money import Money, ZERO_MONEY, Currency

def getActionPrc(price, defaultPrice):

    def calculate(price, defaultPrice):
        return 0 if defaultPrice == 0 or price == defaultPrice else int(round((1 - float(price) / defaultPrice) * 100))

    if isinstance(price, Money):
        for currency in Currency.BY_WEIGHT:
            value = calculate(price.get(currency), defaultPrice.get(currency))
            if value != 0:
                return value

        return 0
    return calculate(price, defaultPrice)


def calcRentPackages(vehicle, proxy):
    result = []
    if proxy is not None and vehicle.isRentable:
        rentCost = proxy.shop.getVehicleRentPrices().get(vehicle.intCD, {})
        defaultRentCost = proxy.shop.defaults.getVehicleRentPrices().get(vehicle.intCD, {})
        if len(rentCost) and len(defaultRentCost) is not None:
            for key in sorted(rentCost.keys()):
                rentPrice = Money(*rentCost[key].get('cost', ZERO_MONEY))
                defaultRentPrice = Money(*defaultRentCost.get(key, {}).get('cost', rentPrice))
                result.append({'days': key,
                 'rentPrice': rentPrice,
                 'defaultRentPrice': defaultRentPrice})

    return result


def getPremiumCostActionPrc(discounts, packet, proxy):
    defaultPremiumCost = proxy.shop.defaults.premiumCost
    premiumCost = proxy.shop.getPremiumCostWithDiscount(discounts)
    return getActionPrc(premiumCost.get(packet), defaultPremiumCost.get(packet))


def calcVehicleRestorePrice(defaultPrice, proxy):
    """
    # calculate vehicle restore price
    :param defaultPrice: <Money> default buy price
    :return: <Money> restore price
    """
    exchangeRate = proxy.exchangeRate
    sellPriceFactor = proxy.sellPriceModif
    resorePriceModif = proxy.vehiclesRestoreConfig.restorePriceModif
    return Money(*getVehicleRestorePrice(defaultPrice, exchangeRate, sellPriceFactor, resorePriceModif))


def getGUIPrice(item, money, exchangeRate):
    """
    # chooses one of item prices to display in GUI
    :param item: <GUIItem>
    :param money: <Money>
    :param exchangeRate: <int> gold exchange rate
    :return: <Money> one price to display in GUI
    """
    mayRent, rentReason = item.mayRent(money)
    if item.isRestorePossible():
        if item.isRestoreAvailable():
            if item.mayRestoreWithExchange(money, exchangeRate) or not mayRent:
                return item.restorePrice
            else:
                return item.minRentPrice
        elif item.hasRestoreCooldown():
            return item.minRentPrice or item.restorePrice
    return item.minRentPrice or item.altPrice or item.buyPrice
