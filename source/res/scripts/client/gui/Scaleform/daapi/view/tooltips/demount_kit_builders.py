# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/demount_kit_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, demount_kits
from gui.shared.tooltips.advanced.demount_kit import DemountKitTooltipAdvanced
from gui.shared.tooltips.advanced.money_and_xp import MoneyAndXpAdvanced
from gui.shared.tooltips.builders import AdvancedDataBuilder, DefaultFormatBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (AdvancedDataBuilder(TOOLTIPS_CONSTANTS.AWARD_DEMOUNT_KIT, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, demount_kits.DemountKitToolTipData(contexts.DemountKitContext()), DemountKitTooltipAdvanced(contexts.DemountKitContext())),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, TOOLTIPS_CONSTANTS.COMPLEX_UI, demount_kits.NotEnoughMoneyTooltipData(contexts.ToolTipContext(None))),
     AlternativeGoldTooltipBuilder(TOOLTIPS_CONSTANTS.GOLD_ALTERNATIVE_STATS, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, demount_kits.GoldStatsToolTipData(contexts.ToolTipContext(None)), MoneyAndXpAdvanced(contexts.ToolTipContext(None))),
     AlternativeGoldTooltipBuilder(TOOLTIPS_CONSTANTS.GOLD_ALTERNATIVE_INFO, TOOLTIPS_CONSTANTS.ADVANCED_SHUFFLE_UI, demount_kits.GoldToolTipData(contexts.ToolTipContext(None)), MoneyAndXpAdvanced(contexts.ToolTipContext(None))))


class AlternativeGoldTooltipBuilder(AdvancedDataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self, tooltipType, linkage, provider, adProvider):
        super(AlternativeGoldTooltipBuilder, self).__init__(tooltipType, linkage, provider, adProvider)
        self.__btnType = CURRENCIES_CONSTANTS.GOLD

    def _buildData(self, _advanced, *args, **kwargs):
        return super(AlternativeGoldTooltipBuilder, self)._buildData(_advanced, self.__btnType)
