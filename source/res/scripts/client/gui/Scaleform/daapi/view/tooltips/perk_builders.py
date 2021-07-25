# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/perk_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import perk
from gui.shared.tooltips import advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.PERK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, advanced.PerkTooltipAdvanced(contexts.PerkContext())), AdvancedDataBuilder(TOOLTIPS_CONSTANTS.PERK_TTC, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, perk.PerkTTCTooltipData(contexts.PerkContext()), advanced.PerkTooltipAdvanced(contexts.PerkContext())))
