# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/economics.py
import typing
from collections import namedtuple
from ItemRestore import getVehicleRestorePrice
from gui.shared.money import Money, Currency
from rent_common import makeRentID

class ActualPrice(object):
    RESTORE_PRICE = 1
    RENT_PRICE = 2
    BUY_PRICE = 3


_DisplayPrice = namedtuple('PriceTuple', ('type', 'cost'))

def getActionPrc(price, defaultPrice):

    def calculate(price, defaultPrice):
        price = price or 0
        defaultPrice = defaultPrice or 0
        return 0 if defaultPrice == 0 or price == defaultPrice else int(round((1 - float(price) / defaultPrice) * 100))

    if isinstance(price, Money):
        for currency in Currency.BY_WEIGHT:
            value = calculate(price.get(currency), defaultPrice.get(currency))
            if value != 0:
                return value

        return 0
    return calculate(price, defaultPrice)


def calcRentPackages(vehicle, proxy, rentalsController):
    result = []
    if proxy is not None and vehicle.isRentable:
        shopRentPrices = proxy.shop.getVehicleRentPrices().get(vehicle.intCD, {})
        shopDefaultRentPrices = proxy.shop.defaults.getVehicleRentPrices().get(vehicle.intCD, {})
        filteredRentPackages = rentalsController.filterRentPackages(shopRentPrices)
        filteredDefaultRentCosts = rentalsController.filterRentPackages(shopDefaultRentPrices)
        for rentType in sorted(filteredRentPackages.iterkeys()):
            costsOfCurrentType = filteredRentPackages[rentType]
            defaultCostsOfCurrentType = filteredDefaultRentCosts.get(rentType, {})
            for packageID in sorted(costsOfCurrentType):
                currentPackage = costsOfCurrentType[packageID]
                rentPrice = rentalsController.getRentPriceOfPackage(vehicle, rentType, packageID, currentPackage)
                defaultPackage = defaultCostsOfCurrentType.get(packageID, None)
                if defaultPackage is not None:
                    defaultRentPrice = rentalsController.getRentPriceOfPackage(vehicle, rentType, packageID, defaultPackage)
                else:
                    defaultRentPrice = rentPrice
                result.append({'rentID': makeRentID(rentType, packageID),
                 'rentPrice': rentPrice,
                 'defaultRentPrice': defaultRentPrice,
                 'seasonType': currentPackage.get('seasonType', None)})

    return result


def getPremiumCostActionPrc(discounts, packet, proxy):
    defaultPremiumCost = proxy.shop.defaults.premiumCost
    premiumCost = proxy.shop.getPremiumCostWithDiscount(discounts)
    return getActionPrc(premiumCost.get(packet), defaultPremiumCost.get(packet))


def calcVehicleRestorePrice(defaultPrice, proxy):
    exchangeRate = proxy.exchangeRate
    sellPriceFactor = proxy.sellPriceModif
    restorePriceModif = proxy.vehiclesRestoreConfig.restorePriceModif
    return Money.makeFromMoneyTuple(getVehicleRestorePrice(defaultPrice, exchangeRate, sellPriceFactor, restorePriceModif))


def getGUIPrice(item, money, exchangeRate):
    mayRent, _ = item.mayRent(money)
    if item.isRestorePossible():
        if item.isRestoreAvailable():
            if item.mayRestoreWithExchange(money, exchangeRate) or not mayRent:
                return item.restorePrice
            return item.minRentPrice
        if item.hasRestoreCooldown():
            return item.minRentPrice or item.restorePrice
    return item.minRentPrice or item.getBuyPrice(preferred=False).price


def getPriceTypeAndValue(item, money, exchangeRate):
    mayRent, _ = item.mayRent(money)
    if item.isRestorePossible() and (item.isRestorePossible() and item.mayRestoreWithExchange(money, exchangeRate) or not mayRent):
        return _DisplayPrice(ActualPrice.RESTORE_PRICE, item.restorePrice)
    if item.hasRestoreCooldown() and not item.minRentPrice:
        return _DisplayPrice(ActualPrice.RESTORE_PRICE, item.restorePrice)
    return _DisplayPrice(ActualPrice.RENT_PRICE, item.minRentPrice) if item.minRentPrice else _DisplayPrice(ActualPrice.BUY_PRICE, item.getBuyPrice(preferred=False))
