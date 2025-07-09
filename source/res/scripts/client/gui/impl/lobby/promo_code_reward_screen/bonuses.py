# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/bonuses.py
import copy
import constants
from gui.impl.lobby.promo_code_reward_screen import isLootboxesExtensionAvailable
from gui.server_events import bonuses
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker
QUESTS_BUNUS_NAME = 'quests'

def getRewardsScreenDefaultBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({QUESTS_BUNUS_NAME: SimpleBonusUIPacker()})
    if isLootboxesExtensionAvailable():
        from gui_lootboxes.gui.bonuses.bonuses_packers import TmanTemplateBonusPacker, LootBoxVehiclesBonusUIPacker, LootBoxCustomizationBonusUIPacker, LootBoxTankmenBonusUIPacker, LootBoxCollectionItemBonusUIPacker, LootBoxAnyCollectionItemBonusUIPacker, LootBoxTokensBonusUIPacker, LootBoxDogTagUIPacker, PremiumDaysBonusPacker
        mapping.update({'tmanToken': TmanTemplateBonusPacker(),
         'vehicles': LootBoxVehiclesBonusUIPacker(),
         'customizations': LootBoxCustomizationBonusUIPacker(),
         'tankmen': LootBoxTankmenBonusUIPacker(),
         'collectionItem': LootBoxCollectionItemBonusUIPacker(),
         'lootBoxToken': LootBoxTokensBonusUIPacker(),
         'dogTagComponents': LootBoxDogTagUIPacker(),
         'anyCollectionItem': LootBoxAnyCollectionItemBonusUIPacker(),
         constants.PREMIUM_ENTITLEMENTS.PLUS: PremiumDaysBonusPacker()})
    return mapping


def getRewardsBonusPacker():
    return BonusUIPacker(getRewardsScreenDefaultBonusPackerMap())


def splitBonuses(bonusesToSplit):
    split = []
    for bonus in bonusesToSplit:
        splitFunc = getSplitBonusFunction(bonus)
        if splitFunc:
            split.extend(splitFunc(bonus))
        split.append(bonus)

    return split


def getSplitBonusFunction(bonus):
    return splitVehiclesBonus if isinstance(bonus, bonuses.VehiclesBonus) else bonuses.getSplitBonusFunction(bonus)


def splitVehiclesBonus(bonus):
    split = []
    value = bonus.getValue()
    for it in value:
        if isinstance(it, dict):
            for key, sub in it.iteritems():
                item = copy.deepcopy(bonus)
                item.setValue([{key: sub}])
                split.append(item)

        item = copy.deepcopy(bonus)
        item.setValue([it])

    return split
