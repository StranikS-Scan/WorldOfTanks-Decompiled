# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/vehicle_items_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import module
from gui.shared.tooltips import shell
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

class InventoryModuleBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(InventoryModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.InventoryContext()))

    def _buildData(self, intCD, *args):
        return self._provider.buildToolTip(intCD)


class ShopModuleBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ShopModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.ShopContext()))

    def _buildData(self, intCD, *args):
        return self._provider.buildToolTip(intCD)


class TechTreeModuleBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(TechTreeModuleBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.TechTreeContext()))

    def _buildData(self, node, parentCD, *args):
        return self._provider.buildToolTip(node, parentCD)


class ModuleDataBuilder(DataBuilder):
    __slots__ = ()

    def __init__(self, tooltipType, linkage):
        super(ModuleDataBuilder, self).__init__(tooltipType, linkage, module.ModuleBlockTooltipData(contexts.TechMainContext()))

    def _buildData(self, intCD, buyPrice=None, inventoryCount=0, vehicleCount=0, slotIdx=0, eqs=None, *args):
        return self._provider.buildToolTip(intCD, slotIdx, eqs)


class ShellBuilder(DataBuilder):
    __slots__ = ()

    def _buildData(self, intCD, *args):
        return self._provider.buildToolTip(intCD)


def getTooltipBuilders():
    return (InventoryModuleBuilder(TOOLTIPS_CONSTANTS.INVENTORY_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     ShopModuleBuilder(TOOLTIPS_CONSTANTS.SHOP_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     TechTreeModuleBuilder(TOOLTIPS_CONSTANTS.TECHTREE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     ModuleDataBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.COMPARE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.VehCmpConfigurationContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.VEH_COMPARE_TECHTREE_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.VehCmpModulesContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.PREVIEW_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.PreviewContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.AWARD_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, module.ModuleBlockTooltipData(contexts.AwardContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.SHOP_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.ShopContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.AWARD_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.AwardContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HANGAR_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.HangarContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.COMPARE_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.VehCmpConfigurationContext(), basicDataAllowed=False)),
     ShellBuilder(TOOLTIPS_CONSTANTS.INVENTORY_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.InventoryContext())),
     ShellBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, shell.ShellBlockToolTipData(contexts.TechMainContext())))
