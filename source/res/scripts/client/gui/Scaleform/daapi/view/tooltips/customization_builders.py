# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/customization_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementTooltip
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM, TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_UI, ElementTooltip(contexts.TechCustomizationContext())),)
