# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/boosters_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import battle_booster
from gui.shared.tooltips import boosters
from gui.shared.tooltips import advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        itemID = item.getGUIEmblemID()
        return 'crewSkillBattleBooster' in item.tags or itemID in advanced.MODULE_MOVIES

    return advancedTooltipExist


def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.INVENTORY_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.InventoryBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.InventoryBattleBoosterContext()), condition=_advancedBlockCondition(contexts.InventoryBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EPIC_AWARD_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.EpicBattleBoosterBlockTooltipData(contexts.AwardBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.AwardBattleBoosterContext()), condition=_advancedBlockCondition(contexts.AwardBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.ShopBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.ShopBattleBoosterContext()), condition=_advancedBlockCondition(contexts.ShopBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.HangarContext()), advanced.HangarBoosterAdvanced(contexts.HangarContext()), condition=_advancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK_SHORTENED, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.HangarContext(), True), advanced.HangarBoosterAdvanced(contexts.HangarContext()), condition=_advancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.NATION_CHANGE_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.NationChangeHangarContext()), advanced.HangarBoosterAdvanced(contexts.NationChangeHangarContext()), condition=_advancedBlockCondition(contexts.NationChangeHangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.DEFAULT_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.BattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.BattleBoosterContext()), condition=_advancedBlockCondition(contexts.BattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.VehCmpConfigurationContext()), advanced.HangarBoosterAdvanced(contexts.VehCmpConfigurationContext()), condition=_advancedBlockCondition(contexts.VehCmpConfigurationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterInfoContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.CLAN_RESERVE_INFO, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.ClanReserveContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTER, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHOP_BOOSTER, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.ShopBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_QUESTS, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.QuestsBoosterContext())))
