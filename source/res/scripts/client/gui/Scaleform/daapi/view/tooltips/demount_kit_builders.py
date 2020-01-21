# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/demount_kit_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, advanced, demount_kits
from gui.shared.tooltips.builders import AdvancedDataBuilder, DefaultFormatBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, demount_kits.DemountKitToolTipData(contexts.DemountKitContext()), advanced.DemountKitTooltipAdvanced(contexts.DemountKitContext())), DefaultFormatBuilder(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, TOOLTIPS_CONSTANTS.COMPLEX_UI, demount_kits.NotEnoughMoneyTooltipData(contexts.ToolTipContext(None))), AlternativeGoldTooltipBuilder())


class AlternativeGoldTooltipBuilder(AdvancedDataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self):
        super(AlternativeGoldTooltipBuilder, self).__init__(TOOLTIPS_CONSTANTS.GOLD_ALTERNATIVE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, demount_kits.GoldToolTipData(contexts.ToolTipContext(None)), advanced.MoneyAndXpAdvanced(contexts.ToolTipContext(None)))
        self.__btnType = CURRENCIES_CONSTANTS.GOLD
        return

    def _buildData(self, _advanced, *args, **kwargs):
        return super(AlternativeGoldTooltipBuilder, self)._buildData(_advanced, self.__btnType)
