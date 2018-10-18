# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/vehicle_items_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import module
from gui.shared.tooltips import shell, advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

class InventoryModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(InventoryModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.InventoryContext()), advanced.HangarModuleAdvanced(contexts.InventoryContext()))

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(InventoryModuleBuilder, self)._buildData(_advanced, intCD)


class ShopModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ShopModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.ShopContext()), advanced.HangarModuleAdvanced(contexts.ShopContext()))

    def _buildData(self, _advanced, intCD, *args, **kwargs):
        return super(ShopModuleBuilder, self)._buildData(_advanced, intCD)


class TechTreeModuleBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TechTreeModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.TechTreeContext()), advanced.HangarModuleAdvanced(contexts.TechTreeContext()))

    def _buildData(self, _advanced, node, parentCD, *args, **kwargs):
        return super(TechTreeModuleBuilder, self)._buildData(_advanced, node, parentCD)


class ModuleDataBuilder(AdvancedDataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ModuleDataBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.TechMainContext()), advanced.HangarModuleAdvanced(contexts.TechMainContext()))

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
    return (InventoryModuleBuilder(TOOLTIPS_CONSTANTS.INVENTORY_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     ShopModuleBuilder(TOOLTIPS_CONSTANTS.SHOP_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     TechTreeModuleBuilder(TOOLTIPS_CONSTANTS.TECHTREE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     ModuleDataBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.HangarContext()), advanced.HangarModuleAdvanced(contexts.HangarContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.COMPARE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.VehCmpConfigurationContext()), advanced.HangarModuleAdvanced(contexts.VehCmpConfigurationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEH_COMPARE_TECHTREE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.VehCmpModulesContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.PREVIEW_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.PreviewContext()), advanced.HangarModuleAdvanced(contexts.PreviewContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.AwardContext()), advanced.HangarModuleAdvanced(contexts.AwardContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.SHOP_20_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.Shop20Context()), advanced.HangarModuleAdvanced(contexts.Shop20Context())),
     ShellBuilder(TOOLTIPS_CONSTANTS.SHOP_20_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.Shop20Context())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.SHOP_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.ShopContext()), advanced.HangarShellAdvanced(contexts.ShopContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.AWARD_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.AwardContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.HANGAR_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.HangarContext()), advanced.HangarShellAdvanced(contexts.HangarContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.COMPARE_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.VehCmpConfigurationContext(), basicDataAllowed=False), advanced.HangarShellAdvanced(contexts.VehCmpConfigurationContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.INVENTORY_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.InventoryContext()), advanced.HangarShellAdvanced(contexts.TechMainContext())),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.TechMainContext()), advanced.HangarShellAdvanced(contexts.TechMainContext())))
