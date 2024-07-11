# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui_lootboxes.gui.bonuses.bonus_tooltips import LootBoxVehicleBlueprintFragmentTooltipData
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.guaranteed_reward_tooltip import GuaranteedRewardTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
from gui.impl.lobby.loot_box.loot_box_helper import getKeyByID
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, ToolTipBaseData
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
from helpers import dependency
from skeletons.gui.shared import IItemsCache
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, LootBoxVehicleBlueprintFragmentTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.LOOT_BOX_TOOLTIP, None, LootBoxTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.LOOT_BOX_GUARANTEED_REWARD_TOOLTIP, None, LootBoxGuaranteedRewardTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.LOOT_BOX_KEY_TOOLTIP, None, LootBoxKeyTooltipData(contexts.ToolTipContext(None))))


class LootBoxTooltipData(ToolTipBaseData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(LootBoxTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.LOOT_BOX_TOOLTIP)

    def getDisplayableData(self, lootboxId):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByTokenID(lootboxId)
        return None if lootBox is None else DecoratedTooltipWindow(LootboxTooltip(lootBox), useDecorator=False)


class LootBoxKeyTooltipData(ToolTipBaseData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(LootBoxKeyTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.LOOT_BOX_KEY_TOOLTIP)

    def getDisplayableData(self, keyID):
        key = getKeyByID(keyID)
        return None if key is None else DecoratedTooltipWindow(LootboxKeyTooltip(key), useDecorator=False)


class LootBoxGuaranteedRewardTooltipData(ToolTipBaseData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(LootBoxGuaranteedRewardTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.LOOT_BOX_GUARANTEED_REWARD_TOOLTIP)

    def getDisplayableData(self, lootboxId):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(lootboxId)
        return None if lootBox is None else DecoratedTooltipWindow(GuaranteedRewardTooltip(lootBox), useDecorator=False)
