# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/post_progression_prices_common.py
from items import vehicles

def getPostProgressionPrice(priceTag, vehType, priceContainer=None):
    postProgressionPricesOverrides = vehType.postProgressionPricesOverrides
    postProgressionPrices = priceContainer if priceContainer else vehicles.g_cache.postProgression().prices
    if postProgressionPricesOverrides and priceTag in postProgressionPricesOverrides:
        price = postProgressionPricesOverrides[priceTag]
    else:
        price = postProgressionPrices.get(priceTag, {}).get(vehType.level, {})
    return price
