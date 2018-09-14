# Embedded file name: scripts/client/gui/customization_2_0/shared.py
from gui.customization_2_0.data_aggregator import CUSTOMIZATION_TYPE
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons
CAMOUFLAGE_GROUP_MAPPING = ('winter', 'summer', 'desert')

def formatPriceGold(value):
    if g_itemsCache.items.stats.gold >= value:
        return text_styles.goldTextBig(value)
    else:
        return formatPriceAlert(value)


def formatPriceCredits(value):
    if g_itemsCache.items.stats.credits >= value:
        return text_styles.creditsTextBig(value)
    else:
        return formatPriceAlert(value)


def formatPriceAlert(value):
    return '{0} {1}'.format(icons.alert(), text_styles.errCurrencyTextBig(value))


def isSale(cType, days):
    _DEFAULT_COST = {CUSTOMIZATION_TYPE.CAMOUFLAGE: g_itemsCache.items.shop.defaults.camouflageCost,
     CUSTOMIZATION_TYPE.EMBLEM: g_itemsCache.items.shop.defaults.playerEmblemCost,
     CUSTOMIZATION_TYPE.INSCRIPTION: g_itemsCache.items.shop.defaults.playerInscriptionCost}
    _COST = {CUSTOMIZATION_TYPE.CAMOUFLAGE: g_itemsCache.items.shop.camouflageCost,
     CUSTOMIZATION_TYPE.EMBLEM: g_itemsCache.items.shop.playerEmblemCost,
     CUSTOMIZATION_TYPE.INSCRIPTION: g_itemsCache.items.shop.playerInscriptionCost}
    sale = _DEFAULT_COST[cType][days][0] - _COST[cType][days][0] > 0
    return sale


def getSalePriceString(isGold, price):
    if isGold:
        salePrice = {'newPrice': [0, price]}
    else:
        salePrice = {'newPrice': [price, 0]}
    return salePrice


def forEachSlotIn(newSlotsData, oldSlotsData, functionToRun):
    for cType in (CUSTOMIZATION_TYPE.CAMOUFLAGE, CUSTOMIZATION_TYPE.EMBLEM, CUSTOMIZATION_TYPE.INSCRIPTION):
        for slotIdx in range(0, len(newSlotsData['data'][cType]['data'])):
            newSlotItem = newSlotsData['data'][cType]['data'][slotIdx]
            oldSlotItem = oldSlotsData['data'][cType]['data'][slotIdx]
            functionToRun(newSlotItem, oldSlotItem, cType, slotIdx)
