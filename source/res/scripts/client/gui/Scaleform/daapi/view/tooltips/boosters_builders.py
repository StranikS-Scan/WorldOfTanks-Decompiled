# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/boosters_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import battle_booster
from gui.shared.tooltips import boosters
from gui.shared.tooltips import advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.INVENTORY_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.InventoryBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.InventoryBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.HangarContext()), advanced.HangarBoosterAdvanced(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_BATTLE_BOOSTER, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.ShopBattleBoosterContext()), advanced.HangarBoosterAdvanced(contexts.ShopBattleBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_COMPARE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, battle_booster.BattleBoosterBlockTooltipData(contexts.VehCmpConfigurationContext()), advanced.HangarBoosterAdvanced(contexts.VehCmpConfigurationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.BoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_SHOP, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.ShopBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.BOOSTERS_QUESTS, TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO_UI, boosters.BoosterTooltipData(contexts.QuestsBoosterContext())))
