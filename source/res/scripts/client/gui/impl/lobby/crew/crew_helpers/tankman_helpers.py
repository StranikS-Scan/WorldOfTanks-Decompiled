# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/tankman_helpers.py
import time
import BigWorld
from constants import GRACE_PERIOD_RESET_PERK
from helpers import dependency
from helpers_common import getFinalRetrainCost, getRetrainCost
from items.tankmen import TankmanDescr
from skeletons.gui.shared import IItemsCache

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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getBethsSlotsCount(itemsCache=None):
    tankmenInBarracks = itemsCache.items.tankmenInBarracksCount()
    slotsCount = itemsCache.items.stats.tankmenBerthsCount
    freeBerthsCount = slotsCount - tankmenInBarracks
    return (slotsCount, freeBerthsCount)


def getPerksResetGracePeriod():
    timeLeft = 0
    playerAccount = BigWorld.player()
    if not playerAccount:
        return timeLeft
    token = playerAccount.tokens.getToken(GRACE_PERIOD_RESET_PERK)
    curTime = int(time.time())
    if token and token[0] > curTime:
        timeLeft = token[0] - curTime
    return timeLeft


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isPremiumRetrainWarning(tmenIds, vehicleCD, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    if not vehicle.isPremium:
        return False
    for tmanId in tmenIds:
        tman = itemsCache.items.getTankman(tmanId)
        if tman.vehicleNativeDescr.type.compactDescr != vehicleCD:
            return True

    return False
