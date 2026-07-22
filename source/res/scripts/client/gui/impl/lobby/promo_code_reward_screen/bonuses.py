# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/bonuses.py
import copy
import constants
from gui.impl.lobby.promo_code_reward_screen import isLootboxesExtensionAvailable
from gui.server_events import bonuses
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker
QUESTS_BUNUS_NAME = 'quests'
if not isLootboxesExtensionAvailable():
    RewardScreenCustomizationBonusUIPacker = CustomizationBonusUIPacker
else:
    from gui_lootboxes.gui.bonuses.bonuses_packers import LootBoxCustomizationBonusUIPacker
    from shared_utils import first
    from gui.shared.money import Money
    from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
    from gui.impl.backport import createTooltipData
    from gui.server_events.bonuses import getServiceBonuses
    from gui.shared.gui_items.customization import CustomizationTooltipContext

    class RewardScreenCustomizationBonusUIPacker(LootBoxCustomizationBonusUIPacker):

        @classmethod
        def _getToolTip(cls, bonus):
            tooltipData = []
            originalBonus = copy.deepcopy(bonus)
            for item in originalBonus.getCustomizations():
                if item is None:
                    continue
                compensation = item.get('customCompensation', None)
                if compensation:
                    compBonus = cls.__getCompBonus(compensation)
                    if compBonus:
                        item['customCompensation'] = None
                        item['compensatedNumber'] = 0
                        tooltipData.append(createTooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[originalBonus, compBonus]))
                itemCustomization = bonus.getC11nItem(item)
                tooltipData.append(createTooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=itemCustomization.intCD)))

            return tooltipData

        @classmethod
        def __getCompBonus(cls, compensation):
            money = Money.makeMoney(compensation)
            if money is not None:
                for currency, value in money.iteritems():
                    if value:
                        return first(getServiceBonuses(currency, value, isCompensation=True))

            return


def getRewardsScreenDefaultBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({QUESTS_BUNUS_NAME: SimpleBonusUIPacker(),
     'customizations': RewardScreenCustomizationBonusUIPacker()})
    if isLootboxesExtensionAvailable():
        from gui_lootboxes.gui.bonuses.bonuses_packers import TmanTemplateBonusPacker, LootBoxVehiclesBonusUIPacker, LootBoxTankmenBonusUIPacker, LootBoxCollectionItemBonusUIPacker, LootBoxAnyCollectionItemBonusUIPacker, LootBoxTokensBonusUIPacker, LootBoxDogTagUIPacker, PremiumDaysBonusPacker
        mapping.update({'tmanToken': TmanTemplateBonusPacker(),
         'vehicles': LootBoxVehiclesBonusUIPacker(),
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
