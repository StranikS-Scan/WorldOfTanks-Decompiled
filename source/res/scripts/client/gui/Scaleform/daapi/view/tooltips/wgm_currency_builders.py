# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/wgm_currency_builders.py
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import wgm_currency
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

class CurrencyTooltipBuilder(DataBuilder):
    __slots__ = ('__btnType',)

    def __init__(self, btnType, tooltipType, linkage):
        super(CurrencyTooltipBuilder, self).__init__(tooltipType, linkage, wgm_currency.WGMCurrencyTooltip(contexts.ToolTipContext(None)))
        self.__btnType = btnType
        return

    def _buildData(self, *args):
        return super(CurrencyTooltipBuilder, self)._buildData(self.__btnType)


def getTooltipBuilders():
    return (CurrencyTooltipBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.GOLD_STATS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI), CurrencyTooltipBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.CREDITS_STATS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI))
