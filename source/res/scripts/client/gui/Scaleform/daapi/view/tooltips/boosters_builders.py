# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/boosters_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import advanced, battle_booster, boosters, contexts, common
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder, TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        itemID = item.getGUIEmblemID()
        return itemID in advanced.SKILL_MOVIES if 'crewSkillBattleBooster' in item.tags else itemID in advanced.MODULE_MOVIES

    return advancedTooltipExist


def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.INVENTORY_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.InventoryBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.InventoryBattleBoosterContext()), condition=_advancedBlockCondition(contexts.InventoryBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EPIC_AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.EpicBattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.ShopBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.ShopBattleBoosterContext()), condition=_advancedBlockCondition(contexts.ShopBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.HangarContext()), advanced.HangarBoosterAdvanced(contexts.HangarContext()), condition=_advancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.NATION_CHANGE_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.NationChangeHangarContext()), advanced.HangarBoosterAdvanced(contexts.NationChangeHangarContext()), condition=_advancedBlockCondition(contexts.NationChangeHangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.DEFAULT_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.BattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.BattleBoosterContext()), condition=_advancedBlockCondition(contexts.BattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.VehCmpConfigurationContext()), advanced.HangarBoosterAdvanced(contexts.VehCmpConfigurationContext()), condition=_advancedBlockCondition(contexts.VehCmpConfigurationContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, None, common.BoosterTooltipContent(contexts.BoosterInfoContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO, None, common.BoosterTooltipContent(contexts.ClanReserveContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTER, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.SHOP_BOOSTER, None, common.QuestBoosterTooltipContent(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_QUESTS, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.QuestsBoosterContext())),
     PersonalReservesBuilder(TOOLTIPS_CONSTANTS.PERSONAL_RESERVES_WIDGET, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))


class PersonalReservesBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(PersonalReservesBuilder, self).__init__(tooltipType, linkage, common.PersonalReservesWidgetTooltipContent(contexts.ToolTipContext(None)))
        return

    def build(self, manager, formatType, advanced_, *args, **kwargs):
        return self._provider
