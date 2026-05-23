# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/summer_sale/common.py
from collections import defaultdict
from gui.server_events.bonuses import LootBoxTokensBonus, VehiclesBonus, getNonQuestBonuses
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ISummerSaleController
from skeletons.gui.shared import IItemsCache
MAIN_COIN = 'bumblebee_coin'
ADDITIONAL_COIN = 'honey_coin'
SUMMER_SALE_SET_BUYING_LIMIT = 20
BONUSES_ORDER = {bonusName:order for order, bonusName in enumerate((MAIN_COIN,
 ADDITIONAL_COIN,
 Currency.CREDITS,
 VehiclesBonus.VEHICLES_BONUS,
 'lootBoxToken'))}

@dependency.replace_none_kwargs(summerSale=ISummerSaleController)
def isValidProduct(productCode, product, summerSale=None):
    return bool(product) and productCode in summerSale.getProductsOrder()


def getBonusName(bonus):
    return bonus.getCode() if bonus.getName() == 'currencies' else bonus.getName()


def getBonusesFromProduct(productCode, products):
    bonuses = []
    for key, value in products.iteritems():
        if key in _PRODUCT_DATA_KEY_BONUS_FACTORY:
            bonuses.extend(_PRODUCT_DATA_KEY_BONUS_FACTORY[key](key, value, {'price': products.get('price', {}),
             'productCode': productCode}))

    return bonuses


def groupBonusesByProbability(bonusSlots):
    groupedByProbabilityBonuses = defaultdict(list)
    for rewards in bonusSlots.itervalues():
        groupedByProbabilityBonuses[first(rewards['probability'])].extend(rewards['bonuses'])

    return groupedByProbabilityBonuses


def groupBonusesByName(bonuses):
    groupedByNameBonuses = defaultdict(list)
    for bonus in bonuses:
        groupedByNameBonuses[getBonusName(bonus)].append(bonus)

    return groupedByNameBonuses


def mergeBonuses(bonuses):
    mergedBonuses = defaultdict(list)
    for probability, groupedByNameBonuses in bonuses.iteritems():
        for bonusName, rewards in groupedByNameBonuses.iteritems():
            mergedBonuses[probability].extend([_getBonusWithMaxValue(rewards)] if bonusName in Currency.ALL + (MAIN_COIN, ADDITIONAL_COIN) else rewards)

    return mergedBonuses


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getVehicleBonus(key, value, ctx, itemsCache=None):
    return getNonQuestBonuses(VehiclesBonus.VEHICLES_BONUS, {value: ctx or {}})


def _getTokenBonus(key, value, ctx):
    return [LootBoxTokensBonus({value['cd']: {'count': value.get('amount', 1)}}, ctx=ctx)] if 'cd' in value and value['cd'].startswith('lootBox:') else []


_PRODUCT_DATA_KEY_BONUS_FACTORY = {'vehicleCD': _getVehicleBonus,
 'token': _getTokenBonus}

def _getBonusWithMaxValue(bonuses):
    bonus = bonuses[0]
    for b in bonuses:
        if b.getValue() > bonus.getValue():
            bonus = b

    return bonus
