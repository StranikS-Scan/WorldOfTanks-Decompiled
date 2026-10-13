# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/vehicle_items_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import contexts, TOOLTIP_COMPONENT
from gui.shared.tooltips import module
from gui.shared.tooltips import ability
from gui.shared.tooltips import shell
from gui.shared.tooltips.advanced.fitting_item import FittingItemAdvanced
from gui.shared.tooltips.advanced.data.advanced_constants import SHELL_MOVIES, MODULE_MOVIES
from gui.shared.tooltips.advanced.data.shell_alt_key_data import getPreparedShellItemType
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder, AdvancedComplexBuilder, AdvancedTooltipWindowBuilder
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
__all__ = ('getTooltipBuilders',)

def _advancedBlockCondition(context):

    def advancedTooltipExist(*args):
        item = context.buildItem(*args)
        return not item.isFlameGun() or item.isAutoShootFlameGun() if item.itemTypeName == FITTING_TYPES.VEHICLE_GUN else item.getGUIEmblemID() in MODULE_MOVIES and not (item.itemTypeID == GUI_ITEM_TYPE.CHASSIS and item.isWheeledOnSpotRotationChassis())

    return advancedTooltipExist


def _shellAdvancedBlockCondition(context):

    def advancedTooltipExist(intCD, *_):
        item = context.buildItem(intCD)
        return getPreparedShellItemType(item) in SHELL_MOVIES

    return advancedTooltipExist


def _nationChangeShellAdvancedBlockCondition(context):

    def advancedTooltipExist(vehCD, intCD, *_):
        item = context.buildItem(vehCD, intCD)
        return getPreparedShellItemType(item) in SHELL_MOVIES

    return advancedTooltipExist


class InventoryModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(InventoryModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.InventoryContext()), FittingItemAdvanced(contexts.InventoryContext()), condition=_advancedBlockCondition(contexts.InventoryContext()))

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(InventoryModuleBuilder, self)._buildData(_advanced, intCD)


class ShopModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ShopModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.DefaultContext()), FittingItemAdvanced(contexts.DefaultContext()), condition=_advancedBlockCondition(contexts.DefaultContext()))

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(ShopModuleBuilder, self)._buildData(_advanced, intCD)


class TechTreeModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TechTreeModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.ModuleContext()), FittingItemAdvanced(contexts.ModuleContext()), condition=_advancedBlockCondition(contexts.ModuleContext()))

    def _buildData(self, _advanced, node, parentCD, *args, **kwargs):
        return super(TechTreeModuleBuilder, self)._buildData(_advanced, node, parentCD)


class ModuleDataBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ModuleDataBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.TechMainContext()), FittingItemAdvanced(contexts.TechMainContext()), condition=_advancedBlockCondition(contexts.TechMainContext()))

    def _buildData(self, _advanced, intCD, buyPrice=None, inventoryCount=0, vehicleCount=0, slotIdx=0, eqs=None, *args):
        return super(ModuleDataBuilder, self)._buildData(_advanced, intCD, slotIdx, eqs)


class ShellBuilder(DataBuilder):
    __slots__ = ()

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(ShellBuilder, self)._buildData(_advanced, intCD)


class AdvancedShellBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(AdvancedShellBuilder, self)._buildData(_advanced, intCD)


def getTooltipBuilders():
    return (InventoryModuleBuilder(TOOLTIPS_CONSTANTS.INVENTORY_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI),
     ShopModuleBuilder(TOOLTIPS_CONSTANTS.DEFAULT_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI),
     TechTreeModuleBuilder(TOOLTIPS_CONSTANTS.TECHTREE_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI),
     ModuleDataBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.HangarContext()), FittingItemAdvanced(contexts.HangarContext()), condition=_advancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_CARD_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.HangarCardContext()), FittingItemAdvanced(contexts.HangarCardContext()), condition=_advancedBlockCondition(contexts.HangarCardContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_SLOT_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.HangarSlotContext()), FittingItemAdvanced(contexts.HangarSlotContext()), condition=_advancedBlockCondition(contexts.HangarSlotContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.AmmunitionSlotSpecTooltipData(contexts.ToolTipContext(TOOLTIP_COMPONENT.HANGAR))),
     AdvancedComplexBuilder(TOOLTIPS_CONSTANTS.OPT_DEVICE_EMPTY_SLOT, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.OptDeviceEmptyBlockTooltipData(contexts.EmptyOptDeviceSlotContext(TOOLTIP_COMPONENT.HANGAR))),
     AdvancedComplexBuilder(TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.AmmunitionEmptyBlockTooltipData(contexts.ToolTipContext(TOOLTIP_COMPONENT.HANGAR))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.NATION_CHANGE_HANGAR_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.NationChangeHangarContext()), FittingItemAdvanced(contexts.NationChangeHangarContext()), condition=_advancedBlockCondition(contexts.NationChangeHangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.COMPARE_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.VehCmpConfigurationContext()), FittingItemAdvanced(contexts.VehCmpConfigurationContext()), condition=_advancedBlockCondition(contexts.VehCmpConfigurationContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.COMPARE_SLOT_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.VehCmpConfigurationSlotContext()), FittingItemAdvanced(contexts.VehCmpConfigurationSlotContext()), condition=_advancedBlockCondition(contexts.VehCmpConfigurationSlotContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEH_COMPARE_TECHTREE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.VehCmpModulesContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.PREVIEW_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.PreviewContext()), FittingItemAdvanced(contexts.PreviewContext()), condition=_advancedBlockCondition(contexts.PreviewContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.AwardContext()), FittingItemAdvanced(contexts.AwardContext()), condition=_advancedBlockCondition(contexts.AwardContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_MODULE, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, module.ModuleBlockTooltipData(contexts.ShopContext()), FittingItemAdvanced(contexts.ShopContext()), condition=_advancedBlockCondition(contexts.ShopContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.SHOP_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.ShopContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.DEFAULT_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.DefaultContext()), FittingItemAdvanced(contexts.DefaultContext()), condition=_shellAdvancedBlockCondition(contexts.DefaultContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.AWARD_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.AwardContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.HangarContext()), FittingItemAdvanced(contexts.HangarContext()), condition=_shellAdvancedBlockCondition(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.NATION_CHANGE_HANGAR_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.NationChangeHangarContext()), FittingItemAdvanced(contexts.NationChangeHangarContext()), condition=_nationChangeShellAdvancedBlockCondition(contexts.NationChangeHangarContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.COMPARE_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.VehCmpConfigurationContext()), FittingItemAdvanced(contexts.VehCmpConfigurationContext()), condition=_shellAdvancedBlockCondition(contexts.VehCmpConfigurationContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.INVENTORY_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.InventoryContext()), FittingItemAdvanced(contexts.TechMainContext()), condition=_shellAdvancedBlockCondition(contexts.TechMainContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, shell.ShellBlockToolTipData(contexts.TechMainContext()), FittingItemAdvanced(contexts.TechMainContext()), condition=_shellAdvancedBlockCondition(contexts.TechMainContext())),
     AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.ABILITY_LOBBY_TOOLTIP, None, ability.AbilitySkillTooltipData(contexts.ToolTipContext(None)), ability.AbilitySkillTooltipDataAdditional(contexts.ToolTipContext(None))))
