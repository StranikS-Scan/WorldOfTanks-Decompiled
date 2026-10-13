# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/boosters_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, common
from gui.shared.tooltips import battle_booster
from gui.shared.tooltips import boosters
from gui.shared.tooltips.advanced.data import advanced_constants
from gui.shared.tooltips.advanced.fitting_item import FittingItemAdvanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        itemID = item.getGUIEmblemID()
        return itemID in advanced_constants.SKILL_MOVIES if 'crewSkillBattleBooster' in item.tags else itemID in advanced_constants.MODULE_MOVIES

    return advancedTooltipExist


def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.INVENTORY_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.InventoryBattleBoosterContext()), FittingItemAdvanced(contexts.InventoryBattleBoosterContext()), condition=_advancedBlockCondition(contexts.InventoryBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), FittingItemAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EPIC_AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.EpicBattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), FittingItemAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.ShopBattleBoosterContext()), FittingItemAdvanced(contexts.ShopBattleBoosterContext()), condition=_advancedBlockCondition(contexts.ShopBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.HangarContext()), FittingItemAdvanced(contexts.HangarContext()), condition=_advancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.NATION_CHANGE_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.NationChangeHangarContext()), FittingItemAdvanced(contexts.NationChangeHangarContext()), condition=_advancedBlockCondition(contexts.NationChangeHangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.DEFAULT_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.BattleBoosterContext()), FittingItemAdvanced(contexts.BattleBoosterContext()), condition=_advancedBlockCondition(contexts.BattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.VehCmpConfigurationContext()), FittingItemAdvanced(contexts.VehCmpConfigurationContext()), condition=_advancedBlockCondition(contexts.VehCmpConfigurationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterInfoContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.ClanReserveContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTER, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_BOOSTER, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.ShopBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_QUESTS, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.QuestsBoosterContext())),
     PersonalReservesBuilder(TOOLTIPS_CONSTANTS.PERSONAL_RESERVES_WIDGET, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))


class PersonalReservesBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(PersonalReservesBuilder, self).__init__(tooltipType, linkage, common.PersonalReservesWidgetTooltipContent(contexts.ToolTipContext(None)))
        return

    def build(self, manager, formatType, advanced_, *args, **kwargs):
        return self._provider
