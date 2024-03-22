# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/tankman_helpers.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from helpers_common import getFinalRetrainCost, getRetrainCost
from items.tankmen import TankmanDescr

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getPriceDiscountMassRetrain(retrainIndex, isUseless, tankmen, itemsCache=None):
    shopRequester = itemsCache.items.shop
    retrainCost = getRetrainCost(shopRequester.tankmanCost, shopRequester.tankman['retrain']['options'])[retrainIndex]
    goldSum = creditsSum = 0
    for index, tankman in enumerate(tankmen):
        if not isUseless[index]:
            credits, gold = getFinalRetrainCost(TankmanDescr(tankman.strCD), retrainCost)
            goldSum += gold
            creditsSum += credits

    return (goldSum, creditsSum)
