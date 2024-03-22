# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/bonus_packers.py
from collections import defaultdict
from copy import deepcopy
import typing
from adisp import adisp_process
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl.lobby.awards.packers import MultiAwardVehiclesBonusUIPacker
from gui.server_events.bonuses import mergeBonuses, splitBonuses, getNonQuestBonuses
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, Customization3Dand2DbonusUIPacker
from gui.shared.money import Currency
from helpers.dependency import replace_none_kwargs
from shared_utils import CONST_CONTAINER, findFirst, first
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
    from gui.server_events.bonuses import CustomizationsBonus, SimpleBonus

class QuestReward(CONST_CONTAINER):
    INDUSTRIAL_RESOURCE = 'industrial_resource'
    TOUR_COIN = 'tourcoin'
    CURRENCY_REWARDS = (INDUSTRIAL_RESOURCE, TOUR_COIN)


BONUSES_ORDER = ['vehicles',
 'items',
 'premium_plus',
 'customizations',
 'tmanToken',
 Currency.EQUIP_COIN,
 'goodies',
 Currency.CREDITS]

def composeBonuses(rewards, bonusesOrder=None):
    bonuses = []
    for key, value in rewards.items():
        bonuses.extend(getNonQuestBonuses(key, value))

    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    if bonusesOrder is not None:

        def sortBonusesByKey(bonus):
            bonusName = bonus.getName()
            return bonusesOrder.index(bonusName) if bonusName in bonusesOrder else len(bonusesOrder) + 1

        bonuses.sort(key=sortBonusesByKey)
    return bonuses


def getCurrencyReward(rewards):
    result = dict(currencies=defaultdict(dict))
    for name, value in rewards.items():
        if name not in QuestReward.CURRENCY_REWARDS:
            continue
        result['currencies'][_normalizeCurrencyName(name)]['count'] = int(value)

    return result


def findVehicle(rewards):
    vehIntCD = None
    vehicleReward = findFirst(lambda r: r[0] == 'vehicles', rewards.items())
    if vehicleReward is not None:
        if isinstance(vehicleReward[1], list) and vehicleReward[1]:
            vehIntCD = first(first(vehicleReward[1]).keys())
        elif isinstance(vehicleReward[1], dict):
            vehIntCD = first(vehicleReward[1].keys())
    return int(vehIntCD) if isinstance(vehIntCD, (str, unicode)) and vehIntCD.isdigit() else vehIntCD


class CustomizationsBonusPacker(Customization3Dand2DbonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(CustomizationsBonusPacker, cls)._packSingleBonus(bonus, item, label)
        customizationItem = bonus.getC11nItem(item)
        model.setValue(str(customizationItem.id))
        return model


def getClanSupplyBonusPacker(isProgression=False):
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': MultiAwardVehiclesBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker()})
    if not isProgression:
        mapping['customizations'] = CustomizationsBonusPacker()
    else:
        mapping['customizations'] = Customization3Dand2DbonusUIPacker()
    return BonusUIPacker(mapping)


def _normalizeCurrencyName(name):
    return 'industrialResource' if name == QuestReward.INDUSTRIAL_RESOURCE else name


@adisp_process
@replace_none_kwargs(purchaseCache=IPurchaseCache)
def extractBonuses(invoiceData, productCode, callback, purchaseCache=None):
    purchasePackage = yield purchaseCache.requestPurchaseByID(productCode)
    rewards = deepcopy(invoiceData['data'])
    compensation = deepcopy(invoiceData.get('compensation', {}))
    rewards.update(compensation)
    for _, extItem in purchasePackage.getExtraData().iterItems():
        rewards.update(extItem)

    callback(rewards)
