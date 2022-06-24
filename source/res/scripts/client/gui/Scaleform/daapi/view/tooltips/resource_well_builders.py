# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/resource_well_builders.py
from gui.Scaleform.daapi.view.tooltips.common_builders import HeaderMoneyAndXpBuilder
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.GOLD, TOOLTIPS_CONSTANTS.RESOURCE_WELL_GOLD, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CREDITS, TOOLTIPS_CONSTANTS.RESOURCE_WELL_CREDITS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.CRYSTAL, TOOLTIPS_CONSTANTS.RESOURCE_WELL_CRYSTAL, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True),
     HeaderMoneyAndXpBuilder(CURRENCIES_CONSTANTS.FREE_XP, TOOLTIPS_CONSTANTS.RESOURCE_WELL_FREE_XP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, True))
